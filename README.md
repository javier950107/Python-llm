# Python-llm

Agente en Python que conecta un **LLM** (vía la API compatible con
OpenAI de **Nous Research**) con el robot **Arduino-Robot**.

El usuario habla en lenguaje natural con el LLM. El LLM decide qué
herramientas invocar (mover servo, escanear, moverse por cm, girar,
explorar) y el código las traduce en comandos WebSocket para el ESP32.

Es el "cerebro" del robot. El firmware Arduino es el "cuerpo".

---

## 🧠 Arquitectura

```
┌──────────────┐   texto     ┌───────────┐   HTTP     ┌──────┐
│  Usuario     │────────────▶│  main.py  │───────────▶│ Nous │
│ (terminal)   │◀────────────│           │◀───────────│ LLM  │
└──────────────┘  respuesta  └─────┬─────┘  tool_call └──────┘
                                   │
                              ┌────▼──────────┐
                              │  agent/brain  │  ← dispatch de tools
                              └────┬──────────┘
                                   │
              ┌────────────────────┼────────────────────┐
              │                    │                    │
     ┌────────▼──────┐    ┌────────▼──────┐   ┌─────────▼──────┐
     │ agent/tools   │    │ perception/   │   │  hardware/     │
     │ (wrappers)    │    │ - scanner     │   │  - esp32       │
     │               │    │ - exploration │   │  - motors      │
     └───────┬───────┘    └───────┬───────┘   └────────┬───────┘
             │                    │                    │
             └────────────────────┴────────────────────┘
                                  │
                                  ▼ WebSocket
                          ┌───────────────┐
                          │  ESP32        │
                          │  (Arduino-    │
                          │   Robot)      │
                          └───────────────┘
```

---

## 📁 Estructura

```
Python-llm/
├── main.py                    ← chat en terminal
├── config.py                  ← lee .env, IP del ESP32, modelo LLM
├── requirements.txt
├── .env                       ← (tuyo, no commiteado) NOUS_API_KEY=…
│
├── agent/
│   ├── brain.py               ← cliente OpenAI + dispatch de tools
│   ├── prompts.py             ← SYSTEM_PROMPT del robot
│   └── tools.py               ← wrappers de cada herramienta
│
├── hardware/
│   ├── esp32.py               ← cliente WebSocket + servo/distance
│   └── motors.py              ← move_forward_cm, move_backward_cm, turn_*
│
├── perception/
│   ├── scanner.py             ← barrido servo 0-180 + análisis
│   └── exploration.py         ← bucle explore(): avanza, escanea, gira
│
└── test/
    ├── test_servo.py          ← mueve el servo
    ├── test_distance.py       ← lee distancia
    ├── test_scan.py           ← escaneo completo
    ├── test_move.py           ← avanza N cm
    ├── test_explore.py        ← exploración autónoma sin LLM
    ├── robot_test.py          ← consola cruda WebSocket
    └── ia_test.py             ← ping al LLM sin robot
```

---

## ⚙️ Instalación

Requiere **Python 3.10+**.

```bash
cd Python-llm

# 1. Entorno virtual
python -m venv .venv
source .venv/bin/activate

# 2. Dependencias
pip install -r requirements.txt

# 3. Variables de entorno
cat > .env <<'EOF'
NOUS_API_KEY=tu_api_key_aqui
EOF

# 4. Ajusta la IP del ESP32 en config.py
#    (la que te mostró el Serial Monitor al arrancar el robot)
```

> ⚠️ **Rota tu API key**: hay una expuesta en `test/ia_test.py`.
> Bórrala de ahí y usa siempre `NOUS_API_KEY` del `.env`.

---

## 🔧 Configuración clave (`config.py`)

