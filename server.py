from fastapi import FastAPI
from pydantic import BaseModel
import requests
import os

app = FastAPI()

MISTRAL_API_KEY = "mstrl_0tJG66jAs5cNQ8DafMh0HPVgl65LJKUL_3c929L"

class PromptRequest(BaseModel):
    prompt: str

@app.post("/ai")
def run_llm(req: PromptRequest):

    response = requests.post(
        "https://api.mistral.ai/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {MISTRAL_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": "mistral-small",
            "messages": [
                {"role": "user", "content": req.prompt}
            ]
        }
    )

    data = response.json()

    return {"response": data["choices"][0]["message"]["content"]}
