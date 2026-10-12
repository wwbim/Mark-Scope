# -*- coding: utf-8 -*-
"""
Verification test for drag and drop file loading in Deliverables/MarkScope.html.
Dispatches synthetic drag & drop file events to verify the overlay dismissal and document loading.
"""
import asyncio
import json
import os
import pathlib
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.request
import websockets

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

EDGE_PATH = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
HTML_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "Deliverables", "MarkScope.html"))
PORT = 9933

def log(msg):
    print(msg, flush=True)

async def send_cmd(ws, msg_id, method, params=None):
    payload = {"id": msg_id, "method": method}
    if params: payload["params"] = params
    await ws.send(json.dumps(payload))
    while True:
        resp = await ws.recv()
        data = json.loads(resp)
        if data.get("id") == msg_id:
            return data

async def verify():
    temp_profile = tempfile.mkdtemp(prefix="edge_drag_test_")
    cmd = [
        EDGE_PATH, "--headless=new", f"--remote-debugging-port={PORT}",
        f"--user-data-dir={temp_profile}", "--disable-gpu", "--no-sandbox",
        "--window-size=1280,800", "--allow-file-access-from-files", "about:blank"
    ]
    proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    try:
        time.sleep(0.8)
        with urllib.request.urlopen(f"http://127.0.0.1:{PORT}/json") as resp:
            targets = json.loads(resp.read().decode())
        ws_url = [t for t in targets if t.get("type") == "page"][0]["webSocketDebuggerUrl"]

        async with websockets.connect(ws_url, max_size=50*1024*1024) as ws:
            msg_id = 1
            await send_cmd(ws, msg_id, "Page.enable"); msg_id += 1
            await send_cmd(ws, msg_id, "Runtime.enable"); msg_id += 1

            file_url = pathlib.Path(HTML_PATH).as_uri()
            log(f"Loading {file_url}...")
            await send_cmd(ws, msg_id, "Page.navigate", {"url": file_url}); msg_id += 1
            await asyncio.sleep(2.0)

            # Test simulating dragenter
            log("Simulating dragenter...")
            res1 = await send_cmd(ws, msg_id, "Runtime.evaluate", {
                "expression": """
                (() => {
                  const dt = new DataTransfer();
                  const file = new File(["# 拖拽测试内容\\n\\n来自拖放测试文件。"], "test_drag.md", { type: "text/markdown" });
                  dt.items.add(file);
                  const enterEvent = new DragEvent('dragenter', { dataTransfer: dt, bubbles: true, cancelable: true });
                  window.dispatchEvent(enterEvent);
                  return document.getElementById('drag-drop-overlay').style.display;
                })()
                """
            })
            msg_id += 1
            overlay_after_enter = res1.get("result", {}).get("result", {}).get("value")
            log(f"Overlay on dragenter: {overlay_after_enter} (Expected: 'flex')")

            # Test simulating drop
            log("Simulating drop...")
            res2 = await send_cmd(ws, msg_id, "Runtime.evaluate", {
                "expression": """
                (() => {
                  const dt = new DataTransfer();
                  const file = new File(["# 拖拽测试成功\\n\\n文件已成功加载！"], "test_drag.md", { type: "text/markdown" });
                  dt.items.add(file);
                  const dropEvent = new DragEvent('drop', { dataTransfer: dt, bubbles: true, cancelable: true });
                  window.dispatchEvent(dropEvent);
                })()
                """
            })
            msg_id += 1

            await asyncio.sleep(0.5)

            # Check overlay hidden and doc loaded
            res3 = await send_cmd(ws, msg_id, "Runtime.evaluate", {
                "expression": """
                JSON.stringify({
                  overlayDisplay: document.getElementById('drag-drop-overlay').style.display,
                  docTitle: document.getElementById('current-doc-title').innerText,
                  contentPreview: window.markScopeApp ? window.markScopeApp.getContent().substring(0, 50) : ''
                })
                """
            })
            msg_id += 1
            state = json.loads(res3.get("result", {}).get("result", {}).get("value", "{}"))
            log(f"State after drop: {state}")

            if state.get("overlayDisplay") == "none" and state.get("docTitle") == "test_drag.md" and "拖拽测试成功" in state.get("contentPreview"):
                log("🎉 DRAG & DROP VERIFICATION PASSED 100%!")
                return True
            else:
                log("❌ Drag & drop verification failed.")
                return False

    finally:
        proc.kill()
        proc.wait()
        try:
            shutil.rmtree(temp_profile, ignore_errors=True)
        except Exception:
            pass

if __name__ == "__main__":
    asyncio.run(verify())
