from crewai import Agent


def create_web_researcher(
    llm,
    web_tool,
    status_callback=None,
):

    def callback(_step):
        if status_callback:
            status_callback(
                "Web Researcher",
                "Investigating broader web-based research context."
            )

    return Agent(
        role="Web Research Specialist",

        goal=(
            "Gather useful web-based background information related to "
            "the research question. Identify organizations, concepts, "
            "definitions and relevant source pages."
        ),

        backstory=(
            "You are a digital research specialist. "
            "You investigate broader context while clearly preserving "
            "the distinction between general web information and "
            "academic evidence."
        ),

        llm=llm,

        tools=[web_tool],

        allow_delegation=False,

        verbose=False,

        max_iter=5,

        step_callback=callback,
    )
