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


def compact_text(text, max_chars=3500):

    if text is None:
        return ""

    text = str(text)

    if len(text) <= max_chars:
        return text

    return (
        text[:max_chars]
        + "\n\n[Additional source material omitted.]"
    )


def build_research_crew(status_callback=None):

    # -----------------------------------------------------
    # LLM
    # -----------------------------------------------------

    llm = GroqLLM(
        model="openai/gpt-oss-120b",
        temperature=0.1,
    )

    # -----------------------------------------------------
    # Tools
    # -----------------------------------------------------

    academic_tool = AcademicSearchTool()
    web_tool = WebResearchTool()

    # -----------------------------------------------------
    # Agents
    # -----------------------------------------------------

    planner = create_planner(
        llm,
        status_callback
    )

    academic_researcher = create_academic_researcher(
        llm,
        academic_tool,
        status_callback
    )

    web_researcher = create_web_researcher(
        llm,
        web_tool,
        status_callback
    )

    evidence_critic = create_evidence_critic(
        llm,
        status_callback
    )

    research_writer = create_research_writer(
        llm,
        status_callback
    )

    # -----------------------------------------------------
    # PLANNER
    # -----------------------------------------------------

    planning_task = Task(
        description="""
        Research question:

        {question}

        Create a concise research strategy.

        Include:

        1. Main objective
        2. Four focused research questions
        3. Key concepts
        4. Evidence requirements
        5. Important boundaries

        Do not answer the question.

        Keep the output below 300 words.
        """,

        expected_output=(
            "A concise research strategy."
        ),

        agent=planner,
    )

    # -----------------------------------------------------
    # ACADEMIC SEARCH
    # -----------------------------------------------------

    # The actual question is passed when kickoff() is called.
    # The task receives a compact academic result through
    # a placeholder supplied by the application.
    #
    # We therefore use a small helper task whose input
    # contains the question and source material.
    # -----------------------------------------------------

    academic_task = Task(
        description="""
        Research question:

        {question}

        Academic literature:

        {academic_sources}

        Summarize the academic evidence.

        For each useful source include:

        - title
        - authors when available
        - year
        - journal
        - DOI
        - relevance to the question

        Do not invent information.

        Keep the response concise.
        """,

        expected_output=(
            "A concise academic evidence summary."
        ),

        agent=academic_researcher,
    )

    # -----------------------------------------------------
    # WEB SEARCH
    # -----------------------------------------------------

    web_task = Task(
        description="""
        Research question:

        {question}

        Web research:

        {web_sources}

        Summarize useful contextual information.

        Include source URLs when supplied.

        Clearly distinguish general web information
        from academic evidence.

        Do not invent URLs or facts.

        Keep the response concise.
        """,

        expected_output=(
            "A concise web research summary."
        ),

        agent=web_researcher,
    )

    # -----------------------------------------------------
    # CRITIC
    # -----------------------------------------------------

    critic_task = Task(
        description="""
        Research question:

        {question}

        Academic evidence:

        {academic_task}

        Web evidence:

        {web_task}

        Evaluate the supplied evidence.

        Identify:

        1. Strong evidence
        2. Weak evidence
        3. Unsupported claims
        4. Contradictions
        5. Missing evidence
        6. Limitations
        7. Research gaps

        Do not introduce new facts.

        Keep the assessment concise.
        """,

        expected_output=(
            "A concise critical evidence assessment."
        ),

        agent=evidence_critic,

        context=[
            academic_task,
            web_task,
        ],
    )

    # -----------------------------------------------------
    # WRITER
    # -----------------------------------------------------

    writing_task = Task(
        description="""
        Write the final research report for:

        {question}

        Evidence assessment:

        {critic_task}

        Structure:

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

        - Use only supplied evidence.
        - Never invent citations.
        - Never invent statistics.
        - Never invent URLs.
        - Preserve supplied DOI URLs.
        - Preserve supplied web URLs.
        - Clearly distinguish evidence from interpretation.
        - State important uncertainty.
        - Keep the report professional and concise.

        Target length: approximately 700 words.
        """,

        expected_output=(
            "A professional research report with references."
        ),

        agent=research_writer,

        context=[
            critic_task,
        ],
    )

    # -----------------------------------------------------
    # CREW
    # -----------------------------------------------------

    return Crew(
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
