import streamlit as st

from crew import build_research_crew
from tools.research_tools import (
    AcademicSearchTool,
    WebResearchTool,
)


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="ResearchLab AI",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded",
)


# =========================================================
# GLOBAL CSS
# =========================================================

st.html(
    """
    <style>

    .stApp {
        background:
            radial-gradient(
                circle at 15% 10%,
                rgba(99, 102, 241, 0.14),
                transparent 28%
            ),
            radial-gradient(
                circle at 85% 15%,
                rgba(168, 85, 247, 0.10),
                transparent 25%
            ),
            linear-gradient(
                135deg,
                #070b17 0%,
                #0b1020 45%,
                #080d19 100%
            );
    }

    .main {
        padding-top: 1.5rem;
    }

    #MainMenu {
        visibility: hidden;
    }

    footer {
        visibility: hidden;
    }

    header {
        background: transparent !important;
    }

    section[data-testid="stSidebar"] {
        background:
            linear-gradient(
                180deg,
                #080d19 0%,
                #0b1020 100%
            );

        border-right:
            1px solid
            rgba(148, 163, 184, 0.10);
    }

    section[data-testid="stSidebar"] > div {
        padding-top: 2rem;
    }

    div[data-baseweb="textarea"] {
        background:
            rgba(15, 23, 42, 0.75);

        border-radius: 14px;
    }

    textarea {
        color: #f8fafc !important;
        font-size: 15px !important;
        line-height: 1.6 !important;
    }

    div.stButton > button {
        width: 100%;

        border:
            1px solid
            rgba(129, 140, 248, 0.35);

        border-radius: 12px;

        padding:
            0.75rem 1.2rem;

        font-weight: 700;

        color: white;

        background:
            linear-gradient(
                135deg,
                #4f46e5,
                #7c3aed
            );

        box-shadow:
            0 8px 30px
            rgba(79, 70, 229, 0.22);

        transition:
            all 0.2s ease;
    }

    div.stButton > button:hover {
        border-color:
            rgba(165, 180, 252, 0.8);

        transform:
            translateY(-1px);

        box-shadow:
            0 12px 35px
            rgba(79, 70, 229, 0.30);
    }

    div.stButton > button:disabled {
        opacity: 0.5;
    }

    .report-container {
        background:
            rgba(15, 23, 42, 0.58);

        border:
            1px solid
            rgba(148, 163, 184, 0.12);

        border-radius: 20px;

        padding: 2rem;

        margin-top: 1.2rem;

        box-shadow:
            0 20px 60px
            rgba(0, 0, 0, 0.18);
    }

    @media (max-width: 768px) {

        .hero-title {
            font-size: 2rem !important;
        }

        .report-container {
            padding: 1rem;
        }

    }

    </style>
    """
)


# =========================================================
# SESSION STATE
# =========================================================

if "research_result" not in st.session_state:
    st.session_state.research_result = None

if "research_question" not in st.session_state:
    st.session_state.research_question = ""

if "research_running" not in st.session_state:
    st.session_state.research_running = False

if "agent_status" not in st.session_state:

    st.session_state.agent_status = {
        "Research Planner": "waiting",
        "Academic Researcher": "waiting",
        "Web Researcher": "waiting",
        "Evidence Critic": "waiting",
        "Research Writer": "waiting",
    }

if "agent_messages" not in st.session_state:
    st.session_state.agent_messages = {}


# =========================================================
# AGENTS
# =========================================================

AGENTS = [

    (
        "Research Planner",
        "Defines the research strategy",
    ),

    (
        "Academic Researcher",
        "Analyzes scholarly evidence",
    ),

    (
        "Web Researcher",
        "Analyzes broader web context",
    ),

    (
        "Evidence Critic",
        "Checks evidence quality and gaps",
    ),

    (
        "Research Writer",
        "Synthesizes the final report",
    ),

]


# =========================================================
# AGENT STATUS CALLBACK
# =========================================================

