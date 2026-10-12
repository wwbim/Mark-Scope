# -*- coding: utf-8 -*-
import asyncio
import json
import os
import pathlib
import subprocess
import tempfile
import time
import urllib.request
import websockets

EDGE_PATH = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
POC_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "poc_offline_vditor.html"))
PORT = 9666

async def send_cmd(ws, msg_id, method, params=None):
    payload = {"id": msg_id, "method": method}
    if params:
        payload["params"] = params
    await ws.send(json.dumps(payload))
    while True:
        resp = await ws.recv()
        data = json.loads(resp)
        if data.get("id") == msg_id:
            return data

async def test():
    temp_profile = tempfile.mkdtemp(prefix="edge_poc_debug_")
    proc = subprocess.Popen([
        EDGE_PATH, "--headless=new", f"--remote-debugging-port={PORT}",
        f"--user-data-dir={temp_profile}", "--disable-gpu", "about:blank"
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(1.0)
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{PORT}/json") as resp:
            targets = json.loads(resp.read().decode())
        page_targets = [t for t in targets if t.get("type") == "page"]
        if not page_targets:
            print("No page target found!")
            return
        ws_url = page_targets[0]["webSocketDebuggerUrl"]
        async with websockets.connect(ws_url) as ws:
            file_url = pathlib.Path(POC_PATH).as_uri()
            print("Target URL:", file_url)
            res = await send_cmd(ws, 1, "Page.navigate", {"url": file_url})
            print("Page.navigate res:", res)
            time.sleep(2.0)
            res2 = await send_cmd(ws, 2, "Runtime.evaluate", {"expression": "window.location.href"})
            print("location.href:", res2.get("result", {}).get("result", {}).get("value"))
            res3 = await send_cmd(ws, 3, "Runtime.evaluate", {"expression": "document.title"})
            print("document.title:", res3.get("result", {}).get("result", {}).get("value"))
            res4 = await send_cmd(ws, 4, "Runtime.evaluate", {"expression": "document.body ? document.body.innerHTML.substring(0, 300) : 'NO_BODY'"})
            print("body preview:", res4.get("result", {}).get("result", {}).get("value"))
    finally:
        proc.kill()
        proc.wait()

if __name__ == "__main__":
    asyncio.run(test())
