import json
import websockets

from config import ESP32_HOST, ESP32_PORT


async def read_distance():

    uri = f"ws://{ESP32_HOST}:{ESP32_PORT}"

    async with websockets.connect(uri) as ws:

        command = {
            "cmd": "distance"
        }

        await ws.send(json.dumps(command))

        response = await ws.recv()

        #print("DEBUG RESPONSE:", repr(response))

        data = json.loads(response)

        #print("DEBUG DATA:", data)
        #print("DEBUG DISTANCE:", data["distance"])
        #print("DEBUG TYPE:", type(data["distance"]))

        return data["distance"]


async def move_servo(angle: int):

    if not 0 <= angle <= 180:
        raise ValueError("El ángulo debe estar entre 0 y 180")

    uri = f"ws://{ESP32_HOST}:{ESP32_PORT}"

    async with websockets.connect(uri) as ws:

        command = {
            "cmd": "servo",
            "angle": angle
        }

        await ws.send(json.dumps(command))

        response = await ws.recv()

        return response