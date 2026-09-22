import streamlit as st

from src.parser import load_all_transcripts
from src.indexer import build_expert_index, build_index
from src.extractor import answer_guide_for_expert
from src.themes import analyze_themes
from src.qa import ask


st.set_page_config(
    page_title="Robotic Surgery Insights",
    page_icon="🤖",
    layout="wide",
)


# =========================================================
# STYLES  (single-line string, no indentation)
# =========================================================

st.markdown(
    "<style>"
    ".stApp{background:#f5f7fb;}"
    ".block-container{max-width:1250px;padding-top:1.5rem;padding-bottom:3rem;}"
    "header[data-testid='stHeader']{background:transparent;}"
    ".hero{"
    "background:radial-gradient(circle at 85% 20%,rgba(99,102,241,0.30),transparent 32%),"
    "linear-gradient(135deg,#111827 0%,#172554 55%,#312e81 100%);"
    "border-radius:22px;padding:30px 34px;margin-bottom:22px;"
    "box-shadow:0 12px 35px rgba(15,23,42,0.14);"
    "}"
    ".hero-top{display:flex;align-items:center;justify-content:space-between;gap:20px;}"
    ".hero-title{color:white;font-size:34px;font-weight:800;letter-spacing:-1px;margin:0;}"
    ".hero-subtitle{color:#cbd5e1;font-size:15px;margin-top:7px;}"
    ".local-badge{"
    "display:inline-flex;align-items:center;gap:7px;"
    "background:rgba(255,255,255,0.10);border:1px solid rgba(255,255,255,0.16);"
    "color:#dbeafe;border-radius:999px;padding:7px 12px;"
    "font-size:12px;font-weight:700;white-space:nowrap;"
    "}"
    ".status-dot{width:7px;height:7px;border-radius:50%;background:#4ade80;display:inline-block;}"
    ".metric-card{background:white;border:1px solid #e6eaf0;border-radius:16px;"
    "padding:18px 20px;box-shadow:0 4px 15px rgba(15,23,42,0.04);min-height:105px;}"
    ".metric-label{color:#64748b;font-size:11px;font-weight:800;"
    "letter-spacing:0.08em;text-transform:uppercase;}"
    ".metric-value{color:#111827;font-size:27px;font-weight:800;margin-top:5px;}"
    ".metric-detail{color:#94a3b8;font-size:12px;margin-top:2px;}"
    ".section-title{color:#111827;font-size:23px;font-weight:800;"
    "letter-spacing:-0.4px;margin-top:18px;margin-bottom:4px;}"
    ".section-subtitle{color:#64748b;font-size:14px;margin-bottom:18px;}"
    ".expert-card{background:white;border:1px solid #e5e7eb;border-radius:18px;"
    "padding:22px;box-shadow:0 5px 18px rgba(15,23,42,0.045);}"
    ".expert-label{color:#6366f1;font-size:11px;font-weight:800;"
    "text-transform:uppercase;letter-spacing:0.08em;}"
    ".expert-name{color:#111827;font-size:22px;font-weight:800;margin-top:7px;}"
    ".expert-role{color:#64748b;font-size:13px;margin-top:3px;}"
    ".expert-market{display:inline-block;margin-top:14px;padding:6px 10px;"
    "border-radius:999px;background:#eef2ff;color:#4f46e5;"
    "font-size:12px;font-weight:700;}"
    ".question-label{color:#64748b;font-size:11px;font-weight:800;"
    "text-transform:uppercase;letter-spacing:0.08em;margin-bottom:5px;}"
    ".answer-card{background:white;border:1px solid #e5e7eb;border-radius:18px;"
    "padding:24px 26px;margin-top:15px;box-shadow:0 7px 22px rgba(15,23,42,0.055);}"
    ".answer-label{color:#6366f1;font-size:11px;font-weight:800;"
    "text-transform:uppercase;letter-spacing:0.09em;margin-bottom:10px;}"
    ".answer-text{color:#172033;font-size:17px;line-height:1.7;}"
    ".evidence-heading{display:flex;align-items:center;gap:9px;color:#111827;"
    "font-size:20px;font-weight:800;margin-top:24px;margin-bottom:12px;}"
    ".quote-card{background:#f8faff;border:1px solid #e2e8f0;border-radius:14px;"
    "padding:18px 20px;margin-bottom:11px;}"
    ".quote-text{color:#1e293b;font-size:14px;line-height:1.7;font-style:italic;}"
    ".quote-meta{color:#64748b;font-size:11px;font-weight:700;margin-top:10px;}"
    "[data-testid='stSidebar']{background:#ffffff;border-right:1px solid #e5e7eb;}"
    "[data-testid='stSidebar'] h3{color:#111827;}"
    ".stButton > button{border-radius:10px;min-height:42px;font-weight:700;"
    "border:1px solid #dbe1ea;transition:0.15s ease;}"
    ".stButton > button:hover{border-color:#6366f1;color:#4f46e5;}"
    "button[data-baseweb='tab']{font-weight:700;font-size:14px;}"
    "[data-baseweb='tab-list']{gap:8px;}"
    "div[data-baseweb='select'] > div{border-radius:10px;}"
    "div[data-testid='stTextInput'] input{border-radius:10px;}"
    "[data-testid='stChatMessage']{border-radius:14px;}"
    ".footer{text-align:center;color:#94a3b8;font-size:11px;padding-top:35px;}"
    "</style>",
    unsafe_allow_html=True,
)


