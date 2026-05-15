# app.py — MatchMind UI (Gradio 6)
import gradio as gr
import json
import uuid
import traceback
import os

# ── Safe imports ───────────────────────────────────────────────────────────────
try:
    from rag import MatchRAG, load_profiles
except Exception as e:
    print(f"❌ IMPORT ERROR — rag.py: {e}"); traceback.print_exc(); raise
try:
    from agent import run_agent_stream
except Exception as e:
    print(f"❌ IMPORT ERROR — agent.py: {e}"); traceback.print_exc(); raise
try:
    from onboarding import QUESTIONS, build_bio
except Exception as e:
    print(f"❌ IMPORT ERROR — onboarding.py: {e}"); traceback.print_exc(); raise
try:
    from i18n import LANGUAGE_OPTIONS, label_for_language, language_code, question_for, tr
    from theme import Matchmind_theme, CSS_HEARTS
except Exception as e:
    print(f"❌ IMPORT ERROR — theme/i18n: {e}"); traceback.print_exc(); raise

# ── Init RAG ──────────────────────────────────────────────────────────────────
rag = MatchRAG()
if not rag.load_index():
    path = 'data/profiles.json' if os.path.exists('data/profiles.json') else 'data/sample_profiles.json'
    profiles = load_profiles(path)
    rag.build_index(profiles)

DEFAULT_LANGUAGE   = "en"
DEFAULT_THEME_MODE = "light"


# ── Theme CSS injection ────────────────────────────────────────────────────────
def theme_mode_css(mode: str = DEFAULT_THEME_MODE) -> str:
    if mode != "dark":
        return "<style></style>"
    return """
    <style>
    .gradio-container { background: #170812 !important; color: #FCEAF1 !important; }
    #sidebar { background: #240D19 !important; border-right-color: #6B2440 !important; }
    #chatbot { background: #210B17 !important; border-color: #7A2C49 !important; }
    textarea, input[type="text"] {
        background: #210B17 !important;
        color: #FCEAF1 !important;
        border-color: #7A2C49 !important;
    }
    .message.bot { background: #2B0F1E !important; border-color: #7A2C49 !important; }
    .stat-card, .quick-btn {
        background: #2B0F1E !important;
        border-color: #7A2C49 !important;
        color: #FCEAF1 !important;
    }
    .stat-lab  { color: #FFD6E4 !important; }
    .tool-chip { color: #FFD6E4 !important; background: #3A0F25 !important; }
    .block     { border-color: #7A2C49 !important; }
    </style>
    """


# ── Progress helpers ───────────────────────────────────────────────────────────
def format_progress(state):
    lang = state.get("language", DEFAULT_LANGUAGE) if state else DEFAULT_LANGUAGE
    if state is None:
        return f"0 / {len(QUESTIONS)} {tr(lang, 'progress_suffix')}"
    idx = min(state.get('onboarding_idx', 0), len(QUESTIONS))
    if state.get('onboarding_done', False):
        return tr(lang, "profile_done")
    return f"{idx} / {len(QUESTIONS)} {tr(lang, 'progress_suffix')}"


# ── Profile card HTML ─────────────────────────────────────────────────────────
def profile_summary_html(state: dict) -> str:
    p = state.get("user_profile", {})
    if not p or not state.get("onboarding_done", False):
        return ""
    name = p.get('name', '?')
    bio  = p.get('bio', '')[:80]
    return f"""
    <div style='background:white;border:2px solid #FFC2D1;border-radius:12px;
                padding:10px 12px;font-size:12px;color:#2D0A16;margin-top:6px;margin-bottom:8px;'>
      <b style='color:#E8174A;font-size:13px;'>👤 {name}</b><br>
      <span style='color:#993556;'>✨ {bio}{'...' if len(p.get('bio','')) > 80 else ''}</span>
    </div>"""