def update_agent(agent_name, message):

    if agent_name not in st.session_state.agent_status:
        return

    for name, _ in AGENTS:

        if name == agent_name:

            st.session_state.agent_status[name] = "active"

        elif st.session_state.agent_status[name] == "active":

            st.session_state.agent_status[name] = "done"

    st.session_state.agent_messages[agent_name] = message


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    # -----------------------------------------------------
    # BRAND
    # -----------------------------------------------------

    st.html(
        """
        <div
            style="
                padding:0.5rem 0 1.5rem 0;
            "
        >

            <div
                style="
                    display:flex;
                    align-items:center;
                    gap:10px;
                    margin-bottom:8px;
                "
            >

                <div
                    style="
                        width:38px;
                        height:38px;
                        border-radius:11px;
                        display:flex;
                        align-items:center;
                        justify-content:center;
                        background:
                            linear-gradient(
                                135deg,
                                #4f46e5,
                                #9333ea
                            );
                        box-shadow:
                            0 8px 25px
                            rgba(
                                79,
                                70,
                                229,
                                0.3
                            );
                        font-size:19px;
                    "
                >
                    🔬
                </div>

                <div>

                    <div
                        style="
                            color:#f8fafc;
                            font-size:18px;
                            font-weight:800;
                        "
                    >
                        ResearchLab
                    </div>

                    <div
                        style="
                            color:#64748b;
                            font-size:11px;
                        "
                    >
                        Multi-Agent AI
                    </div>

                </div>

            </div>

        </div>
        """
    )

    st.divider()

    st.markdown("### 🧠 Research Team")

    st.caption(
        "Five specialized AI agents collaborate "
        "to analyze your research question."
    )

    st.html(
        "<div style='height:8px;'></div>"
    )

    # -----------------------------------------------------
    # AGENT CARDS
    # -----------------------------------------------------

    for agent_name, description in AGENTS:

        status = st.session_state.agent_status.get(
            agent_name,
            "waiting",
        )

        if status == "active":

            icon = "🟢"
            status_text = "Working"
            status_color = "#818cf8"

        elif status == "done":

            icon = "✅"
            status_text = "Complete"
            status_color = "#86efac"

        else:

            icon = "○"
            status_text = "Waiting"
            status_color = "#818cf8"

        # IMPORTANT:
        # Use st.html(), NOT st.markdown(),
        # for custom HTML.

        st.html(
            f"""
            <div
                style="
                    padding:10px 12px;
                    margin-bottom:8px;
                    border-radius:12px;
                    background:
                        rgba(15,23,42,0.65);
                    border:
                        1px solid
                        rgba(148,163,184,0.10);
                "
            >

                <div
                    style="
                        color:#e2e8f0;
                        font-size:13px;
                        font-weight:700;
                    "
                >
                    {icon}
                    &nbsp;&nbsp;
                    {agent_name}
                </div>

                <div
                    style="
                        color:#64748b;
                        font-size:11px;
                        margin-top:3px;
                    "
                >
                    {description}
                </div>

                <div
                    style="
                        color:{status_color};
                        font-size:10px;
                        margin-top:5px;
                    "
                >
                    {status_text}
                </div>

            </div>
            """
        )

    st.divider()

    # -----------------------------------------------------
    # PIPELINE INFO
    # -----------------------------------------------------

    st.markdown("### ⚙️ Pipeline")

    st.caption(
        "Research tools are executed once per question "
        "to keep API usage controlled."
    )

    st.html(
        """
        <div
            style="
                height:8px;
            "
        ></div>

        <div
            style="
                color:#64748b;
                font-size:11px;
                line-height:1.6;
            "
        >

            <b
                style="
                    color:#94a3b8;
                "
            >
                Model
            </b>

            <br>

            GPT-OSS 120B via Groq

            <br><br>

            <b
                style="
                    color:#94a3b8;
                "
            >
                Academic source
            </b>

            <br>

            Crossref

            <br><br>

            <b
                style="
                    color:#94a3b8;
                "
            >
                Web source
            </b>

            <br>

            Wikipedia API

        </div>
        """
    )


# =========================================================
# HERO
# =========================================================

st.html(
    """
    <div
        style="
            padding:1.8rem 0 1.2rem 0;
        "
    >

        <div
            style="
                display:inline-flex;
                align-items:center;
                gap:7px;
                padding:6px 11px;
                border-radius:999px;
                background:
                    rgba(99,102,241,0.10);
                border:
                    1px solid
                    rgba(129,140,248,0.22);
                color:#a5b4fc;
                font-size:11px;
                font-weight:700;
                letter-spacing:0.08em;
                text-transform:uppercase;
            "
        >
            ✦ AI Research Workspace
        </div>

        <h1
            style="
                margin:16px 0 7px 0;
                color:#f8fafc;
                font-size:3.1rem;
                line-height:1.05;
                font-weight:850;
                letter-spacing:-0.04em;
            "
        >

            Research deeper.

            <br>

            <span
                style="
                    background:
                        linear-gradient(
                            90deg,
                            #818cf8,
                            #c084fc
                        );
                    -webkit-background-clip:text;
                    -webkit-text-fill-color:transparent;
                "
            >
                Think critically.
            </span>

        </h1>

        <p
            style="
                color:#858da0;
                font-size:0.95rem;
                max-width:680px;
                line-height:1.6;
                margin-top:12px;
            "
        >
            Ask a research question and let a specialized
            multi-agent team plan, investigate, critique,
            and synthesize the evidence.
        </p>

    </div>
    """
)


