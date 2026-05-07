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
    font=gr.themes.GoogleFont('Nunito'),
    font_mono=gr.themes.GoogleFont('JetBrains Mono'),
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
    #chatbot_bubble_bot_background_fill='#FFFFFF',
    #chatbot_bubble_user_background_fill='#E8174A',
    #chatbot_bubble_user_text_color='#FFFFFF',
)

CSS_HEARTS = '''
@import url('https://fonts.googleapis.com/css2?family=Pacifico&family=Nunito:wght@400;700&display=swap');

.gradio-container { background: #FFF8FA !important; }

.message.bot {
    border: 2px solid #FFC2D1 !important;
    border-radius: 4px 18px 18px 18px !important;
}
.message.user {
    background: #E8174A !important;
    border-radius: 18px 4px 18px 18px !important;
}

button.primary {
    background: #E8174A !important;
    border-radius: 22px !important;
    font-family: Nunito, sans-serif !important;
    font-weight: 700 !important;
}
button.primary:hover {
    background: #C0143E !important;
    transform: scale(1.02) !important;
    transition: all .2s !important;
}

.block {
    border-color: #FFC2D1 !important;
    border-radius: 16px !important;
}

input, textarea {
    border-color: #FFC2D1 !important;
    background: #FFF0F4 !important;
}

@keyframes heartbeat {
    0%, 100% { transform: scale(1); }
    50%       { transform: scale(1.15); }
}
.heart-icon {
    animation: heartbeat 1.5s infinite;
    color: #E8174A;
    display: inline-block;
}

@keyframes pulse {
    0%, 100% { transform: scale(1);   opacity: .7; }
    50%       { transform: scale(1.3); opacity: 1;  }
}
.h-anim {
    animation: pulse 2s infinite;
    display: inline-block;
}
.h-anim:nth-child(2) { animation-delay: .3s; }
.h-anim:nth-child(3) { animation-delay: .6s; }
'''