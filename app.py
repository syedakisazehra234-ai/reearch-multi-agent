import streamlit as st

from crew import build_research_crew


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="ResearchLab AI",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    /* ---------- GLOBAL ---------- */

    .stApp {
        background:
            radial-gradient(
                circle at 10% 0%,
                rgba(99, 102, 241, 0.12),
                transparent 30%
            ),
            radial-gradient(
                circle at 90% 10%,
                rgba(168, 85, 247, 0.10),
                transparent 30%
            ),
            #080b12;
    }

    .block-container {
        max-width: 1200px;
        padding-top: 2rem;
        padding-bottom: 4rem;
    }

    /* ---------- HERO ---------- */

    .hero {
        padding: 2.2rem 2rem;
        border-radius: 24px;
        background:
            linear-gradient(
                135deg,
                rgba(99, 102, 241, 0.20),
                rgba(168, 85, 247, 0.10)
            );
        border: 1px solid rgba(255,255,255,0.10);
        margin-bottom: 1.5rem;
    }

    .hero-badge {
        display: inline-block;
        padding: 0.35rem 0.75rem;
        border-radius: 999px;
        background: rgba(255,255,255,0.08);
        border: 1px solid rgba(255,255,255,0.10);
        color: #c4b5fd;
        font-size: 0.78rem;
        font-weight: 700;
        letter-spacing: 0.08em;
        text-transform: uppercase;
    }

    .hero h1 {
        font-size: 3.2rem;
        line-height: 1.05;
        margin: 0.8rem 0 0.6rem 0;
        font-weight: 800;
        letter-spacing: -0.04em;
    }

    .hero p {
        color: #a7adbd;
        font-size: 1.05rem;
        max-width: 720px;
        line-height: 1.7;
    }

    /* ---------- SECTION ---------- */

    .section-label {
        color: #8b93a7;
        text-transform: uppercase;
        letter-spacing: 0.12em;
        font-size: 0.72rem;
        font-weight: 800;
        margin-bottom: 0.6rem;
    }

    /* ---------- AGENT CARD ---------- */

    .agent-card {
        padding: 1rem 1.15rem;
        border-radius: 16px;
        background: rgba(255,255,255,0.035);
        border: 1px solid rgba(255,255,255,0.07);
        margin-bottom: 0.6rem;
    }

    .agent-active {
        background:
            linear-gradient(
                135deg,
                rgba(99,102,241,0.16),
                rgba(168,85,247,0.08)
            );
        border: 1px solid rgba(129,140,248,0.35);
        box-shadow:
            0 0 25px rgba(99,102,241,0.10);
    }

    .agent-done {
        border-color: rgba(34,197,94,0.18);
    }

    .agent-title {
        font-weight: 700;
        color: #f3f4f6;
    }

    .agent-subtitle {
        color: #8f97aa;
        font-size: 0.82rem;
        margin-top: 0.2rem;
    }

    .dot {
        display: inline-block;
        width: 9px;
        height: 9px;
        border-radius: 50%;
        margin-right: 8px;
    }

    .dot-active {
        background: #a78bfa;
        box-shadow: 0 0 12px #a78bfa;
    }

    .dot-done {
        background: #34d399;
    }

    .dot-waiting {
        background: #4b5563;
    }

    /* ---------- CURRENT AGENT ---------- */

    .current-agent {
        padding: 1.3rem;
        border-radius: 18px;
        background: rgba(99,102,241,0.08);
        border: 1px solid rgba(129,140,248,0.25);
        margin: 1rem 0 1.5rem 0;
    }

    .current-label {
        color: #a78bfa;
        font-size: 0.72rem;
        text-transform: uppercase;
        letter-spacing: 0.12em;
        font-weight: 800;
    }

    .current-name {
        font-size: 1.35rem;
        font-weight: 800;
        margin-top: 0.3rem;
    }

    .current-message {
        color: #a7adbd;
        margin-top: 0.25rem;
    }

    /* ---------- REPORT ---------- */

    .report-shell {
        padding: 1.6rem;
        border-radius: 20px;
        background: rgba(255,255,255,0.025);
        border: 1px solid rgba(255,255,255,0.08);
    }

    /* ---------- SIDEBAR ---------- */

    section[data-testid="stSidebar"] {
        background: #0a0d14;
        border-right: 1px solid rgba(255,255,255,0.07);
    }

    /* ---------- BUTTON ---------- */

    .stButton > button {
        width: 100%;
        border-radius: 13px;
        min-height: 3rem;
        font-weight: 750;
        border: 1px solid rgba(129,140,248,0.35);
        background:
            linear-gradient(
                135deg,
                #6366f1,
                #8b5cf6
            );
        color: white;
        transition: all 0.2s ease;
    }

    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 10px 30px rgba(99,102,241,0.25);
    }

    /* ---------- TEXTAREA ---------- */

    textarea {
        border-radius: 15px !important;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# SESSION STATE
# ============================================================

if "research_result" not in st.session_state:
    st.session_state.research_result = None

if "current_agent" not in st.session_state:
    st.session_state.current_agent = "Waiting for research"

if "current_message" not in st.session_state:
    st.session_state.current_message = "Ready to begin."

if "completed_agents" not in st.session_state:
    st.session_state.completed_agents = []


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown(
        """
        <div style="padding: 0.8rem 0;">
            <div style="
                font-size:1.25rem;
                font-weight:800;
                letter-spacing:-0.03em;
            ">
                ✦ ResearchLab AI
            </div>

            <div style="
                color:#858da0;
                font-size:0.82rem;
                margin-top:0.25rem;
            ">
                Multi-agent research workspace
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.divider()

    st.markdown("### Research Team")

    st.caption(
        "Five specialized agents work sequentially to "
        "plan, research, challenge and synthesize evidence."
    )

    st.markdown(
        """
        **01** · Research Planner  
        **02** · Academic Researcher  
        **03** · Web Researcher  
        **04** · Evidence Critic  
        **05** · Research Writer
        """
    )

    st.divider()

    st.markdown("### Model")

    st.code(
        "openai/gpt-oss-120b",
        language="text",
    )

    st.caption(
        "Powered by Groq"
    )

    st.divider()

    st.caption(
        "ResearchLab AI · CrewAI + Groq + Streamlit"
    )


# ============================================================
# HERO
# ============================================================

st.markdown(
    """
    <div class="hero">

        <span class="hero-badge">
            AI Research Workspace
        </span>

        <h1>
            Research deeper.<br>
            Think critically.
        </h1>

        <p>
            A five-agent research team that plans your investigation,
            searches academic literature, gathers broader context,
            challenges the evidence and produces a structured report.
        </p>

    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# RESEARCH INPUT
# ============================================================

st.markdown(
    '<div class="section-label">Research question</div>',
    unsafe_allow_html=True,
)

question = st.text_area(
    "",
    placeholder=(
        "Example: What is the current role of artificial intelligence "
        "in pharmaceutical quality control?"
    ),
    height=120,
    label_visibility="collapsed",
)


st.write("")

start = st.button(
    "⚡  Start Research",
    type="primary",
)


# ============================================================
# PIPELINE DISPLAY
# ============================================================

st.markdown(
    '<div class="section-label">Live research pipeline</div>',
    unsafe_allow_html=True,
)

agents = [
    (
        "Research Planner",
        "Defines the research strategy",
    ),
    (
        "Academic Researcher",
        "Searches scholarly literature",
    ),
    (
        "Web Researcher",
        "Investigates broader context",
    ),
    (
        "Evidence Critic",
        "Challenges the evidence",
    ),
    (
        "Research Writer",
        "Synthesizes the final report",
    ),
]


pipeline_placeholder = st.empty()


def render_pipeline(active_agent=None):

    completed = st.session_state.completed_agents

    html = ""

    for name, description in agents:

        if name in completed:

            dot = "dot-done"
            icon = "✓"
            extra = "agent-done"

        elif name == active_agent:

            dot = "dot-active"
            icon = "●"
            extra = "agent-active"

        else:

            dot = "dot-waiting"
            icon = "○"
            extra = ""

        html += f"""
        <div class="agent-card {extra}">

            <div>
                <span class="dot {dot}"></span>

                <span class="agent-title">
                    {icon} &nbsp;{name}
                </span>
            </div>

            <div class="agent-subtitle">
                {description}
            </div>

        </div>
        """

    pipeline_placeholder.markdown(
        html,
        unsafe_allow_html=True,
    )


render_pipeline()


# ============================================================
# CURRENT AGENT
# ============================================================

current_placeholder = st.empty()


def update_agent(agent_name, message):

    st.session_state.current_agent = agent_name
    st.session_state.current_message = message

    current_placeholder.markdown(
        f"""
        <div class="current-agent">

            <div class="current-label">
                ● Currently working
            </div>

            <div class="current-name">
                {agent_name}
            </div>

            <div class="current-message">
                {message}
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )

    render_pipeline(agent_name)


# ============================================================
# RUN RESEARCH
# ============================================================

if start:

    if not question.strip():

        st.warning(
            "Enter a research question first."
        )

    else:

        st.session_state.research_result = None
        st.session_state.completed_agents = []

        update_agent(
            "Research Planner",
            "Preparing your research strategy..."
        )

        try:

            crew = build_research_crew(
                status_callback=update_agent
            )

            result = crew.kickoff(
                inputs={
                    "question": question.strip()
                }
            )

            st.session_state.research_result = str(
                result.raw
                if hasattr(result, "raw")
                else result
            )

            st.session_state.completed_agents = [
                name
                for name, _ in agents
            ]

            update_agent(
                "Research Complete",
                "All five agents have completed their work."
            )

            render_pipeline(None)

        except Exception as exc:

            st.error(
                "The research team encountered an error."
            )

            st.exception(exc)


# ============================================================
# FINAL REPORT
# ============================================================

if st.session_state.research_result:

    st.divider()

    st.markdown(
        '<div class="section-label">Final research report</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="report-shell">',
        unsafe_allow_html=True,
    )

    st.markdown(
        st.session_state.research_result
    )

    st.markdown(
        '</div>',
        unsafe_allow_html=True,
    )