# =========================================================
# QUESTION INPUT
# =========================================================

st.markdown("### 🔎 Research Question")

question = st.text_area(
    label="Research question",
    value=st.session_state.research_question,
    height=130,
    placeholder=(
        "Example: What is the current role of "
        "artificial intelligence in pharmaceutical "
        "quality control?"
    ),
    label_visibility="collapsed",
)

question = question.strip()

st.caption(
    "Tip: Ask a focused question for a more useful research report."
)


# =========================================================
# EXAMPLES
# =========================================================

with st.expander("💡 Example research questions"):

    examples = [

        "What is the current role of artificial intelligence in pharmaceutical quality control?",

        "How is machine learning being used in pharmaceutical drug discovery?",

        "What are the major applications of AI in pharmacovigilance?",

        "What are the challenges of implementing AI in pharmaceutical manufacturing?",

        "How can AI improve quality assurance in pharmaceutical production?",

    ]

    for example in examples:

        if st.button(
            example,
            key=f"example_{example}",
            use_container_width=True,
        ):

            st.session_state.research_question = example

            st.rerun()


st.html(
    "<div style='height:8px;'></div>"
)


# =========================================================
# START BUTTON
# =========================================================

start_research = st.button(
    "🚀 Start Research",
    type="primary",
    use_container_width=True,
    disabled=st.session_state.research_running,
)


# =========================================================
# PIPELINE DISPLAY
# =========================================================

pipeline_placeholder = st.empty()


def render_pipeline():

    cards = []

    for name, description in AGENTS:

        status = st.session_state.agent_status.get(
            name,
            "waiting",
        )

        if status == "active":

            border = "rgba(129,140,248,0.55)"
            background = "rgba(79,70,229,0.13)"
            icon = "🟢"
            status_text = "ACTIVE"

        elif status == "done":

            border = "rgba(74,222,128,0.30)"
            background = "rgba(34,197,94,0.07)"
            icon = "✓"
            status_text = "DONE"

        else:

            border = "rgba(148,163,184,0.10)"
            background = "rgba(15,23,42,0.50)"
            icon = "○"
            status_text = "WAITING"

        message = st.session_state.agent_messages.get(
            name,
            description,
        )

        cards.append(
            f"""
            <div
                style="
                    flex:1;
                    min-width:170px;
                    padding:16px;
                    border-radius:16px;
                    background:{background};
                    border:1px solid {border};
                    margin-bottom:10px;
                "
            >

                <div
                    style="
                        display:flex;
                        justify-content:space-between;
                        align-items:center;
                        gap:8px;
                    "
                >

                    <div
                        style="
                            color:#f1f5f9;
                            font-size:13px;
                            font-weight:750;
                        "
                    >
                        {icon}
                        &nbsp;
                        {name}
                    </div>

                    <div
                        style="
                            color:#818cf8;
                            font-size:9px;
                            font-weight:800;
                            letter-spacing:0.06em;
                        "
                    >
                        {status_text}
                    </div>

                </div>

                <div
                    style="
                        color:#7f8aa3;
                        font-size:11px;
                        line-height:1.5;
                        margin-top:8px;
                    "
                >
                    {message}
                </div>

            </div>
            """
        )

    html = f"""
    <div
        style="
            margin:1.5rem 0 1rem 0;
        "
    >

        <div
            style="
                color:#94a3b8;
                font-size:11px;
                font-weight:800;
                text-transform:uppercase;
                letter-spacing:0.12em;
                margin-bottom:10px;
            "
        >
            Research Pipeline
        </div>

        <div
            style="
                display:flex;
                flex-wrap:wrap;
                gap:10px;
            "
        >
            {''.join(cards)}
        </div>

    </div>
    """

    pipeline_placeholder.html(html)


