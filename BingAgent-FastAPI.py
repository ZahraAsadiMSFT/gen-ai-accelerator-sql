# app.py
import os, time, requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# ---  CONFIG -------------------------------------------------------------
ENDPOINT      = os.environ["AZURE_OPENAI_ENDPOINT"]
API_KEY       = os.environ["AZURE_OPENAI_API_KEY"]
ASSISTANT_ID  = os.environ["ASSISTANT_ID"]
API_VERSION   = "2024-07-01-preview"

HEADERS = {"Content-Type": "application/json", "api-key": API_KEY}

# ---  CORE LOGIC ---------------------------------------------------------
def ask_assistant(text: str) -> str:
    # create thread
    thread = requests.post(f"{ENDPOINT}/openai/threads?api-version={API_VERSION}",
                           headers=HEADERS); thread.raise_for_status()
    tid = thread.json()["id"]

    # add user message
    requests.post(f"{ENDPOINT}/openai/threads/{tid}/messages?api-version={API_VERSION}",
                  headers=HEADERS, json={"role": "user", "content": text}).raise_for_status()

    # run assistant
    run = requests.post(f"{ENDPOINT}/openai/threads/{tid}/runs?api-version={API_VERSION}",
                        headers=HEADERS, json={"assistant_id": ASSISTANT_ID}); run.raise_for_status()
    rid = run.json()["id"]

    # poll status
    while True:
        r = requests.get(f"{ENDPOINT}/openai/threads/{tid}/runs/{rid}?api-version={API_VERSION}",
                         headers=HEADERS); r.raise_for_status()
        status = r.json()["status"]
        if status in ("completed", "failed", "cancelled"):
            break
        time.sleep(2)

    # fetch assistant reply
    msgs = requests.get(f"{ENDPOINT}/openai/threads/{tid}/messages?api-version={API_VERSION}",
                        headers=HEADERS); msgs.raise_for_status()
    for m in msgs.json()["data"]:
        if m["role"] == "assistant":
            return m["content"][0]["text"]["value"]
    return "No reply."

# ---  FASTAPI ------------------------------------------------------------
app = FastAPI()

class ChatRequest(BaseModel):
    message: str

@app.post("/chat")
def chat(req: ChatRequest):
    try:
        answer = ask_assistant(req.message)
        return {"answer": answer}
    except requests.HTTPError as e:
        raise HTTPException(status_code=500, detail=str(e))

# run with:  uvicorn app:app --reload
