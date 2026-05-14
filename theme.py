# theme.py
import gradio as gr

Matchmind_theme = gr.themes.Base(
    primary_hue=gr.themes.Color(
        c50='#FFF0F4',  c100='#FFD6E4',  c200='#FFB3C6',
        c300='#FF8FAD', c400='#E8174A',  c500='#C0143E',
        c600='#991033', c700='#720C27',  c800='#4B081A',
        c900='#24040D', c950='#0D0106',
    ),
    secondary_hue=gr.themes.Color(
        c50='#FBEAF0',  c100='#F4C0D1',  c200='#ED93B1',
        c300='#E06490', c400='#D4537E',  c500='#B03D65',
        c600='#8C2B4D', c700='#681E38',  c800='#441224',
        c900='#200810', c950='#0D030A',
    ),
    font=[gr.themes.GoogleFont('Nunito'), 'sans-serif'],
    font_mono=[gr.themes.GoogleFont('JetBrains Mono'), 'monospace'],
).set(
    body_background_fill='#FFF8FA',
    body_text_color='#2D0A16',
    block_background_fill='#FFFFFF',
    block_border_color='#FFC2D1',
    block_border_width='2px',
    block_radius='16px',
    button_primary_background_fill='#E8174A',
    button_primary_text_color='#FFFFFF',
    input_background_fill='#FFF0F4',
    input_border_color='#FFC2D1',
)

CSS_HEARTS = '''
@import url('https://fonts.googleapis.com/css2?family=Pacifico&family=Nunito:wght@400;600;700;800&display=swap');

/* ── Layout ── */
.gradio-container {
    background: #FFF5F7 !important;
    font-family: Nunito, sans-serif !important;
    max-width: 100% !important;
    padding: 0 !important;
}

/* ── Top bar ── */
#topbar {
    background: #E8174A;
    padding: 14px 24px;
    display: flex;
    align-items: center;
    gap: 12px;
    border-radius: 0 !important;
}
#topbar h1 {
    font-family: Pacifico, cursive !important;
    color: white !important;
    font-size: 1.6rem !important;
    margin: 0 !important;
}
#topbar p {
    color: #FFB3C6 !important;
    font-size: 0.75rem !important;
    font-weight: 600 !important;
    margin: 0 !important;
}

/* ── Sidebar ── */
#sidebar {
    background: #FFF0F4 !important;
    border-right: 2px solid #FFC2D1 !important;
    border-radius: 0 !important;
    padding: 16px 12px !important;
    min-width: 200px !important;
}

/* Sidebar section title — used by sidebar_section_html() */
.sidebar-section-title {
    font-size: 11px !important;
    font-weight: 800 !important;
    color: #E8174A !important;
    text-transform: uppercase !important;
    letter-spacing: .08em !important;
    margin-bottom: 4px !important;
}

/* ── Compact dropdowns (language + theme) ── */
.compact-dropdown select,
.compact-dropdown .wrap {
    padding: 4px 8px !important;
    font-size: 12px !important;
    min-height: unset !important;
    height: 32px !important;
    border-radius: 10px !important;
    border-color: #FFC2D1 !important;
    background: #FFF8FA !important;
    color: #2D0A16 !important;
    font-family: Nunito, sans-serif !important;
    font-weight: 700 !important;
}
.compact-dropdown label {
    font-size: 10px !important;
    font-weight: 800 !important;
    color: #E8174A !important;
    text-transform: uppercase !important;
    letter-spacing: .06em !important;
    margin-bottom: 2px !important;
}

/* ── Progress markdown ── */
.progress-md p {
    font-size: 12px !important;
    font-weight: 700 !important;
    color: #993556 !important;
    margin: 0 0 4px !important;
}

/* ── Chatbot bubbles ── */
/* IMPORTANT: do NOT set `color` here — it would override emoji rendering in dark mode */
.message.bot {
    background: #FFFFFF !important;
    border: 2px solid #FFC2D1 !important;
    border-radius: 4px 18px 18px 18px !important;
    font-weight: 600 !important;
}
.message.user {
    background: #E8174A !important;
    border-radius: 18px 4px 18px 18px !important;
    color: white !important;
    font-weight: 600 !important;
}

/* ── Input box ── */
.gr-text-input, textarea, input[type="text"] {
    border: 2px solid #FFC2D1 !important;
    border-radius: 22px !important;
    background: #FFF8FA !important;
    font-family: Nunito, sans-serif !important;
    font-weight: 600 !important;
    color: #2D0A16 !important;
    padding: 10px 16px !important;
}

/* ── Quick action buttons ── */
.quick-btn {
    width: 100% !important;
    background: white !important;
    border: 2px solid #FFC2D1 !important;
    border-radius: 12px !important;
    padding: 8px 10px !important;
    font-size: 12px !important;
    color: #C0436A !important;
    font-family: Nunito, sans-serif !important;
    font-weight: 700 !important;
    text-align: left !important;
    cursor: pointer !important;
    margin-bottom: 5px !important;
    transition: background .15s !important;
}
.quick-btn:hover {
    background: #FFF0F4 !important;
}

/* ── Primary buttons ── */
button.primary, .gr-button-primary {
    background: #E8174A !important;
    border-radius: 22px !important;
    font-family: Nunito, sans-serif !important;
    font-weight: 700 !important;
    border: none !important;
    transition: all .2s !important;
}
button.primary:hover {
    background: #C0143E !important;
    transform: scale(1.02) !important;
}

/* ── Tool chips ── */
.tool-chip {
    background: #FFF0F4;
    border: 1.5px solid #FFC2D1;
    border-radius: 20px;
    padding: 3px 10px;
    font-size: 10px;
    color: #993556;
    font-weight: 700;
    display: inline-block;
    margin: 2px;
}

/* ── Stat cards ── */
.stat-card {
    background: white;
    border: 2px solid #FFC2D1;
    border-radius: 12px;
    padding: 10px;
    text-align: center;
}
.stat-num {
    font-size: 22px;
    font-weight: 800;
    color: #E8174A;
}
.stat-lab {
    font-size: 10px;
    color: #C0436A;
    font-weight: 700;
}

/* ── Hearts animation ── */
@keyframes pulse {
    0%, 100% { transform: scale(1);   opacity: .7; }
    50%       { transform: scale(1.3); opacity: 1;  }
}
.h-anim {
    animation: pulse 2s infinite;
    display: inline-block;
    color: #FFB3C6;
}
.h-anim:nth-child(2) { animation-delay: .3s; }
.h-anim:nth-child(3) { animation-delay: .6s; }

/* ── Block styling ── */
.block {
    border-color: #FFC2D1 !important;
    border-radius: 16px !important;
}

/* ── Chatbot container ── */
#chatbot {
    border: 2px solid #FFC2D1 !important;
    border-radius: 16px !important;
    background: #FFF8FA !important;
}
'''