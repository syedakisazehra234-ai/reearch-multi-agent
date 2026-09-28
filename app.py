```python
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
# Use st.html() instead of st.markdown() for HTML/CSS.
# ============================================================

st.html(
    """
    <style>

    /* ======================================================
       GLOBAL
       ====================================================== */

    .stApp {
        background:
            radial-gradient(
                circle at 10% 0%,
                rgba(99, 102, 241, 0.13),
                transparent 30%
            ),
            radial-gradient(
                circle at 90% 5%,
                rgba(168, 85, 247, 0.10),
                transparent 28%
            ),
            #080b12;
    }

    .block-container {
        max-width: 1200px;
        padding-top: 2rem;
        padding-bottom: 4rem;
    }

    /* ======================================================
       SIDEBAR
       ====================================================== */

    section[data-testid="stSidebar"] {
        background: #090c13;
        border-right: 1px solid rgba(255,255,255,0.07);
    }

    /* ======================================================
       HERO
       ====================================================== */

    .rl-hero {
        padding: 2.4rem 2.2rem;
        border-radius: 26px;

        background:
            linear-gradient(
                135deg,
                rgba(99, 102, 241, 0.20),
                rgba(168, 85, 247, 0.08)
            );

        border: 1px solid rgba(255,255,255,0.09);

        box-shadow:
            0 20px 70px rgba(0,0,0,0.22);

        margin-bottom: 1.8rem;
    }

    .rl-badge {
        display: inline-block;

        padding: 0.38rem 0.8rem;

        border-radius: 999px;

        background: rgba(255,255,255,0.07);

        border: 1px solid rgba(255,255,255,0.10);

        color: #c4b5fd;

        font-size: 0.72rem;

        font-weight: 800;

        letter-spacing: 0.10em;

        text-transform: uppercase;
    }

    .rl-title {
        margin: 0.9rem 0 0.6rem 0;

        color: #f8fafc;

        font-size: 3.1rem;

        line-height: 1.05;

        font-weight: 850;

        letter-spacing: -0.045em;
    }

    .rl-description {
        margin: 0;

        max-width: 750px;

        color: #a7adbd;

        font-size: 1.02rem;

        line-height: 1.7;
    }

    /* ======================================================
       SECTION LABEL
       ====================================================== */

    .rl-section-label {
        margin-bottom: 0.65rem;

        color: #8b93a7;

        font-size: 0.70rem;

        font-weight: 800;

        letter-spacing: 0.13em;

        text-transform: uppercase;
    }

    /* ======================================================
       AGENT CARDS
       ====================================================== */

    .rl-agent {
        padding: 1rem 1.15rem;

        margin-bottom: 0.65rem;

        border-radius: 16px;

        background: rgba(255,255,255,0.035);

        border: 1px solid rgba(255,255,255,0.065);

        transition: all 0.2s ease;
    }

    .rl-agent-active {
        background:
            linear-gradient(
                135deg,
                rgba(99,102,241,0.17),
                rgba(168,85,247,0.08)
            );

        border-color: rgba(129,140,248,0.38);

        box-shadow:
            0 0 28px rgba(99,102,241,0.10);
    }

    .rl-agent-done {
        border-color: rgba(52,211,153,0.20);
    }

    .rl-agent-row {
        display: flex;

        align-items: center;
    }

    .rl-agent-title {
        color: #f3f4f6;

        font-size: 0.94rem;

        font-weight: 750;
    }

    .rl-agent-description {
        margin-top: 0.28rem;

        color: #858da0;

        font-size: 0.78rem;
    }

    .rl-dot {
        width: 9px;
        height: 9px;

        margin-right: 9px;

        border-radius: 50%;

        display: inline-block;

        flex-shrink: 0;
    }

    .rl-dot-active {
        background: #a78bfa;

        box-shadow:
            0 0 12px rgba(167,139,250,0.9);
    }

    .rl-dot-done {
        background: #34d399;
    }

    .rl-dot-waiting {
        background: #4b5563;
    }

    /* ======================================================
       CURRENT AGENT
       ====================================================== */

    .rl-current {
        padding: 1.25rem 1.35rem;

        margin: 1.1rem 0 1.5rem 0;

        border-radius: 18px;

        background:
            linear-gradient(
                135deg,
                rgba(99,102,241,0.12),
                rgba(168,85,247,0.05)
            );

        border: 1px solid rgba(129,140,248,0.25);
    }

    .rl-current-label {
        color: #a78bfa;

        font-size: 0.68rem;

        font-weight: 850;

        letter-spacing: 0.13em;

        text-transform: uppercase;
    }

    .rl-current-name {
        margin-top: 0.28rem;

        color: #f8fafc;

        font-size: 1.25rem;

        font-weight: 800;
    }

    .rl-current-message {
        margin-top: 0.22rem;

        color: #a7adbd;

        font-size: 0.85rem;
    }

    /* ======================================================
       BUTTON
       ====================================================== */

    .stButton > button {
        width: 100%;

        min-height: 3rem;

        border-radius: 13px;

        border: 1px solid rgba(129,140,248,0.35);

        background:
            linear-gradient(
                135deg,
                #6366f1,
                #8b5cf6
            );

        color: white;

        font-weight: 800;

        transition:
            transform 0.2s ease,
            box-shadow 0.2s ease;
    }

    .stButton > button:hover {
        transform: translateY(-1px);

        box-shadow:
            0 12px 32px rgba(99,102,241,0.25);
    }

    /* ======================================================
       TEXT AREA
       ====================================================== */

    textarea {
        border-radius: 15px !important;
    }

    /* ======================================================
       REPORT
       ====================================================== */

    .rl-report-header {
        padding: 1rem 1.15rem;

        margin-bottom: 1rem;

        border-radius: 15px;

        background: rgba(255,255,255,0.035);

        border: 1px solid rgba(255,255,255,0.07);
    }

    /* ======================================================
       MOBILE
       ====================================================== */

    @media (max-width: 700px) {

        .rl-title {
            font-size: 2.2rem;
        }

        .rl-hero {
            padding: 1.6rem;
        }

    }

    </style>
    """
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
# AGENT DEFINITIONS
# ============================================================

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


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.html(
        """
        <div style="padding:0.8rem 0 0.5rem 0;">

            <div style="
                font-size:1.25rem;
                font-weight:800;
                color:#f8fafc;
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
        """
    )

    st.divider()

    st.markdown("### Research Team")

    st.caption(
        "Five specialized agents plan, research, "
        "challenge and synthesize evidence."
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

    st.caption("Powered by Groq")

    st.divider()

    st.caption(
        "ResearchLab AI · CrewAI + Groq + Streamlit"
    )


# ============================================================
# HERO
# ============================================================

st.html(
    """
    <div class="rl-hero">

        <span class="rl-badge">
            AI Research Workspace
        </span>

        <h1 class="rl-title">
            Research deeper.<br>
            Think critically.
        </h1>

        <p class="rl-description">
            A five-agent research team that plans your investigation,
            searches academic literature, gathers broader context,
            challenges the evidence and produces a structured report.
        </p>

    </div>
    """
)


# ============================================================
# RESEARCH QUESTION
# ============================================================

st.html(
    """
    <div class="rl-section-label">
        Research question
    </div>
    """
)

question = st.text_area(
    "Research question",
    placeholder=(
        "Example: What is the current role of artificial "
        "intelligence in pharmaceutical quality control?"
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
# PIPELINE
# ============================================================

st.html(
    """
    <div class="rl-section-label">
        Live research pipeline
    </div>
    """
)

pipeline_placeholder = st.empty()


def render_pipeline(active_agent=None):

    completed = st.session_state.completed_agents

    html = ""

    for name, description in agents:

        if name in completed:

            dot_class = "rl-dot-done"
            icon = "✓"
            card_class = "rl-agent rl-agent-done"

        elif name == active_agent:

            dot_class = "rl-dot-active"
            icon = "●"
            card_class = "rl-agent rl-agent-active"

        else:

            dot_class = "rl-dot-waiting"
            icon = "○"
            card_class = "rl-agent"

        html += f"""
        <div class="{card_class}">

            <div class="rl-agent-row">

                <span class="rl-dot {dot_class}"></span>

                <span class="rl-agent-title">
                    {icon}&nbsp;&nbsp;{name}
                </span>

            </div>

            <div class="rl-agent-description">
                {description}
            </div>

        </div>
        """

    pipeline_placeholder.html(html)


render_pipeline()


# ============================================================
# CURRENT AGENT
# ============================================================

current_placeholder = st.empty()


def update_agent(agent_name, message):

    st.session_state.current_agent = agent_name
    st.session_state.current_message = message

    current_placeholder.html(
        f"""
        <div class="rl-current">

            <div class="rl-current-label">
                ● Currently working
            </div>

            <div class="rl-current-name">
                {agent_name}
            </div>

            <div class="rl-current-message">
                {message}
            </div>

        </div>
        """
    )

    render_pipeline(agent_name)


# ============================================================
# RUN RESEARCH
# ============================================================

if start:

    if not question.strip():

        st.warning(
            "Please enter a research question first."
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

            if hasattr(result, "raw"):
                final_result = result.raw
            else:
                final_result = str(result)

            st.session_state.research_result = final_result

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

            with st.expander(
                "Technical details"
            ):
                st.exception(exc)


# ============================================================
# FINAL REPORT
# ============================================================

if st.session_state.research_result:

    st.divider()

    st.html(
        """
        <div class="rl-section-label">
            Final research report
        </div>

        <div class="rl-report-header">

            <div style="
                color:#f8fafc;
                font-size:1.05rem;
                font-weight:800;
            ">
                ✦ Research synthesis complete
            </div>

            <div style="
                color:#858da0;
                font-size:0.8rem;
                margin-top:0.25rem;
            ">
                Generated from the combined work of five specialized agents.
            </div>

        </div>
        """
    )

    st.markdown(
        st.session_state.research_result
    )
```
