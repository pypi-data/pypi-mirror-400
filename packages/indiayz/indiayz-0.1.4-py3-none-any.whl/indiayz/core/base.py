import requests
from indiayz.core.config import BASE_URL, TIMEOUT

class BaseModule:
    @staticmethod
    def _post(endpoint: str, data: dict):
        try:
            r = requests.post(
                f"{BASE_URL}{endpoint}",
                json=data,
                timeout=TIMEOUT
            )
            r.raise_for_status()
            return r.json()
        except Exception:
            raise RuntimeError("Indiayz service is currently unavailable")
