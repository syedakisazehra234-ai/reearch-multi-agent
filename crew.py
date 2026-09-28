from crewai import Crew, Task, Process
from groq_llm import GroqLLM

from agents.planner import create_planner
from agents.academic_researcher import create_academic_researcher
from agents.web_researcher import create_web_researcher
from agents.evidence_critic import create_evidence_critic
from agents.research_writer import create_research_writer


def build_research_crew(status_callback=None):

    # =========================================================
    # LLM
    # =========================================================

    llm = GroqLLM(
        model="openai/gpt-oss-120b",
        temperature=0.1,
    )

    # =========================================================
    # AGENTS
    # =========================================================

    planner = create_planner(
        llm,
        status_callback
    )

    academic_researcher = create_academic_researcher(
        llm,
        None,
        status_callback
    )

    web_researcher = create_web_researcher(
        llm,
        None,
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

    # =========================================================
    # TASK 1 — PLANNER
    # =========================================================

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

Do not answer the research question.

Maximum: 250 words.
""",

        expected_output="""
A concise research strategy containing:
- main objective
- focused research questions
- key concepts
- evidence requirements
- research boundaries
""",

        agent=planner,
    )

    # =========================================================
    # TASK 2 — ACADEMIC RESEARCHER
    # =========================================================

    academic_task = Task(
        description="""
Research question:

{question}

Academic source material:

{academic_sources}

Analyze ONLY the academic source material supplied above.

Produce a concise academic evidence summary.

For each useful source preserve:

- Title
- Authors
- Year
- Journal
- DOI
- Relevance

Rules:

- Do not invent sources.
- Do not invent study findings.
- Do not invent statistics.
- Do not invent citations.
- If the supplied material is insufficient, say so.

Maximum: 400 words.
""",

        expected_output="""
A concise academic evidence summary based only
on the supplied academic source material.
""",

        agent=academic_researcher,
    )

    # =========================================================
    # TASK 3 — WEB RESEARCHER
    # =========================================================

    web_task = Task(
        description="""
Research question:

{question}

Web source material:

{web_sources}

Analyze ONLY the web source material supplied above.

Produce a concise contextual summary.

For each useful source preserve:

- Title
- Summary
- URL
- Relevance

Rules:

- Do not invent sources.
- Do not invent URLs.
- Do not invent facts.
- Clearly distinguish web information from academic evidence.
- If the supplied material is insufficient, say so.

Maximum: 350 words.
""",

        expected_output="""
A concise web research summary based only
on the supplied web source material.
""",

        agent=web_researcher,
    )

    # =========================================================
    # TASK 4 — EVIDENCE CRITIC
    # =========================================================
    #
    # IMPORTANT:
    # There are NO {academic_task} or {web_task}
    # variables here.
    #
    # CrewAI receives academic_task and web_task through
    # context=[...].
    # =========================================================

    critic_task = Task(
        description="""
Research question:

{question}

Review the outputs supplied in your task context from:

1. Academic Researcher
2. Web Researcher

Critically evaluate the supplied research.

Identify:

- Strong evidence
- Weak evidence
- Unsupported claims
- Contradictions
- Missing evidence
- Limitations
- Research gaps

Rules:

- Evaluate only the information supplied in task context.
- Do not perform additional research.
- Do not introduce new facts.
- Do not invent citations.
- Do not invent statistics.
- Clearly distinguish evidence from interpretation.

Maximum: 450 words.
""",

        expected_output="""
A concise critical assessment of the academic and
web research, identifying evidence strength,
weaknesses, contradictions, limitations,
unsupported claims, and research gaps.
""",

        agent=evidence_critic,

        context=[
            academic_task,
            web_task,
        ],
    )

    # =========================================================
    # TASK 5 — RESEARCH WRITER
    # =========================================================
    #
    # IMPORTANT:
    # There is NO {critic_task} variable here.
    #
    # The critic output is provided through context.
    # =========================================================

    writing_task = Task(
        description="""
Write the final research report.

Research question:

{question}

Use the research evidence and critical assessment
provided in the task context.

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

- Do not invent facts.
- Do not invent citations.
- Do not invent statistics.
- Do not invent URLs.
- Preserve supplied DOI URLs.
- Preserve supplied web URLs.
- Distinguish evidence from interpretation.
- Mention uncertainty where appropriate.
- Do not claim evidence is stronger than the supplied
  material supports.
- Keep the report concise.

Maximum: approximately 700 words.
""",

        expected_output="""
A concise professional research report containing:
executive summary, introduction, key findings,
evidence analysis, limitations, research gaps,
conclusion, and references.
""",

        agent=research_writer,

        context=[
            critic_task,
        ],
    )

    # =========================================================
    # CREW
    # =========================================================

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