# =========================================================
# HERO HEADER
# =========================================================

st.markdown(
    '<div class="hero">'
    '<div class="hero-top">'
    '<div>'
    '<div class="hero-title">Robotic Surgery Insights</div>'
    '<div class="hero-subtitle">'
    'Evidence-grounded expert interview intelligence '
    'across France, Germany, and the UK.'
    '</div>'
    '</div>'
    '<div class="local-badge">'
    '<span class="status-dot"></span>'
    'Local AI · Ollama'
    '</div>'
    '</div>'
    '</div>',
    unsafe_allow_html=True,
)


# =========================================================
# LOAD DATA
# =========================================================

@st.cache_data
def load_data():
    return load_all_transcripts("data")


chunks = load_data()

chunks_by_expert = {}
for chunk in chunks:
    chunks_by_expert.setdefault(chunk["expert"], []).append(chunk)


# =========================================================
# BUILD INDEXES
# =========================================================

@st.cache_resource
def create_indexes(chunks_by_expert):
    return build_expert_index(chunks_by_expert)


expert_indexes = create_indexes(chunks_by_expert)


@st.cache_resource
def create_all_index(chunks):
    return build_index(chunks)


all_index = create_all_index(chunks)


# =========================================================
# SIDEBAR — EXPERT SELECTION
# =========================================================

experts = list(expert_indexes.keys())

selected_expert = st.sidebar.selectbox(
    "Select expert",
    experts,
)

index = expert_indexes[selected_expert]

selected_chunks = chunks_by_expert[selected_expert]

selected_market = (
    selected_chunks[0]["market"]
    if selected_chunks
    else "—"
)

selected_role = (
    selected_chunks[0].get("role", "Expert interview")
    if selected_chunks
    else "Expert interview"
)

st.sidebar.markdown("---")
st.sidebar.write(f"**Expert:** {selected_expert}")
st.sidebar.write(f"**Market:** {selected_market}")


# =========================================================
# METRIC CARDS
# =========================================================

expert_turns = [
    c for c in chunks if c["speaker"] != "Interviewer"
]

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown(
        '<div class="metric-card">'
        '<div class="metric-label">Experts</div>'
        f'<div class="metric-value">{len(chunks_by_expert):02d}</div>'
        '<div class="metric-detail">Expert interviews</div>'
        '</div>',
        unsafe_allow_html=True,
    )

with c2:
    st.markdown(
        '<div class="metric-card">'
        '<div class="metric-label">Markets</div>'
        '<div class="metric-value">03</div>'
        '<div class="metric-detail">France · Germany · UK</div>'
        '</div>',
        unsafe_allow_html=True,
    )

with c3:
    st.markdown(
        '<div class="metric-card">'
        '<div class="metric-label">Evidence</div>'
        f'<div class="metric-value">{len(expert_turns)}</div>'
        '<div class="metric-detail">Transcript turns</div>'
        '</div>',
        unsafe_allow_html=True,
    )

with c4:
    st.markdown(
        '<div class="metric-card">'
        '<div class="metric-label">Grounding</div>'
        '<div class="metric-value">Strict</div>'
        '<div class="metric-detail">Quote validation enabled</div>'
        '</div>',
        unsafe_allow_html=True,
    )


# =========================================================
# TABS
# =========================================================

tabs = st.tabs(
    [
        "Expert Guide",
        "Themes & Differences",
        "Transcript Evidence",
        "Ask Across Transcripts",
    ]
)


