"""
Prueba directa del comportamiento de seguimiento, sin pasar por el LLM.

Uso:
    python test/test_follow.py                    # valores por defecto
    python test/test_follow.py 30 20 80 10        # iters min_dist max_dist step_cm
"""

import sys
import os
import json
import asyncio

sys.path.append(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)

from perception.follower import follow_target


async def main():

    max_iterations = 20
    min_distance = 25.0
    max_distance = 100.0
    step_cm = 10.0

    if len(sys.argv) >= 2:
        max_iterations = int(sys.argv[1])
    if len(sys.argv) >= 3:
        min_distance = float(sys.argv[2])
    if len(sys.argv) >= 4:
        max_distance = float(sys.argv[3])
    if len(sys.argv) >= 5:
        step_cm = float(sys.argv[4])

    print()
    print("==============================")
    print("     SEGUIMIENTO DEL ROBOT")
    print("==============================")
    print(f"max_iterations: {max_iterations}")
    print(f"min_distance:   {min_distance}")
    print(f"max_distance:   {max_distance}")
    print(f"step_cm:        {step_cm}")
    print()

    result = await follow_target(
        max_iterations=max_iterations,
        min_distance=min_distance,
        max_distance=max_distance,
        step_cm=step_cm,
    )

    print()
    print("===== RESUMEN =====")
    print(json.dumps(result["summary"], indent=2))
    print()
    print("===== LOG =====")
    for entry in result["log"]:
        print(entry)


asyncio.run(main())
