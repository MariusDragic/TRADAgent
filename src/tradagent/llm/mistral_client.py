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

        print("Calling Mistral AI for tool execution...")
        while True:
            response = client.chat.complete(
                model=self.model,
                messages=messages,
                tools=tools,
                temperature=0.1,
            )

            msg = response.choices[0].message

            # Case 1: model wants to call tools
            if msg.tool_calls:
                print(f"Model requested {len(msg.tool_calls)} tool call(s)")
        
                messages.append({"role": "assistant", "tool_calls": msg.tool_calls})
                
                for call in msg.tool_calls:
                    fn_name = call.function.name
                    fn_args = json.loads(call.function.arguments or "{}")

                    if fn_name not in tool_handlers:
                        raise RuntimeError(f"Unknown tool: {fn_name}")

                    result = tool_handlers[fn_name](fn_args)

                    messages.append(
                        {
                            "role": "tool",
                            "tool_call_id": call.id,
                            "name": fn_name,
                            "content": result,
                        }
                    )
                continue

            # Case 2: model answered normally → break
            print("Assistant response received")
            messages.append(
                {
                    "role": "assistant",
                    "content": msg.content or "",
                }
            )
            break

        response = client.chat.complete(
            model=self.model,
            messages=messages
            + [
                {
                    "role": "user",
                    "content": "Return ONLY a JSON object matching the schema.",
                }
            ],
            response_format={"type": "json_schema", "json_schema": decision_schema},
            temperature=0.1,
        )

        content = response.choices[0].message.content
        if not content:
            raise RuntimeError("Empty decision response")

        return Decision.model_validate_json(content)

