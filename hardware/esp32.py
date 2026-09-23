import json
import asyncio
import websockets

from config import ESP32_HOST, ESP32_PORT


# =====================================================
# COMANDO WEBSOCKET DE BAJO NIVEL
# =====================================================

async def send_command(command: dict, timeout: float = 15.0):
    """
    Envía un comando al ESP32 y espera su respuesta en JSON.

    El `timeout` es amplio porque un `move_cm` puede tener al ESP32
    ocupado varios segundos mientras el robot se mueve físicamente.
    """

    uri = f"ws://{ESP32_HOST}:{ESP32_PORT}"

    async with websockets.connect(uri) as ws:

        await ws.send(json.dumps(command))

        raw_response = await asyncio.wait_for(
            ws.recv(),
            timeout=timeout
        )

        response = json.loads(raw_response)

        if not response.get("ok", False):
            error = response.get("error", "unknown_error")
            raise RuntimeError(
                f"El ESP32 rechazó el comando "
                f"{command.get('cmd')}: {error}"
            )

        return response


# =====================================================
# DISTANCIA (ULTRASÓNICO)
# =====================================================

async def read_distance():

    response = await send_command({
        "cmd": "distance"
    })

    return response["distance"]


# =====================================================
# SERVO
# =====================================================

async def move_servo(angle: int):

    if not 0 <= angle <= 180:
        raise ValueError(
            "El ángulo debe estar entre 0 y 180"
        )

    return await send_command({
        "cmd": "servo",
        "angle": angle
    })


# =====================================================
# ESCANEO DE RANGO (RÁPIDO)
# =====================================================

async def scan_range(start: int = 0, end: int = 180, step: int = 10):
    """
    Pide al ESP32 que barra el servo del ángulo `start` al `end` con
    incremento `step` y devuelve todas las mediciones en una sola
    respuesta. Mucho más rápido que hacer scan desde el cliente.
    """

    # Timeout aproximado: 0.2 s por punto medido + margen.
    puntos = max(1, (abs(end - start) // max(1, step)) + 1)
    timeout = max(10.0, puntos * 0.3 + 3.0)

    response = await send_command(
        {
            "cmd": "scan_range",
            "start": int(start),
            "end": int(end),
            "step": int(step),
        },
        timeout=timeout,
    )

    return response["measurements"]


# =====================================================
# STOP
# =====================================================

async def stop_motors():

    return await send_command({
        "cmd": "stop"
    })
