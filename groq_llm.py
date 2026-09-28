import os
from typing import Any

from groq import Groq
from pydantic import PrivateAttr
from crewai import BaseLLM


class GroqLLM(BaseLLM):
    """
    CrewAI-compatible Groq LLM.

    Designed for Groq's on-demand token limits by:
    - supporting native tool calling
    - removing unsupported CrewAI metadata
    - limiting request size
    - limiting output size
    - compacting oversized conversation context
    """

    _client: Groq = PrivateAttr()

    # Keep the complete request comfortably below Groq's
    # 8K TPM limit.
    MAX_INPUT_CHARS = 18000

    # Keep generated responses compact.
    MAX_OUTPUT_TOKENS = 1200

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
        Remove CrewAI-specific metadata that Groq does not accept.
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

    @classmethod
    def _compact_messages(cls, messages):
        """
        Prevent accumulated CrewAI context from becoming too large.

        We preserve:
        - system messages
        - the latest user instruction
        - recent tool information

        Older large content is shortened.
        """

        cleaned = [
            cls._clean_message(message)
            for message in messages
        ]

        # Calculate approximate character budget.
        total_chars = sum(
            len(str(message.get("content", "")))
            for message in cleaned
        )

        if total_chars <= cls.MAX_INPUT_CHARS:
            return cleaned

        # ---------------------------------------------------------
        # First pass:
        # Keep system messages intact.
        # ---------------------------------------------------------

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

        remaining_budget = max(
            4000,
            cls.MAX_INPUT_CHARS - system_chars
        )

        # ---------------------------------------------------------
        # Preserve the most recent messages first.
        # ---------------------------------------------------------

        selected = []

        for message in reversed(other_messages):

            content = str(message.get("content", ""))

            if not content:
                selected.insert(0, message)
                continue

            if len(content) <= remaining_budget:
                selected.insert(0, message)
                remaining_budget -= len(content)

            else:

                # Keep the most useful portion of a large message.
                if remaining_budget > 1000:

                    shortened = content[
                        :remaining_budget
                    ]

                    message_copy = dict(message)
                    message_copy["content"] = (
                        shortened
                        + "\n\n[Earlier content compacted "
                        "to remain within the API token limit.]"
                    )

                    selected.insert(0, message_copy)

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

            groq_messages = self._compact_messages(messages)

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
            "max_tokens": self.MAX_OUTPUT_TOKENS,
            "service_tier": "auto",
        }

        # ---------------------------------------------------------
        # 3. Native tool calling
        # ---------------------------------------------------------

        if tools:

            request["tools"] = tools
            request["tool_choice"] = "auto"

            # Avoid unnecessary parallel tool calls.
            request["parallel_tool_calls"] = False

        # ---------------------------------------------------------
        # 4. Call Groq
        # ---------------------------------------------------------

        completion = self._client.chat.completions.create(
            **request
        )

        message = completion.choices[0].message

        # ---------------------------------------------------------
        # 5. Return native tool calls
        # ---------------------------------------------------------

        if getattr(message, "tool_calls", None):

            return list(message.tool_calls)

        # ---------------------------------------------------------
        # 6. Return normal text
        # ---------------------------------------------------------

        return message.content or ""

    def supports_function_calling(self) -> bool:
        return True

    def supports_stop_words(self) -> bool:
        return False