| Variable | Valor por defecto | Qué es |
|---|---|---|
| `NOUS_API_KEY` | leída de `.env` | Token de Nous Research |
| `NOUS_BASE_URL` | `https://inference-api.nousresearch.com/v1` | Endpoint |
| `LLM_MODEL` | `stepfun/step-3.7-flash:free` | Modelo. Ajústalo si Nous lo retira |
| `ESP32_HOST` | `192.168.100.23` | **IP del robot**; ajústala |
| `ESP32_PORT` | `81` | Puerto del WebSocket |

Y en `hardware/motors.py`:

| Variable | Valor | Qué es |
|---|---|---|
| `MS_PER_90_DEG` | `500` | Milisegundos para girar 90° en el sitio. Calibrar. |

---

## ▶️ Cómo probar (orden recomendado)

Prueba de menor a mayor complejidad, siempre con el ESP32 encendido
y en la misma red WiFi:

```bash
# 1) LLM aislado (no necesita robot)
python test/ia_test.py

# 2) Solo servo — el más seguro
python test/test_servo.py

# 3) Ultrasónico
python test/test_distance.py

# 4) Movimiento por cm (¡pon el robot en el piso!)
python test/test_move.py 20

# 5) Escaneo completo (0-180°)
python test/test_scan.py

# 6) Exploración autónoma sin LLM
python test/test_explore.py 3 15 25       # 3 pasos, 15 cm, 25 cm seguros

# 7) Chat con el LLM
python main.py
Tú: explora el entorno
```

---

## 💬 Comandos que reconoce el LLM

Como el LLM decide qué tool invocar, no hay una lista fija de frases.
Estos son ejemplos que funcionan bien con el `SYSTEM_PROMPT` actual:

| Lo que dices | Tool que llamará |
|---|---|
| *"mueve el servo a 45 grados"* | `move_servo(angle=45)` |
| *"avanza 30 cm"* | `move(distance_cm=30, direction="forward")` |
| *"retrocede 15 cm"* | `move(distance_cm=15, direction="backward")` |
| *"gira 90 grados a la derecha"* | `turn(direction="right", degrees=90)` |
| *"escanea alrededor"* | `scan_environment()` |
| *"explora el entorno sin chocar"* | `explore_environment()` |
| *"detente"* | `stop()` |

---

## 🕹️ Ejemplo de uso directo desde código

Si prefieres no pasar por el LLM y controlar el robot como una API:

```python
import asyncio
from hardware.motors import move_forward_cm, turn_degrees, stop
from perception.exploration import explore

async def main():
    # Movimiento manual
    await move_forward_cm(30)
    await turn_degrees("left", 90)
    await move_forward_cm(30)
    await stop()

    # O exploración autónoma
    result = await explore(max_steps=5, step_cm=20, safe_distance=30)
    print(result["summary"])
    for entry in result["log"]:
        print(entry)

asyncio.run(main())
```

---

## 🐛 Problemas comunes

| Síntoma | Causa | Solución |
|---|---|---|
| `[Errno 111] Connection refused` | ESP32 apagado o IP incorrecta | Verifica IP en `config.py` |
| `ESP32 rechazó el comando move_cm: timeout` | Encoders desconectados o `PULSES_PER_CM` mal | Ver README del Arduino |
| El LLM contesta pero no llama tool | El modelo free ignora el function calling | Sé explícito: *"llama a explore_environment"* |
| `RuntimeError: No se encontró NOUS_API_KEY` | Falta `.env` o `python-dotenv` no cargó | Crea el `.env` en la raíz de `Python-llm/` |
| El robot avanza mal o se pasa de largo | `PULSES_PER_CM` sin calibrar | Ver `Arduino-Robot/README.md` |
| Los giros no dan 90° | `MS_PER_90_DEG` sin calibrar | Ajusta en `hardware/motors.py` |

---

## 🧭 Siguiente paso

Cuando todo funcione, vale la pena:
1. Añadir persistencia del historial del chat (multi-turno).
2. Sustituir `turn_ms` por giros por encoder también, para precisión.
3. Añadir PWM al firmware para variar velocidad.
4. Loggear las respuestas del ESP32 a un archivo para depurar la
   calibración con datos reales.
