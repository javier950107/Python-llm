"""
Comportamiento de seguimiento de objetivo.

El robot escanea un rango frontal, elige el objeto más cercano dentro
de una ventana de distancia [min_distance, max_distance] y lo persigue:

- Si el objetivo se movió lateralmente, gira hacia él.
- Si está más lejos que la distancia deseada, avanza.
- Si está más cerca que la distancia mínima, retrocede.
- Si no encuentra ningún objetivo válido durante N iteraciones,
  se detiene y devuelve el log.

Con un solo HC-SR04 esto sigue "el objeto más cercano", no una
persona específica. Ver el README para las limitaciones.
"""

import asyncio

from hardware.esp32 import move_servo, scan_range
from hardware.motors import (
    move_forward_cm,
    move_backward_cm,
    turn_degrees,
    stop,
)


# =====================================================
# CONSTANTES DE SEGUIMIENTO
# =====================================================

DEFAULT_MAX_ITERATIONS = 20
DEFAULT_MIN_DISTANCE_CM = 25.0
DEFAULT_MAX_DISTANCE_CM = 100.0
DEFAULT_STEP_CM = 10.0
DEFAULT_SCAN_START = 60
DEFAULT_SCAN_END = 120
DEFAULT_SCAN_STEP = 10
DEFAULT_LOST_TOLERANCE = 3


async def follow_target(
    max_iterations: int = DEFAULT_MAX_ITERATIONS,
    min_distance: float = DEFAULT_MIN_DISTANCE_CM,
    max_distance: float = DEFAULT_MAX_DISTANCE_CM,
    step_cm: float = DEFAULT_STEP_CM,
    lost_tolerance: int = DEFAULT_LOST_TOLERANCE,
):
    """
    Bucle de seguimiento. Devuelve un diccionario con `summary` y
    `log` para que el LLM pueda contarle al usuario qué pasó.
    """

    log = []
    lost_counter = 0
    iterations_done = 0
    reason_stopped = "max_iterations_reached"

    # Distancia deseada al centro de la ventana.
    ideal_distance = (min_distance + max_distance) / 2.0

    for i in range(max_iterations):

        iterations_done = i + 1

        # -------------------------------------------------
        # 1) Escaneo rápido del frente (60°-120° por defecto).
        # -------------------------------------------------

        try:
            measurements = await scan_range(
                DEFAULT_SCAN_START,
                DEFAULT_SCAN_END,
                DEFAULT_SCAN_STEP,
            )
        except Exception as e:
            log.append({
                "iter": i,
                "action": "scan_error",
                "error": str(e),
            })
            reason_stopped = "scan_error"
            break

        # -------------------------------------------------
        # 2) Filtrar candidatos dentro de la ventana.
        # -------------------------------------------------

        candidates = [
            m for m in measurements
            if (
                m["distance"] is not None
                and m["distance"] > 0
                and min_distance <= m["distance"] <= max_distance
            )
        ]

        if not candidates:

            lost_counter += 1
            log.append({
                "iter": i,
                "action": "no_target",
                "lost_counter": lost_counter,
                "measurements": measurements,
            })

            if lost_counter >= lost_tolerance:
                reason_stopped = "target_lost"
                break

            # Espera un poco antes del siguiente escaneo.
            await asyncio.sleep(0.3)
            continue

        # Objetivo válido -> resetear contador de pérdidas.
        lost_counter = 0

        # -------------------------------------------------
        # 3) Elegir el candidato más cercano (asumimos que
        #    ese es el objetivo dentro de la ventana).
        # -------------------------------------------------

        target = min(candidates, key=lambda m: m["distance"])
        target_angle = target["angle"]
        target_distance = target["distance"]

        log.append({
            "iter": i,
            "action": "target_found",
            "angle": target_angle,
            "distance_cm": target_distance,
            "candidates": len(candidates),
        })

        # -------------------------------------------------
        # 4) Girar el chasis hacia el objetivo si se movió.
        # -------------------------------------------------

        delta = target_angle - 90  # positivo: izquierda, negativo: derecha

        if abs(delta) >= 10:

            direction = "left" if delta > 0 else "right"
            degrees = abs(delta)

            try:
                await turn_degrees(direction, degrees)
                log.append({
                    "iter": i,
                    "action": "turn",
                    "direction": direction,
                    "degrees": degrees,
                })
            except Exception as e:
                log.append({
                    "iter": i,
                    "action": "turn_error",
                    "error": str(e),
                })
                reason_stopped = "turn_error"
                break

        # -------------------------------------------------
        # 5) Ajustar distancia con avance o retroceso.
        # -------------------------------------------------

        try:
            if target_distance > ideal_distance + 5:
                await move_forward_cm(step_cm)
                log.append({
                    "iter": i,
                    "action": "advance",
                    "distance_cm": step_cm,
                })
            elif target_distance < min_distance:
                await move_backward_cm(step_cm)
                log.append({
                    "iter": i,
                    "action": "back_up",
                    "distance_cm": step_cm,
                })
            else:
                # Ya está en la ventana ideal, solo mantener posición.
                log.append({
                    "iter": i,
                    "action": "hold",
                })
        except Exception as e:
            log.append({
                "iter": i,
                "action": "move_error",
                "error": str(e),
            })
            reason_stopped = "move_error"
            break

    # Siempre dejar el servo centrado y motores detenidos.
    try:
        await move_servo(90)
        await stop()
    except Exception:
        pass

    summary = {
        "reason_stopped": reason_stopped,
        "iterations": iterations_done,
        "advances": len(
            [e for e in log if e["action"] == "advance"]
        ),
        "back_ups": len(
            [e for e in log if e["action"] == "back_up"]
        ),
        "turns": len(
            [e for e in log if e["action"] == "turn"]
        ),
        "target_found_times": len(
            [e for e in log if e["action"] == "target_found"]
        ),
    }

    return {
        "summary": summary,
        "log": log,
    }
