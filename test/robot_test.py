import asyncio
import json
import websockets


# =====================================================
# CONFIGURACIÓN
# =====================================================

ROBOT_HOST = "192.168.100.23"
ROBOT_PORT = 81


# =====================================================
# MOVER SERVO
# =====================================================

async def move_servo(ws, angle):

    if not 0 <= angle <= 180:
        print("❌ El ángulo debe estar entre 0 y 180")
        return

    command = {
        "cmd": "servo",
        "angle": angle
    }

    await ws.send(json.dumps(command))

    response = await ws.recv()

    print("ESP32:", response)


# =====================================================
# PROGRAMA PRINCIPAL
# =====================================================

async def main():

    uri = f"ws://{ROBOT_HOST}:{ROBOT_PORT}"

    print("====================================")
    print("        ROBOT ESP32 TEST")
    print("====================================")
    print()
    print(f"Conectando a {uri}...")

    try:

        async with websockets.connect(uri) as ws:

            print("✅ Conectado al ESP32")
            print()
            print("Escribe un ángulo entre 0 y 180.")
            print("Escribe 'q' para salir.")
            print()

            while True:

                entrada = input("Ángulo: ")

                if entrada.lower() == "q":
                    break

                try:
                    angle = int(entrada)
                except ValueError:
                    print("❌ Escribe un número.")
                    continue

                await move_servo(ws, angle)

                print()

    except Exception as e:

        print()
        print("❌ No se pudo conectar al ESP32.")
        print()
        print("Error:", e)


# =====================================================
# INICIAR
# =====================================================

asyncio.run(main())