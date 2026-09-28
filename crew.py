from crewai import Crew, Task, Process
from groq_llm import GroqLLM

from agents.planner import create_planner
from agents.academic_researcher import create_academic_researcher
from agents.web_researcher import create_web_researcher
from agents.evidence_critic import create_evidence_critic
from agents.research_writer import create_research_writer


def build_research_crew(status_callback=None):

    # ---------------------------------------------------------
    # LLM
    # ---------------------------------------------------------

    llm = GroqLLM(
        model="openai/gpt-oss-120b",
        temperature=0.1,
    )

    # ---------------------------------------------------------
    # AGENTS
    # ---------------------------------------------------------

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

    # ---------------------------------------------------------
    # TASK 1 — RESEARCH PLANNER
    # ---------------------------------------------------------

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
        expected_output=(
            "A concise research strategy containing the "
            "objective, focused questions, concepts, "
            "evidence requirements, and boundaries."
        ),
        agent=planner,
    )

    # ---------------------------------------------------------
    # TASK 2 — ACADEMIC RESEARCH
    # ---------------------------------------------------------

    academic_task = Task(
        description="""
Research question:

{question}

Academic source material:

{academic_sources}

Analyze the supplied academic source material.

Produce a concise evidence summary.

For each useful source preserve:

- Title
- Authors
- Year
- Journal
- DOI
- Relevance to the research question

Important rules:

- Use ONLY the supplied academic source material.
- Never invent sources.
- Never invent study findings.
- Never invent statistics.
- If the supplied material is insufficient, explicitly say so.

Maximum: 400 words.
""",
        expected_output=(
            "A concise academic evidence summary based only "
            "on the supplied academic sources."
        ),
        agent=academic_researcher,
    )

    # ---------------------------------------------------------
    # TASK 3 — WEB RESEARCH
    # ---------------------------------------------------------

    web_task = Task(
        description="""
Research question:

{question}

Web source material:

{web_sources}

Analyze the supplied web source material.

Produce a concise contextual summary.

For each useful source preserve:

- Title
- Summary
- URL
- Relevance to the research question

Important rules:

- Use ONLY the supplied web source material.
- Never invent sources.
- Never invent URLs.
- Clearly distinguish general web information
  from academic evidence.
- If the supplied material is insufficient, explicitly say so.

Maximum: 350 words.
""",
        expected_output=(
            "A concise web research summary based only "
            "on the supplied web sources."
        ),
        agent=web_researcher,
    )

    # ---------------------------------------------------------
    # TASK 4 — EVIDENCE CRITIC
    #
    # IMPORTANT:
    # Do NOT use {academic_task} or {web_task}.
    # Their outputs are supplied through context=[...].
    # ---------------------------------------------------------

    critic_task = Task(
        description="""
Research question:

{question}

You have been provided with two research outputs
through task context:

1. Academic Researcher output
2. Web Researcher output

Critically evaluate those supplied outputs.

Identify:

- Strong evidence
- Weak evidence
- Unsupported claims
- Contradictions
- Missing evidence
- Limitations
- Research gaps

Important rules:

- Evaluate ONLY the evidence provided in the task context.
- Do not add new facts.
- Do not perform additional research.
- Do not invent citations.
- Do not assume that a claim is true merely because it
  appears in a source.
- Clearly distinguish evidence from interpretation.

Maximum: 450 words.
""",
        expected_output=(
            "A concise critical assessment of the academic "
            "and web evidence, including strengths, weaknesses, "
            "contradictions, limitations, and research gaps."
        ),
        agent=evidence_critic,

        # CrewAI passes the previous task outputs here.
        context=[
            academic_task,
            web_task,
        ],
    )

    # ---------------------------------------------------------
    # TASK 5 — RESEARCH WRITER
    #
    # IMPORTANT:
    # Do NOT use {critic_task}.
    # Its output is supplied through context=[critic_task].
    # ---------------------------------------------------------

    writing_task = Task(
        description="""
Write the final research report.

Research question:

{question}

You have been provided with the Evidence Critic's
assessment through task context.

Use that assessment together with the evidence contained
in the preceding task context to produce a concise,
professional research report.

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
- Do not claim that evidence is stronger than the supplied
  material supports.
- Keep the report concise.

Maximum: approximately 700 words.
""",
        expected_output=(
            "A concise professional research report with "
            "executive summary, introduction, key findings, "
            "evidence analysis, limitations, research gaps, "
            "conclusion, and references."
        ),
        agent=research_writer,

        # CrewAI passes the critic output here.
        context=[
            critic_task,
        ],
    )

    # ---------------------------------------------------------
    # CREW
    # ---------------------------------------------------------

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
