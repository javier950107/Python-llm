import json

from openai import OpenAI

from config import (
    NOUS_API_KEY,
    NOUS_BASE_URL,
    LLM_MODEL
)

from agent.prompts import SYSTEM_PROMPT
from agent.tools import servo_tool, scan_tool


client = OpenAI(
    api_key=NOUS_API_KEY,
    base_url=NOUS_BASE_URL
)


TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "move_servo",
            "description": "Mueve el servo del robot a un ángulo específico.",
            "parameters": {
                "type": "object",
                "properties": {
                    "angle": {
                        "type": "integer",
                        "description": "Ángulo del servo entre 0 y 180 grados."
                    }
                },
                "required": ["angle"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "scan_environment",
            "description": "Escanea el entorno del robot moviendo el servo y midiendo distancias con el sensor ultrasónico.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    }
]


async def ask_llm(user_message: str):

    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT
        },
        {
            "role": "user",
            "content": user_message
        }
    ]

    response = client.chat.completions.create(
        model=LLM_MODEL,
        messages=messages,
        tools=TOOLS,
        extra_body={
            "tags": ["user=robot"]
        }
    )

    message = response.choices[0].message

    # ========================================
    # NO HAY HERRAMIENTA
    # ========================================

    if not message.tool_calls:

        return message.content

    # ========================================
    # EJECUTAR HERRAMIENTAS
    # ========================================

    messages.append(message)

    for tool_call in message.tool_calls:

        tool_name = tool_call.function.name

        arguments = json.loads(
            tool_call.function.arguments or "{}"
        )

        # ------------------------------------
        # SERVO
        # ------------------------------------

        if tool_name == "move_servo":

            angle = arguments["angle"]

            print()
            print(
                f"🔧 Herramienta: move_servo({angle})"
            )

            result = await servo_tool(angle)

        # ------------------------------------
        # ESCÁNER
        # ------------------------------------

        elif tool_name == "scan_environment":

            print()
            print("🔎 Herramienta: scan_environment()")
            print()

            result = await scan_tool()

        else:

            result = {
                "error": "Herramienta desconocida"
            }

        # ------------------------------------
        # DEVOLVER RESULTADO A NOUS
        # ------------------------------------

        messages.append(
            {
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": json.dumps(
                    result,
                    ensure_ascii=False
                )
            }
        )

    # ========================================
    # NOUS INTERPRETA EL RESULTADO
    # ========================================

    final_response = client.chat.completions.create(
        model=LLM_MODEL,
        messages=messages,
        tools=TOOLS,
        extra_body={
            "tags": ["user=robot"]
        }
    )

    return final_response.choices[0].message.content