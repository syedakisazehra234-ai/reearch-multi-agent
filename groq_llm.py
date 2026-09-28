import os
from typing import Any

from groq import Groq
from pydantic import PrivateAttr
from crewai import BaseLLM


class GroqLLM(BaseLLM):
    """
    Custom CrewAI LLM using the official Groq Python SDK.

    We intentionally use BaseLLM instead of CrewAI's generic provider
    routing so the application talks directly to Groq.
    """

    _client: Groq = PrivateAttr()

    def __init__(
        self,
        model: str = "openai/gpt-oss-120b",
        temperature: float = 0.2,
    ):
        api_key = os.getenv("GROQ_API_KEY")

        if not api_key:
            raise ValueError(
                "GROQ_API_KEY is missing. "
                "Add it to Streamlit Secrets or your environment."
            )

        super().__init__(
            model=model,
            temperature=temperature,
        )

        self._client = Groq(api_key=api_key)

    @staticmethod
    def _clean_message(message: Any) -> dict:
        """
        Remove internal CrewAI metadata that should never be sent
        to the Groq API.
        """

        if not isinstance(message, dict):
            return {
                "role": "user",
                "content": str(message),
            }

        cleaned = {}

        for key, value in message.items():
            if key in {
                "cache_breakpoint",
                "provider_specific_fields",
                "metadata",
            }:
                continue

            cleaned[key] = value

        return cleaned

    def call(
        self,
        messages,
        tools=None,
        callbacks=None,
        available_functions=None,
        from_task=None,
        from_agent=None,
        response_model=None,
        **kwargs,
    ) -> str:

        if isinstance(messages, str):
            groq_messages = [
                {
                    "role": "user",
                    "content": messages,
                }
            ]
        else:
            groq_messages = [
                self._clean_message(message)
                for message in messages
            ]

        # We intentionally let CrewAI execute its tools through its
        # ReAct loop. Therefore Groq itself doesn't need native
        # function-calling schemas here.
        completion = self._client.chat.completions.create(
            model=self.model,
            messages=groq_messages,
            temperature=self.temperature or 0.2,
            max_tokens=6000,
        )

        return completion.choices[0].message.content or ""

    def supports_function_calling(self) -> bool:
        """
        False means CrewAI uses its normal tool/action loop.
        This avoids coupling the custom LLM adapter to CrewAI's
        native function-calling conversion.
        """

        return False
