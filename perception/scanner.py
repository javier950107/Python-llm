import asyncio

from hardware.esp32 import move_servo, read_distance


MIN_SAFE_DISTANCE = 30


async def scan_environment():

    angles = list(range(0, 181, 10))

    results = []

    for angle in angles:

        print(f"Escaneando {angle}°...")

        await move_servo(angle)

        await asyncio.sleep(0.2)

        distance = await read_distance()

        results.append({
            "angle": angle,
            "distance": distance
        })

        print(f"  → {distance} cm")

    # Buscar la dirección con mayor distancia
    safe_results = [
        result
        for result in results
        if result["distance"] >= MIN_SAFE_DISTANCE
    ]

    if safe_results:

        safest = max(
            safe_results,
            key=lambda result: result["distance"]
        )

        safest_angle = safest["angle"]
        safest_distance = safest["distance"]

    else:

        safest_angle = None
        safest_distance = None

    return {
        "measurements": results,
        "safest_angle": safest_angle,
        "safest_distance": safest_distance,
        "minimum_safe_distance": MIN_SAFE_DISTANCE
    }