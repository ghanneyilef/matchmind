import os
import json
from openai import OpenAI
from dotenv import load_dotenv
from profiles import compute_compatibility
from rag import MatchRAG

load_dotenv()
client = OpenAI(
    api_key=os.getenv('OPENAI_API_KEY'),
    base_url="https://openrouter.ai/api/v1",
)

# ── Tool definitions — OpenAI format ──────────────────────────────
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "analyze_compatibility",
            "description": "Compute an 8-dimensional weighted compatibility score between the current user and a candidate profile.",
            "parameters": {
                "type": "object",
                "properties": {
                    "candidate_id": {
                        "type": "string",
                        "description": "The EXACT id field (UUID string) of the candidate profile to analyze. Never use a placeholder."
                    }
                },
                "required": ["candidate_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "find_best_matches",
            "description": "Search the FAISS index and return the top 3 matching candidate profiles for the current user. Call this with no arguments.",
            "parameters": {
                "type": "object",
                "properties": {
                    "top_k": {
                        "type": "integer",
                        "description": "Number of matches to return. Always use 3.",
                        "default": 3
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "generate_match_report",
            "description": "Generate a full narrative compatibility report with date tips and green/red flag analysis.",
            "parameters": {
                "type": "object",
                "properties": {
                    "candidate_id": {
                        "type": "string",
                        "description": "The EXACT id field (UUID string) of the candidate to generate the report for. Never use a placeholder."
                    }
                },
                "required": ["candidate_id"]
            }
        }
    }
]


# ── System prompt ──────────────────────────────────────────────────
def build_system_prompt(user_profile: dict, language: str = "en") -> str:
    language_name = "French" if language == "fr" else "English"
    return f"""You are MatchMind 💘, a warm and witty AI dating agent for Gen Z.
You have already completed the onboarding of the current user.

CURRENT USER PROFILE:
{json.dumps(user_profile, indent=2, ensure_ascii=False)}

YOUR BEHAVIOR:
- You are fun, empathetic, and speak like a smart friend — not a robot.
- When the user asks for matches, ALWAYS call find_best_matches first.
- Then call analyze_compatibility for EACH candidate using their EXACT id from the results.
- For the best match, call generate_match_report using the EXACT id from find_best_matches results.
- CRITICAL: NEVER use placeholder strings like "best_match_id", "candidate_id", or "example_id".
  Always use the real UUID string returned by find_best_matches (e.g. "a1b2c3d4-...").
- Always explain your reasoning after tool calls.
- Never expose raw JSON to the user — translate everything into natural language.
- When displaying compatibility scores, always show them as a percentage (e.g. "72% compatible").
- Use emojis sparingly but warmly 💘
- If the user asks for first date advice, a full report, or info about their #1 match,
  and you already called find_best_matches earlier in this conversation, DO NOT call
  find_best_matches again. Reuse the best candidate's EXACT UUID id from the history
  and call generate_match_report directly with that id.

LANGUAGE: Respond in {language_name}. Follow the selected app language, not automatic language detection.
"""


# ── Tool execution ─────────────────────────────────────────────────
def process_tool_call(
    name: str,
    arguments: dict,
    rag: MatchRAG,
    user_profile: dict,
    session_state: dict,          # ← per-session, replaces the old global
) -> str:
    arguments = arguments or {}

    if name == 'find_best_matches':
        top_k   = int(arguments.get('top_k', 3))
        matches = rag.search(
            user_profile.get('bio', ''),
            top_k=top_k,
            user_profile=user_profile,
        )
        session_state['last_matches'] = matches   # store in session, NOT a global
        return json.dumps({'matches': matches, 'count': len(matches)}, ensure_ascii=False)

    elif name in ('analyze_compatibility', 'generate_match_report'):
        candidate_id = arguments.get('candidate_id', '')

        PLACEHOLDERS = {
            'best_match_id', 'candidate_id', 'example_id', 'match_id',
            'top_match_id', 'first_match_id', 'id', 'uuid', 'profile_id',
        }
        if not candidate_id or candidate_id.lower().replace('-', '_') in PLACEHOLDERS:
            last = session_state.get('last_matches', [])
            if last:
                candidate_id = last[0].get('id', '')
                print(f"⚠️  Resolved placeholder → {candidate_id}")
            else:
                return json.dumps({'error': 'No matches found yet. Call find_best_matches first.'})

        # Exact UUID match first
        candidate = next((p for p in rag.profiles if p.get('id') == candidate_id), None)

        # Fallback: name contains match
        if not candidate:
            candidate = next(
                (p for p in rag.profiles if candidate_id.lower() in p.get('name', '').lower()),
                None,
            )

        if not candidate:
            return json.dumps({'error': f'Profile {candidate_id} not found'})

        if name == 'analyze_compatibility':
            result = compute_compatibility(user_profile, candidate)
            result['candidate_name'] = candidate.get('name', 'Unknown')
            if 'score' in result:
                result['score_pct'] = f"{result['score']}%"
            return json.dumps(result, ensure_ascii=False)

        else:  # generate_match_report
            score_data = compute_compatibility(user_profile, candidate)
            if 'score' in score_data:
                score_data['score_pct'] = f"{score_data['score']}%"
            result = {
                'candidate':  candidate,
                'score_data': score_data,
                'report_hint': (
                    f"Generate a warm narrative report about why {candidate['name']} "
                    f"could be a great match. Mention shared values, potential friction "
                    f"points, and suggest a creative first date idea based on their "
                    f"hobbies: {candidate.get('hobbies', [])}."
                ),
            }
            return json.dumps(result, ensure_ascii=False)

    return json.dumps({'error': 'Unknown tool'})


# ── OpenAI API call ────────────────────────────────────────────────
def _call_openai(messages: list, use_tools: bool = True) -> object:
    kwargs = dict(
        model='gpt-4o-mini',
        max_tokens=2000,
        messages=messages,
    )
    if use_tools:
        kwargs['tools']       = TOOLS
        kwargs['tool_choice'] = 'auto'
    return client.chat.completions.create(**kwargs)


def _is_rate_limit(exc: Exception) -> bool:
    msg = str(exc)
    return '429' in msg or 'rate_limit' in msg.lower() or 'rate limit' in msg.lower()


# ── Main agent loop ────────────────────────────────────────────────
def run_agent_stream(
    user_message: str,
    history: list,
    user_profile: dict,
    rag: MatchRAG,
    language: str = "en",
    agent_session: dict = None,   # ← caller passes this per-session dict
) -> str:
    """
    Run the OpenAI agent loop with tool use.
    `agent_session` is a plain dict stored in Gradio state — no globals.
    """
    if agent_session is None:
        agent_session = {}

    # Build message list
    messages: list[dict] = [
        {"role": "system", "content": build_system_prompt(user_profile, language)}
    ]
    for msg in history:
        if msg.get('role') in ('user', 'assistant'):
            messages.append({'role': msg['role'], 'content': msg['content']})
    messages.append({'role': 'user', 'content': user_message})

    for iteration in range(8):
        try:
            response = _call_openai(messages, use_tools=True)
        except Exception as exc:
            if _is_rate_limit(exc):
                print(f"⏳ OpenAI rate limit: {exc}")
                return "⏳ I've hit my API rate limit — please wait a moment and try again 💘"
            print(f"❌ OpenAI error: {exc}")
            return "Sorry, I could not reach the AI right now 💘 Try again in a moment!"

        choice  = response.choices[0]
        message = choice.message

        # ── Tool calls ─────────────────────────────────────────────
        if choice.finish_reason == 'tool_calls' and message.tool_calls:
            # Append assistant message with tool_calls (OpenAI requires this)
            messages.append({
                "role":       "assistant",
                "content":    message.content or "",
                "tool_calls": [
                    {
                        "id":       tc.id,
                        "type":     "function",
                        "function": {
                            "name":      tc.function.name,
                            "arguments": tc.function.arguments,
                        },
                    }
                    for tc in message.tool_calls
                ],
            })

            for tool_call in message.tool_calls:
                name     = tool_call.function.name
                raw_args = tool_call.function.arguments or '{}'
                try:
                    arguments = json.loads(raw_args)
                except json.JSONDecodeError:
                    arguments = {}

                result = process_tool_call(name, arguments, rag, user_profile, agent_session)
                print(f"🔧 Tool: {name} → {result[:120]}...")

                messages.append({
                    'role':         'tool',
                    'tool_call_id': tool_call.id,
                    'name':         name,
                    'content':      result,
                })
            continue

        # ── Final text response ────────────────────────────────────
        return message.content or ""

    return "Sorry, I could not process your request right now 💘 Try again!"