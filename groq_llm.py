import os
from typing import Any

from groq import Groq
from pydantic import PrivateAttr
from crewai import BaseLLM


class GroqLLM(BaseLLM):

    _client: Groq = PrivateAttr()

    MAX_INPUT_CHARS = 7000
    MAX_OUTPUT_TOKENS = 500

    def __init__(
        self,
        model="openai/gpt-oss-120b",
        temperature=0.1,
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
    def _clean_message(message: Any):

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

    def _compact_messages(self, messages):

        cleaned = [
            self._clean_message(message)
            for message in messages
        ]

        total = sum(
            len(str(m.get("content", "")))
            for m in cleaned
        )

        if total <= self.MAX_INPUT_CHARS:
            return cleaned

        system_messages = [
            m for m in cleaned
            if m.get("role") == "system"
        ]

        other_messages = [
            m for m in cleaned
            if m.get("role") != "system"
        ]

        system_size = sum(
            len(str(m.get("content", "")))
            for m in system_messages
        )

        remaining = max(
            2500,
            self.MAX_INPUT_CHARS - system_size
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

            else:

                if remaining > 500:

                    shortened = dict(message)

                    shortened["content"] = (
                        content[:remaining]
                        + "\n[Context shortened.]"
                    )

                    selected.insert(
                        0,
                        shortened
                    )

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

        # We intentionally do NOT pass CrewAI tools here.
        # Research tools are executed once directly in app.py.
        #
        # This prevents repeated tool-calling requests from
        # exceeding the current Groq TPM limit.

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

    def supports_function_calling(self):

        return False

    def supports_stop_words(self):

        return False
