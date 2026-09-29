from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
import os
import time

app = FastAPI()

MISTRAL_API_KEY = os.environ.get("MISTRAL_API_KEY")
MISTRAL_MODEL = os.environ.get("MISTRAL_MODEL", "mistral-small")


class PromptRequest(BaseModel):
    prompt: str


@app.get("/health")
def health():
    # Used by the desktop app to wake the server without spending a Mistral request
    return {"status": "ok"}


@app.post("/ai")
def run_llm(req: PromptRequest):
    if not MISTRAL_API_KEY:
        raise HTTPException(status_code=500, detail="MISTRAL_API_KEY is not set on the server")

    response = None
    for attempt in range(3):
        response = requests.post(
            "https://api.mistral.ai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {MISTRAL_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": MISTRAL_MODEL,
                "messages": [{"role": "user", "content": req.prompt}],
            },
            timeout=120,
        )
        if response.status_code != 429:
            break
        time.sleep(2 * (attempt + 1))  # rate limited: wait 2s, then 4s, then give up

    try:
        data = response.json()
    except ValueError:
        data = {"raw": response.text[:300]}

    if response.status_code != 200 or "choices" not in data:
        print("Mistral error:", response.status_code, data)  # shows in Render logs
        raise HTTPException(status_code=502, detail=f"Mistral {response.status_code}: {data}")

    return {"response": data["choices"][0]["message"]["content"]}
