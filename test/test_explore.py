"""
Prueba directa del comportamiento de exploración, sin pasar por el LLM.

Uso:
    python test/test_explore.py                # valores por defecto
    python test/test_explore.py 10 20 30       # max_steps step_cm safe_distance
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

from perception.exploration import explore


async def main():

    max_steps = 8
    step_cm = 20.0
    safe_distance = 30.0

    if len(sys.argv) >= 2:
        max_steps = int(sys.argv[1])
    if len(sys.argv) >= 3:
        step_cm = float(sys.argv[2])
    if len(sys.argv) >= 4:
        safe_distance = float(sys.argv[3])

    print()
    print("==============================")
    print("     EXPLORACIÓN DEL ROBOT")
    print("==============================")
    print(f"max_steps:     {max_steps}")
    print(f"step_cm:       {step_cm}")
    print(f"safe_distance: {safe_distance}")
    print()

    result = await explore(
        max_steps=max_steps,
        step_cm=step_cm,
        safe_distance=safe_distance,
    )

    print()
    print("===== RESUMEN =====")
    print(json.dumps(result["summary"], indent=2))
    print()
    print("===== LOG =====")
    for entry in result["log"]:
        print(entry)


asyncio.run(main())
