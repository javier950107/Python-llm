from hardware.esp32 import move_servo
from perception.scanner import scan_environment


async def servo_tool(angle: int):

    response = await move_servo(angle)

    return response


async def scan_tool():

    results = await scan_environment()

    return results