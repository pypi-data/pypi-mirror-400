from time import time
import jwt
import os
import requests

API_URL = "https://api.plotune.net"


def create_jwt() -> str:

    payload = {
        "username_or_email": os.getenv("EMAIL"),
        "password": os.getenv("PASSWORD"),
    }
    response = requests.post(f"{API_URL}/login", json=payload)

    access_token = None
    if response.status_code in (200, 201):
        access_token = response.json().get("access_token")

    stream_url = f"{API_URL}/auth/stream"
    headers = {"Authorization": f"Bearer {access_token}"}

    response = requests.get(stream_url, headers=headers)
    stream_token = response.json().get("token")
    print("Stream Token", stream_token)

    headers = {"Authorization": f"{stream_token}"}
    return stream_token