render_pipeline()


# =========================================================
# RUN RESEARCH
# =========================================================

if start_research:

    if not question:

        st.warning(
            "Please enter a research question first."
        )

        st.stop()

    st.session_state.research_question = question

    st.session_state.research_result = None

    st.session_state.research_running = True

    for agent_name, _ in AGENTS:

        st.session_state.agent_status[
            agent_name
        ] = "waiting"

    st.session_state.agent_messages = {}

    render_pipeline()

    current_placeholder = st.empty()

    try:

        # -------------------------------------------------
        # ACADEMIC SEARCH
        # -------------------------------------------------

        current_placeholder.info(
            "🔎 Searching academic literature..."
        )

        academic_tool = AcademicSearchTool()

        academic_sources = academic_tool._run(
            question
        )

        academic_sources = str(
            academic_sources
        )[:3500]


        # -------------------------------------------------
        # WEB SEARCH
        # -------------------------------------------------

        current_placeholder.info(
            "🌐 Gathering broader web research..."
        )

        web_tool = WebResearchTool()

        web_sources = web_tool._run(
            question
        )

        web_sources = str(
            web_sources
        )[:3000]


        # -------------------------------------------------
        # CREWAI
        # -------------------------------------------------

        current_placeholder.info(
            "🧠 Starting the multi-agent research team..."
        )

        crew = build_research_crew(
            status_callback=update_agent
        )

        render_pipeline()


        result = crew.kickoff(
            inputs={
                "question": question,
                "academic_sources": academic_sources,
                "web_sources": web_sources,
            }
        )


        # -------------------------------------------------
        # FINAL RESULT
        # -------------------------------------------------

        if hasattr(result, "raw"):

            final_report = result.raw

        else:

            final_report = str(result)


        final_report = final_report.strip()


        if not final_report:

            raise ValueError(
                "The research team returned an empty report."
            )


        for agent_name, _ in AGENTS:

            st.session_state.agent_status[
                agent_name
            ] = "done"


        st.session_state.research_result = final_report

        st.session_state.research_running = False

        current_placeholder.empty()

        render_pipeline()


    except Exception as e:

        st.session_state.research_running = False

        current_placeholder.empty()

        st.error(
            "The research team could not complete the request."
        )

        with st.expander(
            "🔧 Technical details",
            expanded=True,
        ):

            st.exception(e)

        st.info(
            "If this error is related to Groq token limits, "
            "the research pipeline may need additional context compression."
        )


# =========================================================
# FINAL REPORT
# =========================================================

if st.session_state.research_result:

    st.html(
        """
        <div
            style="
                display:flex;
                align-items:center;
                justify-content:space-between;
                gap:12px;
                margin-top:2rem;
                margin-bottom:0.5rem;
            "
        >

            <div>

                <div
                    style="
                        color:#94a3b8;
                        font-size:10px;
                        font-weight:800;
                        text-transform:uppercase;
                        letter-spacing:0.12em;
                    "
                >
                    Research Complete
                </div>

                <div
                    style="
                        color:#f8fafc;
                        font-size:25px;
                        font-weight:800;
                        margin-top:4px;
                    "
                >
                    Research Report
                </div>

            </div>

            <div
                style="
                    padding:6px 10px;
                    border-radius:999px;
                    color:#86efac;
                    background:
                        rgba(34,197,94,0.08);
                    border:
                        1px solid
                        rgba(74,222,128,0.18);
                    font-size:10px;
                    font-weight:800;
                "
            >
                ✓ COMPLETE
            </div>

        </div>
        """
    )


    # Report background
    st.html(
        """
        <div
            style="
                background:
                    rgba(15,23,42,0.58);
                border:
                    1px solid
                    rgba(148,163,184,0.12);
                border-radius:20px;
                padding:2rem;
                margin-top:1.2rem;
                margin-bottom:1rem;
                box-shadow:
                    0 20px 60px
                    rgba(0,0,0,0.18);
            "
        >
        """
    )

    # Actual Markdown report
    st.markdown(
        st.session_state.research_result
    )

    # Close report background
    st.html(
        """
        </div>
        """
    )


# =========================================================
# FOOTER
# =========================================================

st.html(
    """
    <div
        style="
            text-align:center;
            padding:2rem 0 1rem 0;
            color:#475569;
            font-size:10px;
        "
    >
        ResearchLab AI · CrewAI × Groq × Streamlit
    </div>
    """
)
