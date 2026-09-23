from hardware.esp32 import send_command


# =====================================================
# CALIBRACIÓN DE GIRO
# =====================================================
# Tiempo aproximado (ms) que tarda el robot en girar 90° en el sitio.
# Ajústalo después de probarlo físicamente.
MS_PER_90_DEG = 500


async def move_forward_cm(distance_cm: float):
    """
    Mueve el robot hacia adelante `distance_cm` centímetros.
    Bloquea hasta que el ESP32 reporte que terminó (o timeout).
    """

    if distance_cm <= 0:
        raise ValueError("La distancia debe ser mayor que 0")

    # Timeout holgado: 1 segundo por cm más un margen fijo.
    timeout = max(15.0, distance_cm * 1.0 + 5.0)

    return await send_command(
        {
            "cmd": "move_cm",
            "direction": "forward",
            "distance": distance_cm
        },
        timeout=timeout
    )


async def move_backward_cm(distance_cm: float):
    """
    Mueve el robot hacia atrás `distance_cm` centímetros.
    """

    if distance_cm <= 0:
        raise ValueError("La distancia debe ser mayor que 0")

    timeout = max(15.0, distance_cm * 1.0 + 5.0)

    return await send_command(
        {
            "cmd": "move_cm",
            "direction": "backward",
            "distance": distance_cm
        },
        timeout=timeout
    )


async def turn_ms(direction: str, ms: int):
    """
    Rota el robot en el sitio durante `ms` milisegundos.
    direction: "left" o "right".
    """

    if direction not in ("left", "right"):
        raise ValueError("direction debe ser 'left' o 'right'")

    if ms <= 0:
        raise ValueError("ms debe ser mayor que 0")

    timeout = max(10.0, (ms / 1000.0) + 5.0)

    return await send_command(
        {
            "cmd": "turn",
            "direction": direction,
            "ms": int(ms)
        },
        timeout=timeout
    )


async def turn_degrees(direction: str, degrees: float):
    """
    Rota el robot aproximadamente `degrees` grados en el sitio.
    La precisión depende de que `MS_PER_90_DEG` esté bien calibrado.
    """

    if degrees <= 0:
        raise ValueError("degrees debe ser mayor que 0")

    ms = int(degrees / 90.0 * MS_PER_90_DEG)

    if ms <= 0:
        ms = 1

    return await turn_ms(direction, ms)


async def stop():

    return await send_command({
        "cmd": "stop"
    })
