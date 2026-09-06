import sys
import os
import asyncio

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from hardware.esp32 import read_distance


async def main():

    print("Leyendo distancia...")

    response = await read_distance()

    print("ESP32:", response)


asyncio.run(main())