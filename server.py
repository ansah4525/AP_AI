from fastapi import FastAPI
from pydantic import BaseModel
import requests
import os
from fastapi import HTTPException

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
    resp=response

    data = response.json()

    if resp.status_code != 200 or "choices" not in data:
        print("Mistral error:", resp.status_code, data)   # shows in Render logs
        raise HTTPException(status_code=502, detail=f"Mistral {resp.status_code}: {data}")

   

    return {"response": data["choices"][0]["message"]["content"]}
