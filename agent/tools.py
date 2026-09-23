from hardware.esp32 import move_servo
from hardware.motors import (
    move_forward_cm,
    move_backward_cm,
    turn_degrees,
    stop,
)
from perception.scanner import scan_environment
from perception.exploration import explore


async def servo_tool(angle: int):

    response = await move_servo(angle)
    return response


async def scan_tool():

    results = await scan_environment()
    return results


async def move_tool(distance_cm: float, direction: str = "forward"):

    if direction == "forward":
        return await move_forward_cm(distance_cm)

    if direction == "backward":
        return await move_backward_cm(distance_cm)

    return {"error": f"Dirección desconocida: {direction}"}


async def turn_tool(direction: str, degrees: float):

    return await turn_degrees(direction, degrees)


async def stop_tool():

    return await stop()


async def explore_tool(
    max_steps: int = 8,
    step_cm: float = 20.0,
    safe_distance: float = 30.0,
):

    return await explore(
        max_steps=max_steps,
        step_cm=step_cm,
        safe_distance=safe_distance,
    )
