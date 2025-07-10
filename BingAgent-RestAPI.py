import os, time, requests

# ---  CONFIG -------------------------------------------------------------
ENDPOINT      = os.environ["AZURE_OPENAI_ENDPOINT"]          # e.g. https://contoso-openai.openai.azure.com
API_KEY       = os.environ["AZURE_OPENAI_API_KEY"]
ASSISTANT_ID  = os.environ["ASSISTANT_ID"]                   # copy from Foundry playground
API_VERSION   = "2024-07-01-preview"                         # latest preview

HEADERS = {
    "Content-Type": "application/json",
    "api-key": API_KEY
}

def run_assistant(user_query: str) -> str:
    # 1. create a thread
    thread = requests.post(
        f"{ENDPOINT}/openai/threads?api-version={API_VERSION}",
        headers=HEADERS
    ); thread.raise_for_status()
    thread_id = thread.json()["id"]

    # 2. add the user message
    requests.post(
        f"{ENDPOINT}/openai/threads/{thread_id}/messages?api-version={API_VERSION}",
        headers=HEADERS,
        json={"role": "user", "content": user_query}
    ).raise_for_status()

    # 3. run the assistant
    run = requests.post(
        f"{ENDPOINT}/openai/threads/{thread_id}/runs?api-version={API_VERSION}",
        headers=HEADERS,
        json={"assistant_id": ASSISTANT_ID}     # assistant_id (not agent_id)
    ); run.raise_for_status()
    run_id = run.json()["id"]

    # 4. poll until finished
    while True:
        status_resp = requests.get(
            f"{ENDPOINT}/openai/threads/{thread_id}/runs/{run_id}?api-version={API_VERSION}",
            headers=HEADERS
        ); status_resp.raise_for_status()
        status = status_resp.json()["status"]
        if status in ("completed", "failed", "cancelled"):
            break
        time.sleep(2)

    # 5. read the answer
    msgs = requests.get(
        f"{ENDPOINT}/openai/threads/{thread_id}/messages?api-version={API_VERSION}",
        headers=HEADERS
    ); msgs.raise_for_status()

    for m in msgs.json()["data"]:
        if m["role"] == "assistant":
            return m["content"][0]["text"]["value"]

    return "No assistant reply."

if __name__ == "__main__":
    print(run_assistant("Please provide technical specifications and purchasing options for a 5-inch stainless-steel strainer."))
