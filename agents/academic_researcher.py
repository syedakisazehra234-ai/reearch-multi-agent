from crewai import Agent


def create_academic_researcher(
    llm,
    academic_tool=None,
    status_callback=None,
):

    def callback(_step):

        if status_callback:

            status_callback(
                "Academic Researcher",
                "Analyzing scholarly evidence."
            )

    return Agent(
        role="Academic Research Specialist",

        goal=(
            "Analyze supplied academic literature and "
            "extract relevant evidence without inventing "
            "sources or claims."
        ),

        backstory=(
            "You are a scholarly research specialist. "
            "You carefully distinguish published evidence "
            "from unsupported claims."
        ),

        llm=llm,

        tools=[],

        allow_delegation=False,

        verbose=False,

        max_iter=1,

        step_callback=callback,
    )
