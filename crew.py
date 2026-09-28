from crewai import Crew, Task, Process

from groq_llm import GroqLLM

from agents.planner import create_planner
from agents.academic_researcher import create_academic_researcher
from agents.web_researcher import create_web_researcher
from agents.evidence_critic import create_evidence_critic
from agents.research_writer import create_research_writer

from tools.research_tools import (
    AcademicSearchTool,
    WebResearchTool,
)


def build_research_crew(status_callback=None):

    llm = GroqLLM()

    academic_tool = AcademicSearchTool()
    web_tool = WebResearchTool()

    planner = create_planner(
        llm,
        status_callback,
    )

    academic_researcher = create_academic_researcher(
        llm,
        academic_tool,
        status_callback,
    )

    web_researcher = create_web_researcher(
        llm,
        web_tool,
        status_callback,
    )

    evidence_critic = create_evidence_critic(
        llm,
        status_callback,
    )

    research_writer = create_research_writer(
        llm,
        status_callback,
    )

    # ---------------------------------------------------------
    # TASK 1 — PLAN
    # ---------------------------------------------------------

    planning_task = Task(
        description="""
        Research question:

        {question}

        Create a rigorous research plan.

        Include:

        1. Main research objective
        2. 4-7 focused research questions
        3. Key concepts that need clarification
        4. Evidence that should be collected
        5. Important limitations or boundaries

        Do not answer the research question yet.
        """,

        expected_output=(
            "A structured research plan with objectives, subquestions, "
            "evidence requirements and boundaries."
        ),

        agent=planner,
    )

    # ---------------------------------------------------------
    # TASK 2 — ACADEMIC
    # ---------------------------------------------------------

    academic_task = Task(
        description="""
        Research question:

        {question}

        Use the Academic Literature Search tool.

        Follow the research plan from the previous agent.

        Find relevant scholarly publications.

        For every useful source preserve:

        - title
        - authors
        - year
        - journal
        - DOI

        Explain briefly why each source is relevant.

        Do not invent publications or citations.
        """,

        expected_output=(
            "A structured collection of relevant academic sources "
            "with bibliographic information and relevance notes."
        ),

        agent=academic_researcher,

        context=[planning_task],
    )

    # ---------------------------------------------------------
    # TASK 3 — WEB
    # ---------------------------------------------------------

    web_task = Task(
        description="""
        Research question:

        {question}

        Use the Web Research Search tool.

        Follow the research plan from the planner.

        Gather useful broader research context.

        Preserve:

        - source title
        - key information
        - source URL

        Clearly distinguish general web information from academic evidence.

        Do not invent URLs or sources.
        """,

        expected_output=(
            "A structured collection of useful web sources and "
            "contextual findings with URLs."
        ),

        agent=web_researcher,

        context=[planning_task],
    )

    # ---------------------------------------------------------
    # TASK 4 — CRITIC
    # ---------------------------------------------------------

    critic_task = Task(
        description="""
        Research question:

        {question}

        Critically evaluate the research produced by the academic
        researcher and web researcher.

        Identify:

        1. Strong evidence
        2. Weak evidence
        3. Unsupported claims
        4. Contradictions
        5. Missing evidence
        6. Important limitations
        7. Research gaps

        Do not add new facts that are not supported by the supplied
        research material.
        """,

        expected_output=(
            "A critical evidence assessment identifying strengths, "
            "weaknesses, contradictions, gaps and limitations."
        ),

        agent=evidence_critic,

        context=[
            academic_task,
            web_task,
        ],
    )

    # ---------------------------------------------------------
    # TASK 5 — WRITER
    # ---------------------------------------------------------

    writing_task = Task(
        description="""
        Write the final research report for:

        {question}

        Use the outputs from:

        - Research Planner
        - Academic Researcher
        - Web Researcher
        - Evidence Critic

        Structure the report as:

        # Research Report

        ## Executive Summary

        ## Introduction

        ## Key Findings

        ## Evidence Analysis

        ## Limitations

        ## Research Gaps

        ## Conclusion

        ## References

        Rules:

        - Do not invent facts.
        - Do not invent citations.
        - Do not invent URLs.
        - Preserve DOI URLs supplied by the academic researcher.
        - Preserve web URLs supplied by the web researcher.
        - Clearly distinguish evidence from interpretation.
        - Mention important uncertainty.
        - Keep the report readable and professional.
        """,

        expected_output=(
            "A complete evidence-aware research report with references."
        ),

        agent=research_writer,

        context=[
            planning_task,
            academic_task,
            web_task,
            critic_task,
        ],
    )

    crew = Crew(
        agents=[
            planner,
            academic_researcher,
            web_researcher,
            evidence_critic,
            research_writer,
        ],

        tasks=[
            planning_task,
            academic_task,
            web_task,
            critic_task,
            writing_task,
        ],

        process=Process.sequential,

        verbose=False,

        memory=False,

        cache=False,
    )

    return crew
