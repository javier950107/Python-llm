import asyncio

from hardware.esp32 import move_servo


async def main():

    print("Moviendo servo a 90 grados...")

    response = await move_servo(11)

    print("ESP32:", response)


asyncio.run(main())