# =========================================================
# TAB 1 — EXPERT GUIDE
# =========================================================

with tabs[0]:

    st.markdown(
        '<div class="section-title">Interview Guide</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="section-subtitle">'
        'Answer the interview-guide questions using evidence retrieved '
        "from the selected expert's transcript."
        '</div>',
        unsafe_allow_html=True,
    )

    guide_questions = [
        "How would you describe current adoption of robotic surgery in your market?",
        "What are the main barriers to adoption?",
        "How important are hospital budgets and ROI in purchasing decisions?",
        "How important are surgeon training and clinical outcomes?",
        "What adoption trend do you expect over the next 3-5 years?",
        "What is the typical hospital decision-making timeline?",
    ]

    left, right = st.columns([0.32, 0.68], gap="large")

    with left:
        st.markdown(
            '<div class="expert-card">'
            '<div class="expert-label">Selected Expert</div>'
            f'<div class="expert-name">{selected_expert}</div>'
            f'<div class="expert-role">{selected_role}</div>'
            f'<div class="expert-market">{selected_market}</div>'
            '</div>',
            unsafe_allow_html=True,
        )

    with right:
        st.markdown(
            '<div class="question-label">Interview Guide Question</div>',
            unsafe_allow_html=True,
        )

        question = st.selectbox(
            "Interview question",
            guide_questions,
            label_visibility="collapsed",
        )

        analyze = st.button(
            "Analyze Evidence",
            type="primary",
            use_container_width=True,
        )

    if analyze:
        with st.spinner(
            "Retrieving evidence and generating grounded answer..."
        ):
            try:
                result = answer_guide_for_expert(
                    question,
                    index,
                )

                answer_text = result.get("answer", "Not addressed")

                st.markdown(
                    '<div class="answer-card">'
                    '<div class="answer-label">Grounded Answer</div>'
                    f'<div class="answer-text">{answer_text}</div>'
                    '</div>',
                    unsafe_allow_html=True,
                )

                quotes = result.get("quotes", [])

                if quotes:
                    st.markdown(
                        '<div class="evidence-heading">'
                        'Verified Evidence'
                        '</div>',
                        unsafe_allow_html=True,
                    )

                    for quote in quotes:
                        meta = (
                            f'{quote["timestamp"]} · '
                            f'{quote.get("expert", selected_expert)} · '
                            f'{selected_market}'
                        )

                        st.markdown(
                            '<div class="quote-card">'
                            f'<div class="quote-text">"{quote["text"]}"</div>'
                            f'<div class="quote-meta">{meta}</div>'
                            '</div>',
                            unsafe_allow_html=True,
                        )

                confidence = result.get("confidence")
                if confidence:
                    st.caption(f"Confidence: {confidence}")

            except Exception as e:
                st.error("Unable to generate the expert answer.")
                st.caption(f"Technical details: {e}")


# =========================================================
# TAB 2 — THEMES & DIFFERENCES
# =========================================================

with tabs[1]:

    st.markdown(
        '<div class="section-title">Common Themes & Differences</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="section-subtitle">'
        'Cross-expert analysis based only on the three transcripts.'
        '</div>',
        unsafe_allow_html=True,
    )

    if st.button("Analyze Themes", type="primary"):
        with st.spinner(
            "Analyzing all three transcripts with the local LLM — "
            "this can take up to a minute on a 3B model..."
        ):
            try:
                theme_data = analyze_themes(chunks)

                themes = theme_data.get("themes", [])
                differences = theme_data.get("differences", [])

                st.markdown(
                    '<div class="section-title">Common Themes</div>',
                    unsafe_allow_html=True,
                )

                if not themes:
                    st.info("No validated themes were returned.")

                for theme in themes:
                    st.markdown(f"#### {theme.get('theme', 'Theme')}")
                    st.write(theme.get("summary", ""))

                    for supporting in theme.get("supporting", []):
                        meta = (
                            f'{supporting.get("timestamp", "")} · '
                            f'{supporting.get("expert", "")}'
                        )
                        st.markdown(
                            '<div class="quote-card">'
                            f'<div class="quote-text">'
                            f'"{supporting.get("quote", "")}"'
                            f'</div>'
                            f'<div class="quote-meta">{meta}</div>'
                            '</div>',
                            unsafe_allow_html=True,
                        )

                st.markdown(
                    '<div class="section-title">Differences & Perspectives</div>',
                    unsafe_allow_html=True,
                )

                if not differences:
                    st.info("No validated differences were returned.")

                for difference in differences:
                    st.markdown(
                        f"#### {difference.get('topic', 'Difference')}"
                    )
                    st.write(difference.get("summary", ""))

                    for perspective in difference.get("perspectives", []):
                        st.markdown(
                            f"**{perspective.get('expert', '')}** — "
                            f"{perspective.get('view', '')}"
                        )

                        meta = perspective.get("timestamp", "")

                        st.markdown(
                            '<div class="quote-card">'
                            f'<div class="quote-text">'
                            f'"{perspective.get("quote", "")}"'
                            f'</div>'
                            f'<div class="quote-meta">{meta}</div>'
                            '</div>',
                            unsafe_allow_html=True,
                        )

            except Exception as e:
                st.error("Unable to analyze themes.")
                st.caption(f"Technical details: {e}")


