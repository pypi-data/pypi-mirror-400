import requests
from netic.config import save_key, load_key

API_URL = "https://netic.jtheberg.cloud/api/v1/chat"

def setapi(key: str):
    save_key(key)

def chat(message: str) -> str:
    key = load_key()
    if not key:
        raise RuntimeError("Aucune clé API définie")

    headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json"
    }

    try:
        r = requests.post(API_URL, json={"message": message}, headers=headers, timeout=30)
        if r.status_code != 200:
            print(f"Erreur API {r.status_code} : {r.text}")
            return f"Erreur API {r.status_code}"
        data = r.json()
        return data.get("response", "")
    except requests.exceptions.RequestException as e:
        return f"Erreur requête : {e}"
