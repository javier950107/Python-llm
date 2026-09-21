from hardware.esp32 import move_servo
from hardware.motors import move_forward_cm, move_backward_cm
from perception.scanner import scan_environment


async def servo_tool(angle: int):

    response = await move_servo(angle)

    return response


async def scan_tool():

    results = await scan_environment()

    return results

async def move_motor():

    results = await move_forward_cm(10)

    return results