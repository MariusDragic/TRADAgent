from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Callable

from mistralai import Mistral

from tradagent.models import Decision


ToolHandler = Callable[[dict[str, Any]], str]


@dataclass(frozen=True)
class MistralToolCaller:
    api_key: str
    model: str

    def decide(
        self,
        system_prompt: str,
        user_payload: dict[str, Any],
        tools: list[dict[str, Any]],
        tool_handlers: dict[str, ToolHandler],
        decision_schema: dict[str, Any],
    ) -> Decision:
        client = Mistral(api_key=self.api_key)

        messages: list[dict[str, Any]] = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": json.dumps(user_payload)},
        ]

        response = client.chat.complete(
            model=self.model,
            messages=messages,
            tools=tools,
            tool_choice="required",
            temperature=0.1,
        )

        msg = response.choices[0].message
        tool_calls = getattr(msg, "tool_calls", None)
        if not tool_calls:
            raise RuntimeError("Model did not produce a tool call.")

        for call in tool_calls:
            fn_name = call.function.name
            fn_args = json.loads(call.function.arguments or "{}")
            if fn_name not in tool_handlers:
                raise RuntimeError(f"Missing tool handler for: {fn_name}")

            tool_result = tool_handlers[fn_name](fn_args)
            messages.append(
                {
                    "role": "tool",
                    "name": fn_name,
                    "content": tool_result,
                    "tool_call_id": call.id,
                }
            )

        response2 = client.chat.complete(
            model=self.model,
            messages=messages
            + [
                {
                    "role": "user",
                    "content": "Return a single JSON object that follows the provided schema.",
                }
            ],
            response_format={"type": "json_schema", "json_schema": decision_schema},
            temperature=0.1,
        )

        content = response2.choices[0].message.content
        if not content:
            raise RuntimeError("Empty decision content from model.")

        return Decision.model_validate_json(content)
