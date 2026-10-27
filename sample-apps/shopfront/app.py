import os
import time

from fastapi import FastAPI, HTTPException

app = FastAPI(title="shopfront")

VALID_MODES = {"normal", "slow", "leak", "crash"}
state = {"mode": "normal"}
leaked_memory = []  # grows in "leak" mode


@app.get("/health")
def health():
    return {"status": "fine", "mode": state["mode"]}


@app.get("/checkout")
def checkout():
    mode = state["mode"]
    if mode == "slow":
        time.sleep(3)  # simulate a slow dependency
    elif mode == "leak":
        leaked_memory.append(bytearray(10 * 1024 * 1024))  # +10 MB per request
    elif mode == "crash":
        os._exit(1)  # hard crash, like a real bug
    return {"order": "confirmed", "mode": mode}


@app.post("/admin/mode/{mode}")
def set_mode(mode: str):
    if mode not in VALID_MODES:
        raise HTTPException(status_code=400, detail=f"mode must be one of {sorted(VALID_MODES)}")
    state["mode"] = mode
    return {"mode": mode}