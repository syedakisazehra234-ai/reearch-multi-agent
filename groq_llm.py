import os
from typing import Any, ClassVar

from groq import Groq
from pydantic import PrivateAttr
from crewai import BaseLLM


class GroqLLM(BaseLLM):

    _client: Groq = PrivateAttr()

    MAX_INPUT_CHARS: ClassVar[int] = 7000
    MAX_OUTPUT_TOKENS: ClassVar[int] = 500

    def __init__(
        self,
        model: str = "openai/gpt-oss-120b",
        temperature: float = 0.1,
    ):
        api_key = os.getenv("GROQ_API_KEY")

        if not api_key:
            raise ValueError(
                "GROQ_API_KEY is missing."
            )

        super().__init__(
            model=model,
            temperature=temperature,
        )

        self._client = Groq(
            api_key=api_key
        )

    @staticmethod
    def _clean_message(message: Any) -> dict:

        if not isinstance(message, dict):
            return {
                "role": "user",
                "content": str(message),
            }

        cleaned = {}

        for key, value in message.items():

            # CrewAI may add provider-specific metadata
            # that Groq does not accept.
            if key in {
                "cache_breakpoint",
                "provider_specific_fields",
                "metadata",
            }:
                continue

            cleaned[key] = value

        return cleaned

    def _compact_messages(self, messages):

        cleaned = [
            self._clean_message(message)
            for message in messages
        ]

        total_chars = sum(
            len(str(message.get("content", "")))
            for message in cleaned
        )

        if total_chars <= self.MAX_INPUT_CHARS:
            return cleaned

        system_messages = [
            message
            for message in cleaned
            if message.get("role") == "system"
        ]

        other_messages = [
            message
            for message in cleaned
            if message.get("role") != "system"
        ]

        system_chars = sum(
            len(str(message.get("content", "")))
            for message in system_messages
        )

        remaining = max(
            1500,
            self.MAX_INPUT_CHARS - system_chars
        )

        selected = []

        for message in reversed(other_messages):

            content = str(
                message.get("content", "")
            )

            if len(content) <= remaining:

                selected.insert(
                    0,
                    message
                )

                remaining -= len(content)

            elif remaining > 500:

                shortened = dict(message)

                shortened["content"] = (
                    content[:remaining]
                    + "\n[Context shortened.]"
                )

                selected.insert(
                    0,
                    shortened
                )

                remaining = 0

                break

            else:
                break

        return system_messages + selected

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

        if isinstance(messages, str):

            groq_messages = [
                {
                    "role": "user",
                    "content": messages,
                }
            ]

        else:

            groq_messages = self._compact_messages(
                messages
            )

        request = {
            "model": self.model,
            "messages": groq_messages,
            "temperature": 0.1,
            "max_tokens": self.MAX_OUTPUT_TOKENS,
            "reasoning_effort": "low",
        }

        # Research tools are executed directly in app.py.
        # We intentionally do not send CrewAI tools to Groq.
        completion = (
            self._client
            .chat
            .completions
            .create(**request)
        )

        return (
            completion
            .choices[0]
            .message
            .content
            or ""
        )

    def supports_function_calling(self) -> bool:
        return False

    def supports_stop_words(self) -> bool:
        return False
