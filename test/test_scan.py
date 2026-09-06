import sys
import os
import asyncio

sys.path.append(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)

from perception.scanner import scan_environment


async def main():

    print()
    print("==============================")
    print("     ESCANEO DEL ROBOT")
    print("==============================")
    print()

    results = await scan_environment()

    print()
    print("===== RESULTADO =====")

    for result in results:

        angle = result["angle"]
        distance = result["distance"]

        print(
            f"{angle}° → {distance} cm"
        )


asyncio.run(main())