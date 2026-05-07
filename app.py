# app.py
import gradio as gr
import json
import os
from rag import MatchRAG
from agent import run_agent_stream
from onboarding import QUESTIONS, build_bio
from theme import Matchmind_theme, CSS_HEARTS

# ── Init RAG ──────────────────────────────────────────────────────
rag = MatchRAG()

if not rag.load_index():
    if os.path.exists('data/profiles.json'):
        with open('data/profiles.json') as f:
            profiles = json.load(f)
        rag.build_index(profiles)
    else:
        # fallback to sample profiles during development
        with open('data/sample_profiles.json') as f:
            profile = json.load(f)
        rag.build_index([profile])

# ── State (one per session) ────────────────────────────────────────
def create_state():
    return {
        'user_profile':   {},
        'onboarding_idx': 0,
        'onboarding_done': False
    }

# ── Chat function ──────────────────────────────────────────────────
def chat(message, history, state):
    if state is None:
        state = create_state()

    # ── Onboarding phase ───────────────────────────────────────────
    if not state['onboarding_done']:
        idx = state['onboarding_idx']
        key = QUESTIONS[idx]['key']
        state['user_profile'][key] = message
        state['onboarding_idx'] += 1

        # More questions remaining
        if state['onboarding_idx'] < len(QUESTIONS):
            next_q = QUESTIONS[state['onboarding_idx']]['q']
            yield next_q, state
            return

        # Onboarding complete — build bio + embed
        state['user_profile']['bio'] = build_bio(state['user_profile'])
        state['onboarding_done'] = True

        yield "✅ Perfect! Your profile is ready 💘 Looking for your best matches... just ask me!", state
        return

    # ── Matching phase — stream agent ─────────────────────────────
    agent_history = [
        {'role': h['role'], 'content': h['content']}
        for h in history
    ]

    response = ""
    for token in run_agent_stream(message, agent_history, state['user_profile'], rag):
        response += token
        yield response, state


# ── Gradio UI ──────────────────────────────────────────────────────
with gr.Blocks(theme=Matchmind_theme, css=CSS_HEARTS) as demo:

    gr.HTML("""
        <div style="text-align:center; padding: 20px 0 10px;">
            <h1 style="font-family:'Pacifico',cursive; color:#E8174A; font-size:2.5rem;">
                💘 MatchMind
            </h1>
            <p style="color:#991033; font-size:1rem;">
                Your AI Dating Agent — find your perfect match
            </p>
        </div>
    """)

    state   = gr.State(create_state())
    chatbot = gr.Chatbot(
        label="MatchMind",
        height=480,
    )
    msg = gr.Textbox(
        placeholder="Type your answer here...",
        show_label=False,
        container=False,
    )

    # Quick action buttons (after onboarding)
    with gr.Row():
        btn_match  = gr.Button("💘 Find my matches",      size="sm")
        btn_top1   = gr.Button("🏆 Who is my #1 match?",  size="sm")
        btn_report = gr.Button("📋 Generate full report", size="sm")

    # ── Event handlers ─────────────────────────────────────────────
    def respond(message, chat_history, state):
        chat_history.append({'role': 'user', 'content': message})
        response = ""
        final_state = state
        for token, new_state in chat(message, chat_history, state):
            response = token
            final_state = new_state
        return "", chat_history + [{'role': 'assistant', 'content': response}], final_state

    def quick_send(btn_text, chat_history, state):
        return respond(btn_text, chat_history, state)

    msg.submit(respond, [msg, chatbot, state], [msg, chatbot, state])

    btn_match.click( lambda h, s: respond("Find my best matches", h, s),
                     [chatbot, state], [msg, chatbot, state])
    btn_top1.click(  lambda h, s: respond("Who is my number 1 match?", h, s),
                     [chatbot, state], [msg, chatbot, state])
    btn_report.click(lambda h, s: respond("Generate a full report for my best match", h, s),
                     [chatbot, state], [msg, chatbot, state])

    # ── First message on load ──────────────────────────────────────
    demo.load(
        fn=lambda: (
            [{'role': 'assistant', 'content': QUESTIONS[0]['q']}],
            create_state()
        ),
        outputs=[chatbot, state]
    )

demo.launch(share=True)