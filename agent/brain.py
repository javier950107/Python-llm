import json

from openai import OpenAI

from config import (
    NOUS_API_KEY,
    NOUS_BASE_URL,
    LLM_MODEL,
)

from agent.prompts import SYSTEM_PROMPT
from agent.tools import (
    servo_tool,
    scan_tool,
    move_tool,
    turn_tool,
    stop_tool,
    explore_tool,
    follow_tool,
)


client = OpenAI(
    api_key=NOUS_API_KEY,
    base_url=NOUS_BASE_URL,
)


TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "move_servo",
            "description":
                "Mueve el servo del sensor ultrasónico a un ángulo "
                "específico (0-180). 90 apunta al frente.",
            "parameters": {
                "type": "object",
                "properties": {
                    "angle": {
                        "type": "integer",
                        "description": "Ángulo en grados (0-180)."
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
            "description":
                "Barre el servo de 0 a 180 grados tomando lecturas "
                "de distancia y devuelve el ángulo con más espacio.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "move",
            "description":
                "Mueve el robot una distancia específica en cm. "
                "La dirección puede ser 'forward' o 'backward'.",
            "parameters": {
                "type": "object",
                "properties": {
                    "distance_cm": {
                        "type": "number",
                        "description":
                            "Distancia a recorrer en cm (positiva)."
                    },
                    "direction": {
                        "type": "string",
                        "enum": ["forward", "backward"],
                        "description": "Dirección de movimiento."
                    }
                },
                "required": ["distance_cm"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "turn",
            "description":
                "Rota el robot en el sitio un número de grados.",
            "parameters": {
                "type": "object",
                "properties": {
                    "direction": {
                        "type": "string",
                        "enum": ["left", "right"]
                    },
                    "degrees": {
                        "type": "number",
                        "description": "Cuánto girar en grados."
                    }
                },
                "required": ["direction", "degrees"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "stop",
            "description": "Detiene los motores inmediatamente.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "follow_target",
            "description":
                "Sigue al objeto más cercano dentro de una ventana "
                "de distancia (por defecto entre 25 y 100 cm). "
                "Escanea el frente, gira hacia el objetivo y ajusta "
                "distancia avanzando o retrocediendo. Se detiene "
                "cuando se cumplen las iteraciones o cuando pierde "
                "al objetivo varias veces seguidas. Devuelve un log "
                "con lo que hizo.",
            "parameters": {
                "type": "object",
                "properties": {
                    "max_iterations": {
                        "type": "integer",
                        "description":
                            "Cuántas iteraciones de "
                            "escanear-girar-mover ejecutar."
                    },
                    "min_distance": {
                        "type": "number",
                        "description":
                            "Distancia mínima al objetivo (cm)."
                    },
                    "max_distance": {
                        "type": "number",
                        "description":
                            "Distancia máxima al objetivo (cm)."
                    },
                    "step_cm": {
                        "type": "number",
                        "description":
                            "Cuántos cm avanzar o retroceder por paso."
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "explore_environment",
            "description":
                "Explora el entorno de forma autónoma: avanza "
                "mientras haya espacio libre y, cuando detecta un "
                "obstáculo, escanea alrededor, elige la dirección "
                "más segura, gira hacia allá y continúa. Devuelve "
                "un log completo de cada medición y acción para "
                "que el asistente pueda resumir lo ocurrido.",
            "parameters": {
                "type": "object",
                "properties": {
                    "max_steps": {
                        "type": "integer",
                        "description":
                            "Máximo de pasos de avance o giro."
                    },
                    "step_cm": {
                        "type": "number",
                        "description":
                            "Cuántos cm avanzar por paso."
                    },
                    "safe_distance": {
                        "type": "number",
                        "description":
                            "Distancia mínima al frente (cm) "
                            "considerada segura."
                    }
                },
                "required": []
            }
        }
    }
]


# =====================================================
# DISPATCH DE HERRAMIENTAS
# =====================================================

async def _dispatch_tool(name: str, arguments: dict):

    if name == "move_servo":
        return await servo_tool(arguments["angle"])

    if name == "scan_environment":
        return await scan_tool()

    if name == "move":
        return await move_tool(
            distance_cm=arguments["distance_cm"],
            direction=arguments.get("direction", "forward"),
        )

    if name == "turn":
        return await turn_tool(
            direction=arguments["direction"],
            degrees=arguments["degrees"],
        )

    if name == "stop":
        return await stop_tool()

    if name == "explore_environment":
        return await explore_tool(
            max_steps=arguments.get("max_steps", 8),
            step_cm=arguments.get("step_cm", 20.0),
            safe_distance=arguments.get("safe_distance", 30.0),
        )

    if name == "follow_target":
        return await follow_tool(
            max_iterations=arguments.get("max_iterations", 20),
            min_distance=arguments.get("min_distance", 25.0),
            max_distance=arguments.get("max_distance", 100.0),
            step_cm=arguments.get("step_cm", 10.0),
        )

    return {"error": f"Herramienta desconocida: {name}"}


# =====================================================
# CHAT CON TOOL CALLS
# =====================================================

async def ask_llm(user_message: str):

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_message},
    ]

    response = client.chat.completions.create(
        model=LLM_MODEL,
        messages=messages,
        tools=TOOLS,
        extra_body={"tags": ["user=robot"]},
    )

    message = response.choices[0].message

    # Sin llamadas a herramientas -> respuesta directa.
    if not message.tool_calls:
        return message.content

    messages.append(message)

    for tool_call in message.tool_calls:

        tool_name = tool_call.function.name

        arguments = json.loads(
            tool_call.function.arguments or "{}"
        )

        print()
        print(f"🔧 Herramienta: {tool_name}({arguments})")

        try:
            result = await _dispatch_tool(tool_name, arguments)
        except Exception as e:
            result = {"error": str(e)}

        messages.append({
            "role": "tool",
            "tool_call_id": tool_call.id,
            "content": json.dumps(result, ensure_ascii=False, default=str),
        })

    # El LLM interpreta los resultados de las herramientas.
    final_response = client.chat.completions.create(
        model=LLM_MODEL,
        messages=messages,
        tools=TOOLS,
        extra_body={"tags": ["user=robot"]},
    )

    return final_response.choices[0].message.content
