from crewai import Agent


def create_planner(llm, status_callback=None):

    def callback(_step):
        if status_callback:
            status_callback(
                "Research Planner",
                "Breaking the research question into focused objectives."
            )

    return Agent(
        role="Research Strategy Planner",

        goal=(
            "Transform the user's research question into a precise "
            "research strategy containing focused objectives, key "
            "subquestions, evidence requirements, and important "
            "research boundaries."
        ),

        backstory=(
            "You are an experienced research strategist. "
            "You do not conduct the research yourself. "
            "You design a rigorous research plan that other specialists "
            "can execute."
        ),

        llm=llm,

        tools=[],

        allow_delegation=False,

        verbose=False,

        max_iter=3,

        step_callback=callback,
    )
