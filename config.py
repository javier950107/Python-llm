import os
from dotenv import load_dotenv


load_dotenv()


# =====================================================
# NOUS
# =====================================================

NOUS_API_KEY = os.getenv("NOUS_API_KEY")

if not NOUS_API_KEY:
    raise RuntimeError(
        "No se encontró NOUS_API_KEY en el archivo .env"
    )


NOUS_BASE_URL = "https://inference-api.nousresearch.com/v1"

LLM_MODEL = "stepfun/step-3.7-flash:free"


# =====================================================
# ESP32
# =====================================================

ESP32_HOST = "192.168.100.23"
ESP32_PORT = 81