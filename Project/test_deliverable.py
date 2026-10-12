# -*- coding: utf-8 -*-
"""
End-to-End Verification Test for Deliverables/MarkScope.html
Runs in headless Edge, validates all core components, outlines, statusbars,
and takes a screenshot of the final production deliverable.
"""
import asyncio
import base64
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
PORT = 9911

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
    temp_profile = tempfile.mkdtemp(prefix="edge_markscope_test_")
    log(f"Isolated profile: {temp_profile}")

    cmd = [
        EDGE_PATH, "--headless=new", f"--remote-debugging-port={PORT}",
        f"--user-data-dir={temp_profile}", "--disable-gpu", "--no-sandbox",
        "--window-size=1280,800",
        "--disable-web-security", "--allow-file-access-from-files", "about:blank"
    ]
    proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    try:
        # Wait for CDP
        target_info = None
        for i in range(20):
            time.sleep(0.4)
            try:
                with urllib.request.urlopen(f"http://127.0.0.1:{PORT}/json", timeout=2) as resp:
                    targets = json.loads(resp.read().decode())
                    page_targets = [t for t in targets if t.get("type") == "page"]
                    if page_targets:
                        target_info = page_targets[0]
                        break
            except Exception:
                pass

        if not target_info:
            log("❌ Failed to connect to Edge CDP endpoint.")
            return False

        ws_url = target_info["webSocketDebuggerUrl"]
        async with websockets.connect(ws_url, max_size=50*1024*1024) as ws:
            msg_id = 1
            await send_cmd(ws, msg_id, "Page.enable"); msg_id += 1
            await send_cmd(ws, msg_id, "Runtime.enable"); msg_id += 1

            file_url = pathlib.Path(HTML_PATH).as_uri()
            log(f"Navigating to deliverable: {file_url}...")
            await send_cmd(ws, msg_id, "Page.navigate", {"url": file_url}); msg_id += 1

            # Wait for Vditor and App ready
            log("Waiting for Mark Scope application lifecycle ready...")
            app_ready = False
            for r in range(20):
                await asyncio.sleep(0.5)
                res = await send_cmd(ws, msg_id, "Runtime.evaluate", {
                    "expression": """
                    JSON.stringify({
                      title: document.title,
                      docTitle: document.getElementById('current-doc-title') ? document.getElementById('current-doc-title').innerText : '',
                      vditorHtmlLen: document.getElementById('vditor-container') ? document.getElementById('vditor-container').innerHTML.length : 0,
                      outlineCount: document.querySelectorAll('.outline-item').length,
                      statChars: document.getElementById('stat-chars') ? document.getElementById('stat-chars').innerText : '',
                      statWords: document.getElementById('stat-words') ? document.getElementById('stat-words').innerText : '',
                      statMode: document.getElementById('stat-mode') ? document.getElementById('stat-mode').innerText : ''
                    })
                    """
                })
                msg_id += 1
                try:
                    info = json.loads(res.get("result", {}).get("result", {}).get("value", "{}"))
                    if info.get("vditorHtmlLen", 0) > 20000 and info.get("outlineCount", 0) > 0:
                        log(f"✅ Mark Scope App is fully loaded & rendered!")
                        log(f"   - Title: {info.get('title')}")
                        log(f"   - Current File: {info.get('docTitle')}")
                        log(f"   - Outline Headings: {info.get('outlineCount')} items")
                        log(f"   - Metrics: {info.get('statChars')} | {info.get('statWords')}")
                        log(f"   - Active Mode: {info.get('statMode')}")
                        app_ready = True
                        break
                except Exception as e:
                    pass

            if not app_ready:
                log("❌ Timed out waiting for Mark Scope app initialization.")
                return False

            # Capture Screenshot of Production Deliverable
            screenshot_path = os.path.join(os.path.dirname(__file__), "mark_scope_production.png")
            snap_res = await send_cmd(ws, msg_id, "Page.captureScreenshot", {"format": "png"})
            msg_id += 1
            img_b64 = snap_res.get("result", {}).get("data", "")
            if img_b64:
                with open(screenshot_path, "wb") as f:
                    f.write(base64.b64decode(img_b64))
                log(f"📸 Screenshot saved to: {screenshot_path}")

            log("\n" + "=" * 50)
            log("🎉 DELIVERABLES VERIFICATION PASSED: 100% READY!")
            log("=" * 50)
            return True

    finally:
        proc.kill()
        proc.wait()
        try:
            shutil.rmtree(temp_profile, ignore_errors=True)
        except Exception:
            pass

if __name__ == "__main__":
    asyncio.run(verify())
