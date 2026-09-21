from hardware.esp32 import send_command


async def move_forward_cm(distance_cm: float):

    if distance_cm <= 0:
        raise ValueError("La distancia debe ser mayor que 0")

    return await send_command({
        "cmd": "move_cm",
        "direction": "forward",
        "distance": distance_cm
    })


async def move_backward_cm(distance_cm: float):

    if distance_cm <= 0:
        raise ValueError("La distancia debe ser mayor que 0")

    return await send_command({
        "cmd": "move_cm",
        "direction": "backward",
        "distance": distance_cm
    })


async def stop():

    return await send_command({
        "cmd": "motor",
        "action": "stop"
    })