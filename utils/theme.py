"""
CYBERDECK theme — a cyberpunk terminal skin for the Streamlit UI.
Pure CSS/HTML injected via st.markdown; no JS frameworks, no external
services. Respects prefers-reduced-motion.
"""

CYBERPUNK_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@500;700;900&family=JetBrains+Mono:wght@400;500;700&display=swap');

:root {
    --void: #05070d;
    --panel: #0d1420;
    --panel-2: #0a0f18;
    --grid-line: rgba(0, 240, 255, 0.10);
    --signal-cyan: #00f0ff;
    --pulse-magenta: #ff2e88;
    --volt-lime: #b6ff3c;
    --amber: #ffb000;
    --ash: #9fb3c8;
    --ink: #e8fbff;
}

/* ---- base canvas -------------------------------------------------- */
.stApp {
    background:
        linear-gradient(var(--grid-line) 1px, transparent 1px) 0 0 / 34px 34px,
        linear-gradient(90deg, var(--grid-line) 1px, transparent 1px) 0 0 / 34px 34px,
        radial-gradient(ellipse at 20% -10%, rgba(0,240,255,0.08), transparent 55%),
        radial-gradient(ellipse at 90% 110%, rgba(255,46,136,0.07), transparent 55%),
        var(--void);
    color: var(--ink);
    font-family: 'JetBrains Mono', monospace;
}

/* scanline overlay, subtle + slow */
.stApp::before {
    content: "";
    position: fixed;
    inset: 0;
    pointer-events: none;
    z-index: 9999;
    background: repeating-linear-gradient(
        to bottom,
        rgba(255,255,255,0.018) 0px,
        rgba(255,255,255,0.018) 1px,
        transparent 2px,
        transparent 4px
    );
    mix-blend-mode: overlay;
}

@media (prefers-reduced-motion: no-preference) {
    .cyber-title { animation: flicker 6s infinite; }
    .cyber-cursor { animation: blink 1s steps(1) infinite; }
    .cyber-glow-btn button { transition: box-shadow 0.25s ease, transform 0.15s ease; }
}
@media (prefers-reduced-motion: reduce) {
    .cyber-cursor { opacity: 1; }
}

@keyframes flicker {
    0%, 96%, 100% { opacity: 1; }
    97% { opacity: 0.82; }
    98% { opacity: 1; }
    99% { opacity: 0.9; }
}
@keyframes blink {
    0%, 49% { opacity: 1; }
    50%, 100% { opacity: 0; }
}

/* ---- header block --------------------------------------------------- */
.cyber-header {
    border: 1px solid rgba(0,240,255,0.35);
    background: linear-gradient(180deg, rgba(0,240,255,0.06), rgba(13,20,32,0.4));
    padding: 22px 26px;
    margin-bottom: 18px;
    position: relative;
}
.cyber-header::before, .cyber-header::after,
.hud-panel::before, .hud-panel::after {
    content: "";
    position: absolute;
    width: 14px; height: 14px;
    border-color: var(--signal-cyan);
    border-style: solid;
    opacity: 0.9;
}
.cyber-header::before { top: -1px; left: -1px; border-width: 2px 0 0 2px; }
.cyber-header::after  { bottom: -1px; right: -1px; border-width: 0 2px 2px 0; }

.cyber-eyebrow {
    font-family: 'JetBrains Mono', monospace;
    letter-spacing: 3px;
    font-size: 12px;
    color: var(--volt-lime);
    text-transform: uppercase;
    margin-bottom: 6px;
}
.cyber-title {
    font-family: 'Orbitron', sans-serif;
    font-weight: 900;
    font-size: 34px;
    letter-spacing: 1px;
    color: var(--ink);
    text-shadow: 0 0 8px rgba(0,240,255,0.55), 0 0 24px rgba(0,240,255,0.25);
    margin: 0;
}
.cyber-cursor { color: var(--pulse-magenta); }
.cyber-subtitle {
    font-size: 13px;
    color: var(--ash);
    margin-top: 8px;
    letter-spacing: 0.5px;
}
.cyber-subtitle b { color: var(--signal-cyan); }

/* ---- section labels: [ 01 // NAME.LOG ] ----------------------------- */
.cyber-section {
    font-family: 'Orbitron', sans-serif;
    font-size: 15px;
    font-weight: 700;
    letter-spacing: 2px;
    color: var(--signal-cyan);
    border-bottom: 1px solid rgba(0,240,255,0.25);
    padding-bottom: 8px;
    margin: 22px 0 12px 0;
    text-shadow: 0 0 6px rgba(0,240,255,0.35);
}
.cyber-section .idx { color: var(--pulse-magenta); }

.hud-panel {
    position: relative;
    border: 1px solid rgba(0,240,255,0.22);
    background: rgba(13,20,32,0.55);
    padding: 16px 18px;
    margin-bottom: 14px;
}
.hud-panel .cyber-label {
    font-family: 'Orbitron', sans-serif;
    font-size: 12px;
    letter-spacing: 2px;
    color: var(--pulse-magenta);
    text-transform: uppercase;
    margin-bottom: 10px;
}