# ── Sidebar HTML ───────────────────────────────────────────────────────────────
def sidebar_section_html(lang: str) -> str:
    return f"""
    <div id="sidebar-labels">
      <div class='sidebar-section-title'>{tr(lang, "profile_title").upper()}</div>
      <div style='margin-bottom:4px;'></div>
      <div class='sidebar-section-title' style='margin-top:14px;'>{tr(lang, "stats_title").upper()}</div>
      <div style='display:grid;grid-template-columns:1fr 1fr;gap:6px;margin-bottom:12px;margin-top:6px;'>
        <div class='stat-card'><div class='stat-num'>{len(rag.profiles)}</div><div class='stat-lab'>{tr(lang, "stats_candidates")}</div></div>
        <div class='stat-card'><div class='stat-num'>3</div><div class='stat-lab'>{tr(lang, "stats_top_matches")}</div></div>
      </div>
      <div class='sidebar-section-title'>{tr(lang, "agent_title").upper()}</div>
      <div style='background:white;border:2px solid #FFC2D1;border-radius:12px;
                  padding:10px 12px;font-size:12px;color:#993556;font-weight:600;
                  margin-top:6px;margin-bottom:12px;'>
        <span style='color:#22c55e;margin-right:5px;'>●</span>{tr(lang, "agent_status")}<br>
        <span style='font-size:10px;color:#C0436A;'>GPT-4o + FAISS + 3 tools</span>
      </div>
      <div class='sidebar-section-title'>{tr(lang, "quick_title").upper()}</div>
    </div>
    """


# ── DB helpers ─────────────────────────────────────────────────────────────────
def save_user_to_database(profile: dict):
    path = 'data/profiles.json'
    if os.path.exists(path):
        all_profiles = load_profiles(path)
    else:
        all_profiles = load_profiles('data/sample_profiles.json')
    if not any(p.get('id') == profile.get('id') for p in all_profiles):
        all_profiles.append(profile)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(all_profiles, f, indent=2, ensure_ascii=False)
        print(f"✓ Saved: {profile.get('name')}")
        rag.add_profile(profile)


# ── State helpers ──────────────────────────────────────────────────────────────
def create_state():
    first_question = question_for(DEFAULT_LANGUAGE, QUESTIONS, 0)
    return {
        'user_profile':    {},
        'onboarding_idx':  0,
        'onboarding_done': False,
        'language':        DEFAULT_LANGUAGE,
        'theme_mode':      DEFAULT_THEME_MODE,
        'conversation':    [{"role": "assistant", "content": first_question}],
        'agent_history':   [],
    }


def ensure_state(state: dict, history=None):
    if state is None:
        state = create_state()
    state.setdefault('user_profile', {})
    state.setdefault('onboarding_idx', 0)
    state.setdefault('onboarding_done', False)
    state['language'] = language_code(state.get('language', DEFAULT_LANGUAGE))
    state.setdefault('theme_mode', DEFAULT_THEME_MODE)
    if 'conversation' not in state or not state['conversation']:
        state['conversation'] = [{"role": "assistant",
                                   "content": question_for(state['language'], QUESTIONS, 0)}]
    if 'agent_history' not in state:
        state['agent_history'] = list(state.get('chat_history', []))
    state['chat_history'] = state['agent_history']
    return state


def get_conversation(state: dict):
    state = ensure_state(state)
    return list(state.get('conversation', []))


def get_progress_text(state):
    return format_progress(state)


def add_exchange(history, user_message, assistant_message):
    history = list(history or [])
    if user_message is not None:
        history.append({"role": "user", "content": user_message})
    history.append({"role": "assistant", "content": assistant_message})
    return history


def append_exchange(state: dict, user_message, assistant_message):
    state = ensure_state(state)
    state['conversation'] = add_exchange(state['conversation'], user_message, assistant_message)
    return get_conversation(state)


# ── Session management ─────────────────────────────────────────────────────────
def load_session():
    state = create_state()
    return get_conversation(state), state, get_progress_text(state), ""


