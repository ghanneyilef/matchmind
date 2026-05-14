import os
import json
from groq import Groq
from dotenv import load_dotenv
from profiles import compute_compatibility
from rag import MatchRAG

load_dotenv()
client = Groq(api_key=os.getenv('GROQ_API_KEY'))

# ── 3 Tools definitions — OpenAI format ───────────────────────────
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
                        "description": "The id field of the candidate profile to analyze"
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
            "description": "Search the FAISS index and return the top matching candidate profiles for the current user.",
            "parameters": {
                "type": "object",
                "properties": {
                    "top_k": {
                        "type": "integer",
                        "description": "Number of matches to return. Default is 3."
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
                        "description": "The id of the candidate to generate the report for"
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
- Then call analyze_compatibility for each result.
- For the best match, call generate_match_report.
- Always explain your reasoning after tool calls.
- Never expose raw JSON to the user — translate everything into natural language.
- Use emojis sparingly but warmly 💘

LANGUAGE: Respond in {language_name}. Follow the selected app language, not automatic language detection.
"""


# ── Tool execution ─────────────────────────────────────────────────
def process_tool_call(name: str, arguments: dict, rag: MatchRAG, user_profile: dict) -> str:
    if name == 'find_best_matches':
        top_k   = arguments.get('top_k', 3)
        matches = rag.search(user_profile.get('bio', ''), top_k=top_k, user_profile=user_profile)
        return json.dumps({'matches': matches, 'count': len(matches)}, ensure_ascii=False)

    elif name == 'analyze_compatibility':
        candidate_id = arguments.get('candidate_id')
        candidate    = next((p for p in rag.profiles if p['id'] == candidate_id), None)
        if candidate:
            result = compute_compatibility(user_profile, candidate)
            result['candidate_name'] = candidate.get('name', 'Unknown')
        else:
            result = {'error': f'Profile {candidate_id} not found'}
        return json.dumps(result, ensure_ascii=False)

    elif name == 'generate_match_report':
        candidate_id = arguments.get('candidate_id')
        candidate    = next((p for p in rag.profiles if p['id'] == candidate_id), None)
        if candidate:
            score_data = compute_compatibility(user_profile, candidate)
            result = {
                'candidate':  candidate,
                'score_data': score_data,
                'report_hint': (
                    f"Generate a warm narrative report about why {candidate['name']} "
                    f"could be a great match. Mention shared values, potential friction "
                    f"points, and suggest a creative first date idea based on their "
                    f"hobbies: {candidate.get('hobbies', [])}."
                )
            }
        else:
            result = {'error': f'Profile {candidate_id} not found'}
        return json.dumps(result, ensure_ascii=False)

    return json.dumps({'error': 'Unknown tool'})


# ── Main agent loop ────────────────────────────────────────────────
def run_agent_stream(user_message: str, history: list, user_profile: dict, rag: MatchRAG, language: str = "en") -> str:
    """Run the OpenAI agent loop with tool use. Returns the full response string."""

    # System message first
    messages = [{"role": "system", "content": build_system_prompt(user_profile, language)}]

    # Append conversation history (already role/content dicts)
    for msg in history:
        if msg.get('role') in ('user', 'assistant'):
            messages.append({'role': msg['role'], 'content': msg['content']})

    messages.append({'role': 'user', 'content': user_message})

    for iteration in range(5):
        response = client.chat.completions.create(
            model='llama-3.3-70b-versatile',  # Groq free tier
            max_tokens=2000,
            tools=TOOLS,
            tool_choice='auto',
            messages=messages,
        )

        choice  = response.choices[0]
        message = choice.message

        # ── Tool calls ─────────────────────────────────────────────
        if choice.finish_reason == 'tool_calls' and message.tool_calls:
            messages.append(message)  # assistant message with tool_calls

            for tool_call in message.tool_calls:
                name      = tool_call.function.name
                arguments = json.loads(tool_call.function.arguments)
                result    = process_tool_call(name, arguments, rag, user_profile)
                print(f"🔧 Tool: {name} → {result[:120]}...")

                messages.append({
                    'role':         'tool',
                    'tool_call_id': tool_call.id,
                    'content':      result,
                })
            continue

        # ── Final text response ────────────────────────────────────
        return message.content or ""

    return "Sorry, I could not process your request right now 💘 Try again!"