# =========================================================
# TAB 3 — TRANSCRIPT EVIDENCE
# =========================================================

with tabs[2]:

    st.markdown(
        '<div class="section-title">Transcript Evidence</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="section-subtitle">'
        f'Showing transcript turns for <b>{selected_expert}</b>.'
        '</div>',
        unsafe_allow_html=True,
    )

    for chunk in selected_chunks:
        if chunk["speaker"] == "Interviewer":
            continue

        with st.expander(
            f'{chunk["timestamp"]} · {chunk["speaker"]} · {chunk["market"]}'
        ):
            st.write(chunk["text"])


# =========================================================
# TAB 4 — CROSS-TRANSCRIPT Q&A
# =========================================================

with tabs[3]:

    st.markdown(
        '<div class="section-title">Ask Across All Transcripts</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="section-subtitle">'
        'Answers are shown only if every citation matches a retrieved '
        'transcript turn. Otherwise the app fails closed.'
        '</div>',
        unsafe_allow_html=True,
    )

    if "chat" not in st.session_state:
        st.session_state.chat = []

    for role, msg, meta in st.session_state.chat:

        with st.chat_message(role):
            st.write(msg)

            if meta:
                if not meta.get("grounded"):
                    st.info(
                        "This is a fallback response — no grounded "
                        "answer was available from the retrieved evidence."
                    )

                if meta.get("citations"):
                    st.caption(
                        "Verified citations: "
                        + ", ".join(
                            f"[{e}, {m}, {t}]"
                            for e, m, t in meta["citations"]
                        )
                    )

                if meta.get("sources"):
                    with st.expander("Sources"):
                        for source in meta["sources"]:
                            st.markdown(
                                f'`{source["timestamp"]}` '
                                f'**{source["expert"]} '
                                f'({source["market"]})** — '
                                f'{source["text"]}'
                            )

    q = st.chat_input(
        "e.g. What are the main barriers to adoption across the three markets?"
    )

    if q:

        st.session_state.chat.append(("user", q, None))

        with st.chat_message("user"):
            st.write(q)

        with st.chat_message("assistant"):

            with st.spinner(
                "Searching all transcripts and generating a grounded answer..."
            ):

                try:
                    # Cross-transcript Q&A — uses the index built over ALL chunks
                    res = ask(all_index, q)

                    st.session_state.chat.append(
                        ("assistant", res["answer"], res)
                    )

                    st.write(res["answer"])

                    if not res.get("grounded"):
                        st.info(
                            "This is a fallback response — no grounded "
                            "answer was available from the retrieved evidence."
                        )

                    if res.get("citations"):
                        st.caption(
                            "Verified citations: "
                            + ", ".join(
                                f"[{e}, {m}, {t}]"
                                for e, m, t in res["citations"]
                            )
                        )

                    if res.get("sources"):
                        with st.expander("Sources"):
                            for source in res["sources"]:
                                st.markdown(
                                    f'`{source["timestamp"]}` '
                                    f'**{source["expert"]} '
                                    f'({source["market"]})** — '
                                    f'{source["text"]}'
                                )

                except Exception as e:
                    st.error(
                        "The local LLM could not generate a response. "
                        "Please make sure Ollama is running."
                    )
                    st.caption(f"Technical details: {e}")


# =========================================================
# FOOTER
# =========================================================

st.markdown(
    '<div class="footer">'
    'Evidence-grounded transcript analysis · Local LLM inference · '
    'Transcript data processed locally'
    '</div>',
    unsafe_allow_html=True,
)