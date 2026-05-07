# agent.py
import os
import json
from openai import OpenAI
from dotenv import load_dotenv
from profiles import compute_compatibility
from rag import MatchRAG

load_dotenv()
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# ── 3 Tools definitions ────────────────────────────────────────────
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
def build_system_prompt(user_profile: dict) -> str:
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

LANGUAGE: Respond in the same language the user writes in.
"""


# ── Tool execution ─────────────────────────────────────────────────
def process_tool_call(name: str, arguments: dict, rag: MatchRAG, user_profile: dict) -> str:
    if name == 'find_best_matches':
        top_k   = arguments.get('top_k', 3)
        matches = rag.search(user_profile.get('bio', ''), top_k=top_k)
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
def run_agent_stream(user_message: str, history: list, user_profile: dict, rag: MatchRAG):
    """Run the agent with streaming. Yields tokens for Gradio."""

    messages = [{'role': 'system', 'content': build_system_prompt(user_profile)}]
    messages += history
    messages.append({'role': 'user', 'content': user_message})

    for iteration in range(5):
        response = client.chat.completions.create(
            model='gpt-4o',
            messages=messages,
            tools=TOOLS,
            tool_choice='auto',
            max_tokens=2000,
        )

        msg = response.choices[0].message

        # ── Tool calls ─────────────────────────────────────────────
        if msg.tool_calls:
            messages.append(msg)
            for tool_call in msg.tool_calls:
                name      = tool_call.function.name
                arguments = json.loads(tool_call.function.arguments)
                result    = process_tool_call(name, arguments, rag, user_profile)
                messages.append({
                    'role':         'tool',
                    'tool_call_id': tool_call.id,
                    'content':      result
                })
            continue

        # ── Final response — stream it ─────────────────────────────
        messages.append({'role': 'assistant', 'content': msg.content})

        stream = client.chat.completions.create(
            model='gpt-4o',
            messages=messages,
            max_tokens=2000,
            stream=True,
        )
        for chunk in stream:
            token = chunk.choices[0].delta.content
            if token:
                yield token
        return

    yield "Sorry, I could not process your request right now 💘 Try again!"