from crewai import Agent


def create_academic_researcher(
    llm,
    academic_tool,
    status_callback=None,
):

    def callback(_step):
        if status_callback:
            status_callback(
                "Academic Researcher",
                "Searching scholarly literature and extracting evidence."
            )

    return Agent(
        role="Academic Research Specialist",

        goal=(
            "Find relevant scholarly literature for the research question. "
            "Prioritize academic evidence, publication dates, authors, "
            "journals and DOI information."
        ),

        backstory=(
            "You are a scholarly research specialist. "
            "You distinguish academic evidence from unsupported claims "
            "and always preserve source information."
        ),

        llm=llm,

        tools=[academic_tool],

        allow_delegation=False,

        verbose=False,

        max_iter=5,

        step_callback=callback,
    )
