import requests
from lesson0 import fetch_user

BASE_URL = "https://httpbin.org/get?page=2&limit=5"


def get_with_params(url: str, params: dict) -> requests.Response:

    response = requests.get(url, params=params, timeout=5)
    response.raise_for_status()
    return response

def post_json(url: str, payload: dict) -> dict:

    response = requests.post(url, json=payload, timeout=5)
    response.raise_for_status()
    return response.json()

def classify_status(status_code: int) -> str:

    if 200 <= status_code <= 299:
        return "success"
    elif 300 <= status_code <= 399:
        return "redirect"
    elif 400 <= status_code <= 499:
        return "client_error"
    elif 500 <= status_code <= 599:
        return "server_error"
    else:
        return "unknown"

if __name__ == "__main__":
    codes = [200, 201, 204, 301, 400, 401, 403, 404, 429, 500, 503]

    for code in codes:
        response = requests.get(f"https://httpbin.org/status/{code}", timeout=5)
        category = classify_status(response.status_code)
        print(f"Code: {code} | response.ok: {response.ok} | Category: {category}")