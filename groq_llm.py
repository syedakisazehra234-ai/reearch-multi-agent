import os
from typing import Any

from groq import Groq
from pydantic import PrivateAttr
from crewai import BaseLLM


class GroqLLM(BaseLLM):
    """
    CrewAI-compatible Groq LLM.

    Uses Groq's native OpenAI-compatible tool calling so that
    CrewAI agents can reliably execute research tools.
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
                "Add it under Streamlit Secrets."
            )

        super().__init__(
            model=model,
            temperature=temperature,
        )

        self._client = Groq(api_key=api_key)

    @staticmethod
    def _clean_message(message: Any) -> dict:
        """
        Remove CrewAI-only metadata that Groq does not accept.
        Preserve native tool-call fields.
        """

        if not isinstance(message, dict):
            return {
                "role": "user",
                "content": str(message),
            }

        cleaned = {}

        for key, value in message.items():

            # CrewAI internal metadata that should not be
            # sent directly to Groq.
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
    ):
        """
        Send a request to Groq.

        When CrewAI supplies tools, they are forwarded to Groq's
        native tool-calling API.

        CrewAI expects native tool calls to be returned as a list.
        """

        # ---------------------------------------------------------
        # 1. Normalize messages
        # ---------------------------------------------------------

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

        # ---------------------------------------------------------
        # 2. Build request
        # ---------------------------------------------------------

        request = {
            "model": self.model,
            "messages": groq_messages,
            "temperature": (
                self.temperature
                if self.temperature is not None
                else 0.2
            ),
            "max_tokens": 6000,
        }

        # ---------------------------------------------------------
        # 3. Native tool calling
        # ---------------------------------------------------------

        if tools:
            request["tools"] = tools
            request["tool_choice"] = "auto"

        # ---------------------------------------------------------
        # 4. Call Groq
        # ---------------------------------------------------------

        completion = self._client.chat.completions.create(
            **request
        )

        message = completion.choices[0].message

        # ---------------------------------------------------------
        # 5. If Groq requested tools, return the tool calls
        #    directly to CrewAI.
        # ---------------------------------------------------------

        if getattr(message, "tool_calls", None):

            return list(message.tool_calls)

        # ---------------------------------------------------------
        # 6. Otherwise return normal text
        # ---------------------------------------------------------

        return message.content or ""

    def supports_function_calling(self) -> bool:
        """
        Tell CrewAI that this LLM supports native function calling.
        """

        return True

    def supports_stop_words(self) -> bool:
        """
        Groq can handle generation without CrewAI stop-word
        manipulation, so keep this disabled.
        """

        return False
