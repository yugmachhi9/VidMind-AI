import streamlit as st
from dotenv import load_dotenv
from utils.audio_processor import process_input
from core.transcriber import transcribe_all
from core.summarizer import summarize, generate_title
from core.extractor import extract_action_items, extract_key_decisions, extract_questions
from core.rag_engine import build_rag_chain, ask_question

load_dotenv()

# ─── Page Config ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="VidMind AI",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",   # sidebar open by default
)

# ─── Global Styles ───────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Mono:wght@300;400;500&display=swap');

:root {
    --bg:        #080b12;
    --bg2:       #0d1120;
    --surface:   #111827;
    --border:    #1e2d45;
    --accent:    #00d4ff;
    --accent2:   #7c3aed;
    --accent3:   #f59e0b;
    --text:      #e2e8f0;
    --muted:     #64748b;
    --success:   #10b981;
    --glow:      0 0 24px rgba(0,212,255,.25);
    --glow2:     0 0 24px rgba(124,58,237,.25);
}

html, body, [data-testid="stAppViewContainer"] {
    background: var(--bg) !important;
    color: var(--text) !important;
    font-family: 'DM Mono', monospace !important;
}

[data-testid="stHeader"], [data-testid="stToolbar"] { display: none !important; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: var(--bg2) !important;
    border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] * {
    font-family: 'DM Mono', monospace !important;
}
.sb-logo {
    text-align: center;
    padding: 1rem 0 1.4rem;
    border-bottom: 1px solid var(--border);
    margin-bottom: 1.6rem;
}
.sb-logo-title {
    font-family: 'Syne', sans-serif !important;
    font-size: 1.2rem;
    font-weight: 800;
    background: linear-gradient(135deg, #fff 0%, var(--accent) 55%, var(--accent2) 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
}
.sb-logo-sub {
    font-size: .6rem;
    color: var(--muted);
    letter-spacing: .16em;
    text-transform: uppercase;
    margin-top: .2rem;
}
.sb-section {
    font-size: .6rem;
    letter-spacing: .18em;
    text-transform: uppercase;
    color: var(--muted);
    padding-bottom: .5rem;
    border-bottom: 1px solid var(--border);
    margin-bottom: 1rem;
}

/* ── Hero ── */
.hero {
    text-align: center;
    padding: 3rem 0 2rem;
}
.hero-badge {
    display: inline-block;
    background: linear-gradient(135deg,rgba(0,212,255,.12),rgba(124,58,237,.12));
    border: 1px solid var(--border);
    color: var(--accent);
    font-size: .7rem;
    letter-spacing: .18em;
    text-transform: uppercase;
    padding: .35rem 1rem;
    border-radius: 999px;
    margin-bottom: 1.2rem;
}
.hero-title {
    font-family: 'Syne', sans-serif;
    font-size: clamp(2.4rem, 5vw, 4rem);
    font-weight: 800;
    line-height: 1.1;
    background: linear-gradient(135deg, #ffffff 0%, var(--accent) 50%, var(--accent2) 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin: 0 0 .6rem;
}
.hero-sub {
    color: var(--muted);
    font-size: .9rem;
    letter-spacing: .04em;
}

/* ── Input Card ── */
.input-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 2rem;
    margin: 1.5rem auto;
    max-width: 860px;
    box-shadow: var(--glow);
}

/* ── Widget overrides ── */
.stTextInput > div > div > input,
.stSelectbox > div > div {
    background: var(--bg2) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    color: var(--text) !important;
    font-family: 'DM Mono', monospace !important;
}
.stTextInput > div > div > input:focus {
    border-color: var(--accent) !important;
    box-shadow: var(--glow) !important;
}
label, .stSelectbox label {
    color: var(--muted) !important;
    font-size: .75rem !important;
    letter-spacing: .08em !important;
    text-transform: uppercase !important;
}

/* ── Buttons ── */
.stButton > button {
    background: linear-gradient(135deg, var(--accent), var(--accent2)) !important;
    border: none !important;
    border-radius: 10px !important;
    color: #fff !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
    font-size: .95rem !important;
    letter-spacing: .06em !important;
    padding: .75rem 2rem !important;
    transition: opacity .2s, transform .15s !important;
}
.stButton > button:hover { opacity: .88; transform: translateY(-1px); }
.stButton > button:active { transform: translateY(0); }

/* ══════════════════════════════════════════════
   UPGRADED RESULT CARDS
══════════════════════════════════════════════ */

/* base card */
.result-card {
    border-radius: 16px;
    padding: 0;
    margin-bottom: 1.4rem;
    position: relative;
    overflow: hidden;
    box-shadow: 0 4px 24px rgba(0,0,0,.4);
}

/* top accent bar */
.result-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    z-index: 2;
}
.card-summary::before   { background: linear-gradient(90deg, var(--accent), var(--accent2)); }
.card-actions::before   { background: linear-gradient(90deg, var(--success), #059669); }
.card-decisions::before { background: linear-gradient(90deg, var(--accent2), #a855f7); }
.card-questions::before { background: linear-gradient(90deg, var(--accent3), #f97316); }
.card-transcript::before{ background: linear-gradient(90deg, var(--muted), #334155); }

/* inner header band */
.card-header {
    display: flex;
    align-items: center;
    gap: .7rem;
    padding: .9rem 1.4rem;
    border-bottom: 1px solid rgba(255,255,255,.05);
}
.card-summary   .card-header { background: linear-gradient(135deg, rgba(0,212,255,.1), rgba(124,58,237,.06)); }
.card-actions   .card-header { background: linear-gradient(135deg, rgba(16,185,129,.1), rgba(5,150,105,.05)); }
.card-decisions .card-header { background: linear-gradient(135deg, rgba(124,58,237,.1), rgba(168,85,247,.06)); }
.card-questions .card-header { background: linear-gradient(135deg, rgba(245,158,11,.1), rgba(249,115,22,.06)); }
.card-transcript .card-header{ background: rgba(255,255,255,.03); }

.card-icon {
    font-size: 1.1rem;
    line-height: 1;
    flex-shrink: 0;
}
.card-label {
    font-family: 'Syne', sans-serif;
    font-size: .72rem;
    font-weight: 700;
    letter-spacing: .16em;
    text-transform: uppercase;
    flex: 1;
}
.card-summary   .card-label { color: var(--accent); }
.card-actions   .card-label { color: var(--success); }
.card-decisions .card-label { color: #a78bfa; }
.card-questions .card-label { color: var(--accent3); }
.card-transcript .card-label{ color: var(--muted); }

/* badge showing line count */
.card-badge {
    font-size: .6rem;
    letter-spacing: .06em;
    padding: .2rem .55rem;
    border-radius: 999px;
    font-family: 'DM Mono', monospace;
}
.card-summary   .card-badge { background: rgba(0,212,255,.12); color: var(--accent); border: 1px solid rgba(0,212,255,.2); }
.card-actions   .card-badge { background: rgba(16,185,129,.12); color: var(--success); border: 1px solid rgba(16,185,129,.2); }
.card-decisions .card-badge { background: rgba(124,58,237,.12); color: #a78bfa; border: 1px solid rgba(124,58,237,.2); }
.card-questions .card-badge { background: rgba(245,158,11,.12); color: var(--accent3); border: 1px solid rgba(245,158,11,.2); }
.card-transcript .card-badge{ background: rgba(100,116,139,.1); color: var(--muted); border: 1px solid rgba(100,116,139,.2); }

/* body */
.card-body {
    background: var(--surface);
    padding: 1.2rem 1.5rem 1.4rem;
}
.card-content {
    color: var(--text);
    font-size: .88rem;
    line-height: 1.85;
    white-space: pre-wrap;
}

/* ── Title pill ── */
.title-pill {
    display: inline-flex;
    align-items: center;
    gap: .6rem;
    background: linear-gradient(135deg,rgba(0,212,255,.1),rgba(124,58,237,.1));
    border: 1px solid rgba(0,212,255,.3);
    border-radius: 12px;
    padding: .8rem 1.4rem;
    font-family: 'Syne', sans-serif;
    font-weight: 700;
    font-size: 1.1rem;
    color: var(--text);
    margin-bottom: 1.5rem;
    box-shadow: var(--glow);
    width: 100%;
}
.title-icon { font-size: 1.3rem; }

/* ── Chat area ── */
.chat-header {
    font-family: 'Syne', sans-serif;
    font-size: .7rem;
    font-weight: 700;
    letter-spacing: .16em;
    text-transform: uppercase;
    color: var(--accent);
    margin: 2rem 0 1rem;
    display: flex;
    align-items: center;
    gap: .5rem;
}
.chat-header::after { content:''; flex: 1; height: 1px; background: var(--border); }

.msg-user {
    background: linear-gradient(135deg,rgba(0,212,255,.08),rgba(124,58,237,.08));
    border: 1px solid rgba(0,212,255,.2);
    border-radius: 12px 12px 4px 12px;
    padding: .75rem 1rem;
    margin-bottom: .8rem;
    font-size: .88rem;
    text-align: right;
    color: var(--text);
}
.msg-bot {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px 12px 12px 4px;
    padding: .75rem 1rem;
    margin-bottom: .8rem;
    font-size: .88rem;
    color: var(--text);
    line-height: 1.7;
}
.msg-label-user { font-size:.65rem; color:var(--accent); letter-spacing:.08em; text-transform:uppercase; margin-bottom:.3rem; text-align:right; }
.msg-label-bot  { font-size:.65rem; color:var(--muted);  letter-spacing:.08em; text-transform:uppercase; margin-bottom:.3rem; }

/* ── Progress ── */
.stProgress > div > div { background: linear-gradient(90deg,var(--accent),var(--accent2)) !important; border-radius: 4px !important; }
.stSpinner > div { border-top-color: var(--accent) !important; }
hr { border-color: var(--border) !important; }

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] { background: var(--surface) !important; border-radius: 12px !important; border: 1px solid var(--border) !important; padding: 4px !important; gap: 4px !important; }
.stTabs [data-baseweb="tab"] { background: transparent !important; color: var(--muted) !important; border-radius: 8px !important; font-family: 'DM Mono', monospace !important; font-size: .82rem !important; }
.stTabs [aria-selected="true"] { background: linear-gradient(135deg,var(--accent),var(--accent2)) !important; color: #fff !important; }
.stTabs [data-baseweb="tab-panel"] { padding-top: 1.2rem !important; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: var(--bg2); }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: var(--accent); }
</style>
""", unsafe_allow_html=True)


# ─── Session State Init ───────────────────────────────────────────────────────
for key in ["result", "chat_history", "processing"]:
    if key not in st.session_state:
        st.session_state[key] = None if key != "chat_history" else []


# ─── Sidebar ─────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div class="sb-logo">
        <div class="sb-logo-title">🎬 VidMind AI</div>
        <div class="sb-logo-sub">Video Intelligence</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="sb-section">⚙ Settings</div>', unsafe_allow_html=True)

    language = st.selectbox(
        "Transcription Language",
        ["english", "hinglish", "hindi", "french", "spanish"],
        index=0,
        key="lang_select",
    )

    model_choice = st.selectbox(
        "Summarization Model",
        ["GPT-4o", "GPT-4o Mini", "Claude 3.5 Sonnet", "Gemini 1.5 Pro"],
        index=0,
        key="model_select",
    )

    chunk_size = st.selectbox(
        "Chunk Size (tokens)",
        ["512", "1024", "2048", "4096"],
        index=1,
        key="chunk_select",
    )

    insight_depth = st.radio(
        "Insight Depth",
        ["Concise", "Detailed", "Exhaustive"],
        index=1,
        key="depth_select",
        horizontal=True,
    )

    st.markdown("<hr>", unsafe_allow_html=True)

    if st.button("🗑  Clear Session", use_container_width=True):
        st.session_state.result = None
        st.session_state.chat_history = []
        st.rerun()

    # session stats
    if st.session_state.result:
        words = len(st.session_state.result["transcript"].split())
        turns = len(st.session_state.chat_history) // 2
        st.markdown(f"""
        <div style="margin-top:1.2rem;font-size:.7rem;color:var(--muted);">
            <div style="margin-bottom:.4rem">📝 Transcript: <span style="color:var(--accent)">{words:,} words</span></div>
            <div>💬 Chat turns: <span style="color:var(--accent)">{turns}</span></div>
        </div>
        """, unsafe_allow_html=True)


# ─── Helper: upgraded result card ─────────────────────────────────────────────
def result_card(icon: str, label: str, content: str, css_class: str, badge: str = ""):
    st.markdown(f"""
    <div class="result-card {css_class}">
        <div class="card-header">
            <span class="card-icon">{icon}</span>
            <span class="card-label">{label}</span>
            {f'<span class="card-badge">{badge}</span>' if badge else ''}
        </div>
        <div class="card-body">
            <div class="card-content">{content}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ─── Hero ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <div class="hero-badge">⚡ AI-Powered Video Intelligence</div>
    <div class="hero-title">VidMind AI</div>
    <div class="hero-sub">Drop a YouTube URL or local file — get a full intelligence brief in seconds</div>
</div>
""", unsafe_allow_html=True)


# ─── Input Section ───────────────────────────────────────────────────────────
st.markdown('<div class="input-card">', unsafe_allow_html=True)

col1, col2 = st.columns([3, 1])
with col1:
    source = st.text_input(
        "Video Source",
        placeholder="https://youtube.com/watch?v=... or /path/to/file.mp4",
        key="source_input",
    )
with col2:
    # language is now in sidebar; show a read-only reminder
    st.markdown(f"<div style='padding-top:1.9rem;font-size:.72rem;color:var(--muted)'>Lang set in sidebar</div>", unsafe_allow_html=True)

col_btn, col_spacer = st.columns([1, 3])
with col_btn:
    run_btn = st.button("🚀  Analyse Video", use_container_width=True)

st.markdown('</div>', unsafe_allow_html=True)


# ─── Pipeline ────────────────────────────────────────────────────────────────
if run_btn and source.strip():
    st.session_state.chat_history = []
    st.session_state.result = None

    progress_bar = st.progress(0)
    status = st.empty()

    steps = [
        (10,  "🎧  Processing audio input…"),
        (25,  "📝  Transcribing audio…"),
        (45,  "✨  Generating title & summary…"),
        (65,  "🔍  Extracting insights…"),
        (85,  "🧠  Building RAG knowledge base…"),
        (100, "✅  Done!"),
    ]

    try:
        for i, (pct, msg) in enumerate(steps[:-1]):
            status.markdown(f"<p style='color:var(--accent);font-size:.85rem'>{msg}</p>", unsafe_allow_html=True)
            progress_bar.progress(pct)

            if i == 0:
                chunks = process_input(source.strip())
            elif i == 1:
                transcript = transcribe_all(chunks, st.session_state.lang_select)
            elif i == 2:
                title   = generate_title(transcript)
                summary = summarize(transcript)
            elif i == 3:
                action_items = extract_action_items(transcript)
                decisions    = extract_key_decisions(transcript)
                questions    = extract_questions(transcript)
            elif i == 4:
                rag_chain = build_rag_chain(transcript)

        progress_bar.progress(100)
        status.markdown(f"<p style='color:var(--success);font-size:.85rem'>{steps[-1][1]}</p>", unsafe_allow_html=True)

        st.session_state.result = {
            "title":         title,
            "transcript":    transcript,
            "summary":       summary,
            "action_items":  action_items,
            "key_decisions": decisions,
            "open_questions":questions,
            "rag_chain":     rag_chain,
        }

    except Exception as e:
        st.error(f"Pipeline error: {e}")
        progress_bar.empty()
        status.empty()

elif run_btn and not source.strip():
    st.warning("Please enter a YouTube URL or local file path.")


# ─── Results ─────────────────────────────────────────────────────────────────
if st.session_state.result:
    res = st.session_state.result

    word_count  = len(res["transcript"].split())
    action_lines = len([l for l in res["action_items"].splitlines() if l.strip()])
    dec_lines    = len([l for l in res["key_decisions"].splitlines() if l.strip()])
    q_lines      = len([l for l in res["open_questions"].splitlines() if l.strip()])

    st.markdown(f"""
    <div class="title-pill">
        <span class="title-icon">🎬</span>
        {res['title']}
    </div>
    """, unsafe_allow_html=True)

    tab_insights, tab_transcript, tab_chat = st.tabs(
        ["📊  Insights", "📄  Transcript", "💬  Chat with Video"]
    )

    with tab_insights:
        result_card("📋", "Summary",        res["summary"],        "card-summary",   "AI generated")
        result_card("✅", "Action Items",   res["action_items"],   "card-actions",   f"{action_lines} items")
        result_card("🔑", "Key Decisions",  res["key_decisions"],  "card-decisions", f"{dec_lines} decisions")
        result_card("❓", "Open Questions", res["open_questions"], "card-questions", f"{q_lines} questions")

    with tab_transcript:
        result_card("🗒", "Full Transcript", res["transcript"], "card-transcript", f"{word_count:,} words")

    with tab_chat:
        st.markdown('<div class="chat-header">💬 Ask anything about this video</div>', unsafe_allow_html=True)

        for msg in st.session_state.chat_history:
            if msg["role"] == "user":
                st.markdown(f"""
                <div class="msg-label-user">You</div>
                <div class="msg-user">{msg['content']}</div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="msg-label-bot">🤖 VidMind</div>
                <div class="msg-bot">{msg['content']}</div>
                """, unsafe_allow_html=True)

        chat_col, send_col = st.columns([5, 1])
        with chat_col:
            user_q = st.text_input(
                "question",
                placeholder="What was decided about the budget?",
                label_visibility="collapsed",
                key="chat_input",
            )
        with send_col:
            send_btn = st.button("Send", use_container_width=True, key="send_btn")

        if send_btn and user_q.strip():
            st.session_state.chat_history.append({"role": "user", "content": user_q.strip()})
            with st.spinner("Thinking…"):
                answer = ask_question(res["rag_chain"], user_q.strip())
            st.session_state.chat_history.append({"role": "assistant", "content": answer})
            st.rerun()


# ─── Empty state ──────────────────────────────────────────────────────────────
if not st.session_state.result:
    st.markdown("""
    <div style="text-align:center;padding:3rem 0;color:var(--muted);">
        <div style="font-size:3rem;margin-bottom:1rem">🎬</div>
        <div style="font-family:'Syne',sans-serif;font-size:1rem;letter-spacing:.06em">
            Paste a URL or file path above and hit <span style="color:var(--accent)">Analyse Video</span>
        </div>
    </div>
    """, unsafe_allow_html=True)


#for run                      
# source .venv/bin/activate
# python -m streamlit run app.py