def reset_session(state):
    new_state = create_state()
    return get_conversation(new_state), new_state, get_progress_text(new_state), ""


def export_json(state):
    state = ensure_state(state)
    data = {"profile": state["user_profile"], "conversation": state["conversation"]}
    path = os.path.join(os.environ.get("TEMP", os.getcwd()), "matchmind_conversation.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    return path


def export_markdown(state):
    state = ensure_state(state)
    lines = ["# MatchMind Report\n"]
    for msg in state["conversation"]:
        role = "**You**" if msg["role"] == "user" else "**MatchMind 💘**"
        lines.append(f"{role}: {msg['content']}\n")
    path = os.path.join(os.environ.get("TEMP", os.getcwd()), "matchmind_report.md")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    return path


# ── Language change ────────────────────────────────────────────────────────────
def apply_language(language_label: str, state: dict):
    state = ensure_state(state)
    state['language'] = language_code(language_label)
    if not state.get('onboarding_done', False) and state.get('conversation'):
        idx = min(state.get('onboarding_idx', 0), len(QUESTIONS) - 1)
        state['conversation'][-1] = {
            "role": "assistant",
            "content": question_for(state['language'], QUESTIONS, idx),
        }
    lang = state['language']
    return (
        get_conversation(state),
        state,
        get_progress_text(state),
        gr.update(placeholder=tr(lang, "input_placeholder")),
        gr.update(value=tr(lang, "btn_match")),
        gr.update(value=tr(lang, "btn_top1")),
        gr.update(value=tr(lang, "btn_report")),
        gr.update(value=tr(lang, "btn_advice")),
        sidebar_section_html(lang),
    )


# ── Theme change ───────────────────────────────────────────────────────────────
def apply_theme_mode(theme_label: str, state: dict):
    state = ensure_state(state)
    state['theme_mode'] = "dark" if str(theme_label).lower() in {"dark", "sombre", "🌙 dark", "🌙 sombre"} else "light"
    return theme_mode_css(state['theme_mode']), state


# ── Quick actions ──────────────────────────────────────────────────────────────
def quick_action(prompt_key: str, history: list, state: dict):
    if state is None:
        state = create_state()
    state = ensure_state(state)
    return btn_respond(tr(state['language'], prompt_key), state)


# ── respond ────────────────────────────────────────────────────────────────────
def respond(message: str, history: list, state: dict):
    try:
        state = ensure_state(state)
        if not message or not message.strip():
            return "", get_conversation(state), state, get_progress_text(state), profile_summary_html(state)

        if not state['onboarding_done']:
            idx = state['onboarding_idx']
            if idx >= len(QUESTIONS):
                state['onboarding_done'] = True
                state['user_profile'].setdefault('bio', build_bio(state['user_profile']))
                return respond(message, history, state)

            key = QUESTIONS[idx]['key']
            state['user_profile'][key] = message
            state['onboarding_idx'] += 1

            if state['onboarding_idx'] < len(QUESTIONS):
                next_q = question_for(state['language'], QUESTIONS, state['onboarding_idx'])
                conversation = append_exchange(state, message, next_q)
                return "", conversation, state, get_progress_text(state), profile_summary_html(state)

            state['user_profile']['id']  = str(uuid.uuid4())
            state['user_profile']['bio'] = build_bio(state['user_profile'])
            state['onboarding_done']     = True
            save_user_to_database(state['user_profile'])

            done_msg = tr(
                state['language'], "done_msg",
                name=state['user_profile'].get('name', ''),
                count=len(rag.profiles),
            )
            conversation = append_exchange(state, message, done_msg)
            return "", conversation, state, get_progress_text(state), profile_summary_html(state)

        # Matching phase
        response = run_agent_stream(message, state['agent_history'], state['user_profile'], rag, state['language'])
        if not response:
            response = tr(state['language'], "fallback_error")

        state['agent_history'] = add_exchange(state['agent_history'], message, response)
        state['chat_history']  = state['agent_history']
        conversation = append_exchange(state, message, response)
        return "", conversation, state, get_progress_text(state), profile_summary_html(state)

    except Exception as e:
        print(f"❌ ERROR in respond: {e}"); traceback.print_exc()
        state = ensure_state(state)
        conversation = append_exchange(state, message, f"❌ Error: {e}")
        return "", conversation, state, get_progress_text(state), profile_summary_html(state)


def btn_respond(text: str, state: dict):
    try:
        state = ensure_state(state)
        if not state.get('onboarding_done', False):
            append_exchange(state, None, tr(state['language'], "finish_onboarding"))
            return get_conversation(state), state, get_progress_text(state)
        _, conversation, state, prog_text, _ = respond(text, [], state)
        return conversation, state, prog_text
    except Exception as e:
        print(f"❌ ERROR in btn_respond: {e}"); traceback.print_exc()
        state = ensure_state(state)
        conversation = append_exchange(state, None, f"❌ Error: {e}")
        return conversation, state, get_progress_text(state)


# ── UI ─────────────────────────────────────────────────────────────────────────
with gr.Blocks() as demo:

    state = gr.State(create_state())
    theme_injector = gr.HTML(theme_mode_css(DEFAULT_THEME_MODE))

    # ── Top bar ───────────────────────────────────────────────────────────────
    gr.HTML("""
    <div id="topbar" style="background:#E8174A; padding:14px 24px; display:flex;
         align-items:center; gap:14px; margin-bottom:0;">
        <div style="font-size:26px; line-height:1;">❤️</div>
        <div>
            <div style="font-family:'Pacifico',cursive; color:white; font-size:1.5rem; line-height:1.2;">
                MatchMind
            </div>
            <div style="color:#FFB3C6; font-size:0.75rem; font-weight:600;">
                AI Dating Agent
            </div>
        </div>
        <div style="margin-left:auto; display:flex; gap:6px; align-items:center;">
            <span class="tool-chip">🔧 analyze_compat</span>
            <span class="tool-chip">🔍 find_matches</span>
            <span class="tool-chip">📋 gen_report</span>
            <span style="margin-left:10px;">
                <span class="h-anim">❤️</span>
                <span class="h-anim">❤️</span>
                <span class="h-anim">❤️</span>
            </span>
        </div>
    </div>
    """)

    with gr.Row(equal_height=True):

        # ── Sidebar ───────────────────────────────────────────────────────────
        with gr.Column(scale=1, min_width=220, elem_id="sidebar"):

            with gr.Row():
                language_selector = gr.Dropdown(
                    choices=LANGUAGE_OPTIONS,
                    value=label_for_language(DEFAULT_LANGUAGE),
                    label=tr(DEFAULT_LANGUAGE, "language_label"),
                    interactive=True,
                    elem_classes=["compact-dropdown"],
                    scale=3,
                )
                theme_selector = gr.Dropdown(
                    choices=["☀️ Light", "🌙 Dark"],
                    value="☀️ Light",
                    label=tr(DEFAULT_LANGUAGE, "theme_label"),
                    interactive=True,
                    elem_classes=["compact-dropdown"],
                    scale=2,
                )

            sidebar_labels = gr.HTML(sidebar_section_html(DEFAULT_LANGUAGE))
            profile_card   = gr.HTML("", elem_id="profile-card")
            progress_text  = gr.Markdown(format_progress(create_state()), elem_classes=["progress-md"])

            btn_match  = gr.Button(tr(DEFAULT_LANGUAGE, "btn_match"),  elem_classes=["quick-btn"])
            btn_top1   = gr.Button(tr(DEFAULT_LANGUAGE, "btn_top1"),   elem_classes=["quick-btn"])
            btn_report = gr.Button(tr(DEFAULT_LANGUAGE, "btn_report"), elem_classes=["quick-btn"])
            btn_advice = gr.Button(tr(DEFAULT_LANGUAGE, "btn_advice"), elem_classes=["quick-btn"])

            gr.HTML("<div style='border-top:1px solid #FFC2D1;margin:10px 0;'></div>")
            gr.HTML("<div class='sidebar-section-title'>SESSION</div>")

            btn_new_chat  = gr.Button("🔄 New Chat",      elem_classes=["quick-btn"])
            btn_save_json = gr.Button("💾 Save as JSON",  elem_classes=["quick-btn"])
            btn_export_md = gr.Button("📄 Export Report", elem_classes=["quick-btn"])

            file_output = gr.File(label="Download", visible=False)

        # ── Chat ──────────────────────────────────────────────────────────────
        with gr.Column(scale=4):

            gr.HTML("""
            <div style='background:white;border-bottom:2px solid #FFE0EA;
                        padding:12px 18px;display:flex;align-items:center;gap:10px;
                        border-radius:16px 16px 0 0;'>
                <div style='width:40px;height:40px;background:#E8174A;border-radius:50%;
                            display:flex;align-items:center;justify-content:center;
                            font-size:20px;'>❤️</div>
                <div>
                    <div style='font-weight:800;font-size:15px;color:#2D0A16;'>Agent MatchMind</div>
                    <div style='font-size:11px;color:#C0436A;'>
                        <span style='color:#22c55e;'>●</span> Online · multi-step reasoning
                    </div>
                </div>
            </div>
            """)

            chatbot = gr.Chatbot(
                label="",
                height=460,
                elem_id="chatbot",
                show_label=False,
            )

            with gr.Row():
                msg = gr.Textbox(
                    placeholder=tr(DEFAULT_LANGUAGE, "input_placeholder"),
                    show_label=False,
                    container=False,
                    scale=5,
                )
                send_btn = gr.Button("➤", variant="primary", scale=1, min_width=60)

    # ── Events ────────────────────────────────────────────────────────────────
    respond_outputs = [msg, chatbot, state, progress_text, profile_card]

    msg.submit(respond,     inputs=[msg, chatbot, state], outputs=respond_outputs)
    send_btn.click(respond, inputs=[msg, chatbot, state], outputs=respond_outputs)

    language_selector.change(
        apply_language,
        inputs=[language_selector, state],
        outputs=[chatbot, state, progress_text, msg,
                 btn_match, btn_top1, btn_report, btn_advice, sidebar_labels],
    )

    theme_selector.change(
        apply_theme_mode,
        inputs=[theme_selector, state],
        outputs=[theme_injector, state],
    )

    btn_outputs = [chatbot, state, progress_text]

    btn_match.click( lambda h, s: quick_action("quick_match_prompt",  h, s), inputs=[chatbot, state], outputs=btn_outputs)
    btn_top1.click(  lambda h, s: quick_action("quick_top1_prompt",   h, s), inputs=[chatbot, state], outputs=btn_outputs)
    btn_report.click(lambda h, s: quick_action("quick_report_prompt", h, s), inputs=[chatbot, state], outputs=btn_outputs)
    btn_advice.click(lambda h, s: quick_action("quick_advice_prompt", h, s), inputs=[chatbot, state], outputs=btn_outputs)

    btn_new_chat.click( reset_session,   inputs=[state], outputs=[chatbot, state, progress_text, profile_card])
    btn_save_json.click(export_json,     inputs=[state], outputs=[file_output]).then(lambda: gr.update(visible=True), outputs=[file_output])
    btn_export_md.click(export_markdown, inputs=[state], outputs=[file_output]).then(lambda: gr.update(visible=True), outputs=[file_output])

    demo.load(fn=load_session, outputs=[chatbot, state, progress_text, profile_card])

#demo.launch(share=True, theme=Matchmind_theme, css=CSS_HEARTS)
app = demo

if __name__ == "__main__":
    demo.launch(
        share=True,
        theme=Matchmind_theme,
        css=CSS_HEARTS
    )