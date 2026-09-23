"""
Comportamiento de exploración autónoma.

El robot avanza mientras haya espacio libre al frente. Si detecta un
obstáculo dentro de `safe_distance` cm, escanea el entorno, elige la
dirección con más espacio libre, gira hacia allá y continúa.

Devuelve un log completo de todo lo que vio e hizo, para que el LLM
pueda resumirle al usuario cómo le fue.
"""

import asyncio

from hardware.esp32 import move_servo, read_distance
from hardware.motors import (
    move_forward_cm,
    move_backward_cm,
    turn_degrees,
    stop,
)
from perception.scanner import scan_environment


# =====================================================
# CONSTANTES DE EXPLORACIÓN
# =====================================================

DEFAULT_MAX_STEPS = 8
DEFAULT_STEP_CM = 20.0
DEFAULT_SAFE_DISTANCE_CM = 30.0
DEFAULT_BACKUP_CM = 10.0


async def explore(
    max_steps: int = DEFAULT_MAX_STEPS,
    step_cm: float = DEFAULT_STEP_CM,
    safe_distance: float = DEFAULT_SAFE_DISTANCE_CM,
):
    """
    Corre el bucle de exploración. Devuelve un diccionario con el log
    paso a paso y un resumen que el LLM puede convertir en lenguaje
    natural.
    """

    log = []
    total_forward_cm = 0.0
    turns = 0
    reason_stopped = "max_steps_reached"

    for step_index in range(max_steps):

        # -------------------------------------------------
        # 1) Mirar al frente y medir distancia.
        # -------------------------------------------------

        await move_servo(90)
        await asyncio.sleep(0.2)

        try:
            front_distance = await read_distance()
        except Exception as e:
            log.append({
                "step": step_index,
                "action": "read_distance_error",
                "error": str(e),
            })
            reason_stopped = "sensor_error"
            break

        log.append({
            "step": step_index,
            "action": "look_forward",
            "front_distance_cm": front_distance,
        })

        # -------------------------------------------------
        # 2) Camino libre -> avanzar step_cm.
        # -------------------------------------------------

        if front_distance is not None and front_distance >= safe_distance:

            try:
                response = await move_forward_cm(step_cm)
            except Exception as e:
                log.append({
                    "step": step_index,
                    "action": "move_forward_error",
                    "error": str(e),
                })
                reason_stopped = "move_error"
                break

            total_forward_cm += step_cm
            log.append({
                "step": step_index,
                "action": "advance",
                "distance_cm": step_cm,
                "esp32_response": response,
            })

            continue

        # -------------------------------------------------
        # 3) Obstáculo detectado -> escanear el entorno.
        # -------------------------------------------------

        log.append({
            "step": step_index,
            "action": "obstacle_detected",
            "front_distance_cm": front_distance,
        })

        scan = await scan_environment()

        log.append({
            "step": step_index,
            "action": "scan",
            "safest_angle": scan["safest_angle"],
            "safest_distance": scan["safest_distance"],
            "measurements": scan["measurements"],
        })

        safest_angle = scan["safest_angle"]
        safest_distance = scan["safest_distance"]

        # -------------------------------------------------
        # 4) No hay dirección segura -> retroceder y parar.
        # -------------------------------------------------

        if safest_angle is None:

            log.append({
                "step": step_index,
                "action": "no_safe_direction",
            })

            try:
                await move_backward_cm(DEFAULT_BACKUP_CM)
                log.append({
                    "step": step_index,
                    "action": "back_up",
                    "distance_cm": DEFAULT_BACKUP_CM,
                })
            except Exception as e:
                log.append({
                    "step": step_index,
                    "action": "back_up_error",
                    "error": str(e),
                })

            reason_stopped = "stuck"
            break

        # -------------------------------------------------
        # 5) Girar el chasis hacia el ángulo más seguro.
        #    El servo a 90° es "al frente".
        #    < 90° es hacia la derecha; > 90° hacia la izquierda.
        # -------------------------------------------------

        delta = safest_angle - 90  # positivo: izquierda, negativo: derecha

        if abs(delta) < 5:
            # Ya apunta más o menos hacia el hueco pero sigue bloqueado
            # al frente -> retrocede un poco e intenta de nuevo.
            try:
                await move_backward_cm(DEFAULT_BACKUP_CM)
                log.append({
                    "step": step_index,
                    "action": "back_up",
                    "distance_cm": DEFAULT_BACKUP_CM,
                })
            except Exception:
                pass
            continue

        direction = "left" if delta > 0 else "right"
        degrees = abs(delta)

        try:
            response = await turn_degrees(direction, degrees)
            turns += 1
            log.append({
                "step": step_index,
                "action": "turn",
                "direction": direction,
                "degrees": degrees,
                "esp32_response": response,
            })
        except Exception as e:
            log.append({
                "step": step_index,
                "action": "turn_error",
                "error": str(e),
            })
            reason_stopped = "turn_error"
            break

    # Siempre dejar el servo centrado y los motores detenidos.
    try:
        await move_servo(90)
        await stop()
    except Exception:
        pass

    summary = {
        "reason_stopped": reason_stopped,
        "steps_executed": len(
            [entry for entry in log if entry["action"] == "advance"]
        ),
        "total_forward_cm": total_forward_cm,
        "turns": turns,
    }

    return {
        "summary": summary,
        "log": log,
    }
