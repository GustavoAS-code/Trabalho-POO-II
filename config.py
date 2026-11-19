import os
from dotenv import load_dotenv

load_dotenv()

API_BASE_URL = os.getenv("LOCADORA_API_URL", "http://127.0.0.1:5000").rstrip("/")
REQUEST_TIMEOUT = float(os.getenv("LOCADORA_TIMEOUT", "5"))