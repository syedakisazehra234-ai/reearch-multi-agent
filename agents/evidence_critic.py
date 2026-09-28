from crewai import Agent


def create_evidence_critic(llm, status_callback=None):

    def callback(_step):
        if status_callback:
            status_callback(
                "Evidence Critic",
                "Checking source quality, contradictions and unsupported claims."
            )

    return Agent(
        role="Evidence Quality Critic",

        goal=(
            "Critically evaluate the collected research. "
            "Identify weak evidence, contradictions, unsupported claims, "
            "missing evidence and important limitations."
        ),

        backstory=(
            "You are a skeptical research reviewer. "
            "Your job is not to make the report sound impressive. "
            "Your job is to identify where the evidence is strong, "
            "weak, incomplete or contradictory."
        ),

        llm=llm,

        tools=[],

        allow_delegation=False,

        verbose=False,

        max_iter=4,

        step_callback=callback,
    )