/* priority / sentiment chips */
.chip {
    display: inline-block;
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px;
    letter-spacing: 1px;
    padding: 2px 8px;
    border-radius: 2px;
    margin-left: 8px;
    text-transform: uppercase;
    border: 1px solid currentColor;
}
.chip-urgent { color: var(--pulse-magenta); background: rgba(255,46,136,0.08); }
.chip-high { color: var(--amber); background: rgba(255,176,0,0.08); }
.chip-normal { color: var(--ash); background: rgba(159,179,200,0.08); }
.chip-positive { color: var(--volt-lime); background: rgba(182,255,60,0.08); }
.chip-neutral { color: var(--ash); background: rgba(159,179,200,0.08); }
.chip-negative { color: var(--pulse-magenta); background: rgba(255,46,136,0.08); }

/* ---- widget restyling ------------------------------------------------ */
[data-testid="stSidebar"] {
    background: var(--panel-2);
    border-right: 1px solid rgba(0,240,255,0.15);
}
[data-testid="stSidebar"] * { font-family: 'JetBrains Mono', monospace; }

.stTabs [data-baseweb="tab-list"] { gap: 4px; }
.stTabs [data-baseweb="tab"] {
    background: var(--panel);
    border: 1px solid rgba(0,240,255,0.18);
    color: var(--ash);
    font-family: 'JetBrains Mono', monospace;
    letter-spacing: 0.5px;
}
.stTabs [aria-selected="true"] {
    color: var(--signal-cyan) !important;
    border-color: var(--signal-cyan) !important;
    box-shadow: 0 0 10px rgba(0,240,255,0.25);
}

.stButton button, .stDownloadButton button {
    background: rgba(0,240,255,0.06);
    color: var(--signal-cyan);
    border: 1px solid var(--signal-cyan);
    border-radius: 2px;
    font-family: 'Orbitron', sans-serif;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    font-size: 12.5px;
}
.stButton button:hover, .stDownloadButton button:hover {
    box-shadow: 0 0 16px rgba(0,240,255,0.45);
    border-color: var(--signal-cyan);
    color: var(--ink);
}
.stButton button[kind="primary"] {
    background: linear-gradient(90deg, rgba(0,240,255,0.15), rgba(255,46,136,0.12));
    border: 1px solid var(--signal-cyan);
    color: var(--ink);
}
.stButton button[kind="primary"]:hover {
    box-shadow: 0 0 22px rgba(0,240,255,0.55), 0 0 40px rgba(255,46,136,0.25);
}

.stTextInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"] > div {
    background: var(--panel) !important;
    color: var(--ink) !important;
    border: 1px solid rgba(0,240,255,0.25) !important;
    font-family: 'JetBrains Mono', monospace !important;
}
.stTextInput input:focus, .stTextArea textarea:focus {
    border-color: var(--signal-cyan) !important;
    box-shadow: 0 0 8px rgba(0,240,255,0.35) !important;
}

[data-testid="stExpander"] {
    background: var(--panel);
    border: 1px solid rgba(0,240,255,0.18);
}

.stProgress > div > div {
    background-image: linear-gradient(90deg, var(--signal-cyan), var(--pulse-magenta));
}

::-webkit-scrollbar { width: 10px; height: 10px; }
::-webkit-scrollbar-track { background: var(--void); }
::-webkit-scrollbar-thumb { background: rgba(0,240,255,0.35); border-radius: 4px; }

hr { border-color: rgba(0,240,255,0.15) !important; }

.cyber-highlight { background: rgba(255,176,0,0.28); color: var(--ink); padding: 0 2px; }

.cyber-footer {
    margin-top: 30px;
    padding-top: 12px;
    border-top: 1px solid rgba(0,240,255,0.15);
    font-size: 11px;
    color: var(--ash);
    letter-spacing: 1px;
    text-transform: uppercase;
}
</style>
"""


def inject_theme(st):
    st.markdown(CYBERPUNK_CSS, unsafe_allow_html=True)


def header_html(subtitle_html: str) -> str:
    return f"""
    <div class="cyber-header">
        <div class="cyber-eyebrow">// LOCAL_NEURAL_TERMINAL — NO_API_KEY_REQUIRED</div>
        <div class="cyber-title">AI MEETING NOTES<span class="cyber-cursor">_</span></div>
        <div class="cyber-subtitle">{subtitle_html}</div>
    </div>
    """


def section_html(index: str, label: str) -> str:
    return f'<div class="cyber-section"><span class="idx">[{index}]</span> {label}</div>'


def chip_html(text: str, kind: str) -> str:
    cls = {
        "Urgent": "chip-urgent", "High": "chip-high", "Normal": "chip-normal",
        "Positive": "chip-positive", "Neutral": "chip-neutral", "Negative": "chip-negative",
    }.get(text, "chip-normal")
    return f'<span class="chip {cls}">{text}</span>'


def highlight(text: str, query: str) -> str:
    """Wrap case-insensitive matches of `query` in a highlight span.
    Used only for display (already-escaped context), not raw HTML input."""
    if not query:
        return text
    import re
    pattern = re.compile(re.escape(query), re.IGNORECASE)
    return pattern.sub(lambda m: f'<span class="cyber-highlight">{m.group(0)}</span>', text)
