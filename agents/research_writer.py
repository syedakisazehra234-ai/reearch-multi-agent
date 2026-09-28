from crewai import Agent


def create_research_writer(llm, status_callback=None):

    def callback(_step):
        if status_callback:
            status_callback(
                "Research Writer",
                "Synthesizing the evidence into the final research report."
            )

    return Agent(
        role="Senior Research Report Writer",

        goal=(
            "Produce a clear, structured and evidence-aware research "
            "report using only the research material supplied by the "
            "other agents."
        ),

        backstory=(
            "You are a professional research writer. "
            "You never invent citations, studies, statistics or URLs. "
            "You clearly distinguish established findings from "
            "limitations and research gaps."
        ),

        llm=llm,

        tools=[],

        allow_delegation=False,

        verbose=False,

        max_iter=1,

        step_callback=callback,
    )
