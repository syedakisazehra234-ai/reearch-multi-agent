from crewai import Agent


def create_web_researcher(
    llm,
    web_tool=None,
    status_callback=None,
):

    def callback(_step):

        if status_callback:

            status_callback(
                "Web Researcher",
                "Analyzing broader web research."
            )

    return Agent(
        role="Web Research Specialist",

        goal=(
            "Analyze supplied web research and extract "
            "useful contextual information without "
            "inventing sources."
        ),

        backstory=(
            "You are a digital research specialist. "
            "You distinguish general web information "
            "from academic evidence."
        ),

        llm=llm,

        tools=[],

        allow_delegation=False,

        verbose=False,

        max_iter=1,

        step_callback=callback,
    )
