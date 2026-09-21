import json
import websockets

from config import ESP32_HOST, ESP32_PORT


async def send_command(command: dict):

    uri = f"ws://{ESP32_HOST}:{ESP32_PORT}"

    async with websockets.connect(uri) as ws:

        await ws.send(json.dumps(command))

        response = await ws.recv()

        return json.loads(response)


async def read_distance():

    response = await send_command({
        "cmd": "distance"
    })

    return response["distance"]


async def move_servo(angle: int):

    if not 0 <= angle <= 180:
        raise ValueError(
            "El ángulo debe estar entre 0 y 180"
        )

    return await send_command({
        "cmd": "servo",
        "angle": angle
    })