"""
Prueba directa: manda un comando de moverse por cm al robot.

Uso:
    python test/test_move.py                # por defecto: 20 cm adelante
    python test/test_move.py 30             # 30 cm adelante
    python test/test_move.py 15 backward    # 15 cm hacia atrás
"""

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

from hardware.motors import move_forward_cm, move_backward_cm


async def main():

    distance = 20.0
    direction = "forward"

    if len(sys.argv) >= 2:
        distance = float(sys.argv[1])

    if len(sys.argv) >= 3:
        direction = sys.argv[2].lower()

    print()
    print("==============================")
    print("     PRUEBA DE MOVIMIENTO")
    print("==============================")
    print(f"Dirección: {direction}")
    print(f"Distancia: {distance} cm")
    print()

    try:

        if direction == "forward":
            response = await move_forward_cm(distance)
        elif direction == "backward":
            response = await move_backward_cm(distance)
        else:
            print(f"❌ Dirección desconocida: {direction}")
            return

        print("✅ Respuesta del ESP32:")
        print(response)

    except Exception as e:
        print(f"❌ Error: {e}")


asyncio.run(main())
