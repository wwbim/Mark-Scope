# -*- coding: utf-8 -*-
"""
Automated headless Edge verification for Mark Scope PoC.
Uses an isolated temporary user-data-dir and evaluates DOM status directly.
"""
import asyncio
import base64
import json
import os
import pathlib
import shutil
import subprocess
import tempfile
import time
import urllib.request
import websockets

EDGE_PATH = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
POC_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "poc_offline_vditor.html"))
PORT = 9888

import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

def log(msg):
    print(msg, flush=True)

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

async def verify():
    temp_profile = tempfile.mkdtemp(prefix="edge_poc_test_")
    log(f"Using isolated profile: {temp_profile}")

    cmd = [
        EDGE_PATH,
        "--headless=new",
        f"--remote-debugging-port={PORT}",
        f"--user-data-dir={temp_profile}",
        "--disable-gpu",
        "--no-sandbox",
        "--disable-web-security",
        "--allow-file-access-from-files",
        "about:blank"
    ]
    log(f"Launching Edge on port {PORT}...")
    proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    try:
        # 1. Connect to CDP
        target_info = None
        for i in range(20):
            time.sleep(0.4)
            try:
                with urllib.request.urlopen(f"http://127.0.0.1:{PORT}/json", timeout=2) as resp:
                    targets = json.loads(resp.read().decode())
                    page_targets = [t for t in targets if t.get("type") == "page"]
                    if page_targets:
                        target_info = page_targets[0]
                        log(f"CDP endpoint ready (attempt {i+1})")
                        break
            except Exception:
                pass

        if not target_info:
            log("ERROR: Could not connect to Edge.")
            return False

        ws_url = target_info["webSocketDebuggerUrl"]
        log(f"Connecting to {ws_url}...")

        async with websockets.connect(ws_url, max_size=50*1024*1024) as ws:
            msg_id = 1
            await send_cmd(ws, msg_id, "Page.enable"); msg_id += 1
            await send_cmd(ws, msg_id, "Runtime.enable"); msg_id += 1

            file_url = pathlib.Path(POC_PATH).as_uri()
            log(f"Navigating to {file_url}...")
            await send_cmd(ws, msg_id, "Page.navigate", {"url": file_url}); msg_id += 1

            # Poll DOM status
            log("Polling document status in browser...")
            status_text = ""
            console_errors = []
            
            for check_round in range(20):
                await asyncio.sleep(0.5)
                # Check status element text
                eval_res = await send_cmd(ws, msg_id, "Runtime.evaluate", {
                    "expression": """
                    JSON.stringify({
                      status: document.getElementById('poc-status') ? document.getElementById('poc-status').innerText : 'NOT_FOUND',
                      hasLute: typeof window.Lute !== 'undefined',
                      hasVditor: typeof window.Vditor !== 'undefined',
                      hasKatex: typeof window.katex !== 'undefined',
                      hasMermaid: typeof window.mermaid !== 'undefined',
                      hasHljs: typeof window.hljs !== 'undefined',
                      vditorHtmlLen: document.getElementById('vditor-container') ? document.getElementById('vditor-container').innerHTML.length : 0
                    })
                    """
                })
                msg_id += 1

                val_str = eval_res.get("result", {}).get("result", {}).get("value", "{}")
                try:
                    info = json.loads(val_str)
                    status_text = info.get("status", "")
                    log(f"Round {check_round+1} State: status='{status_text}', VditorHTML={info.get('vditorHtmlLen')} bytes, Lute={info.get('hasLute')}, Mermaid={info.get('hasMermaid')}")
                    if "PoC 验证成功" in status_text or "验证成功" in status_text:
                        log("Success confirmed by DOM status!")
                        break
                except Exception as e:
                    log(f"Error parsing eval result: {e}")

            # Capture screenshot
            screenshot_path = os.path.join(os.path.dirname(__file__), "poc_screenshot.png")
            snap_res = await send_cmd(ws, msg_id, "Page.captureScreenshot", {"format": "png"})
            msg_id += 1
            img_b64 = snap_res.get("result", {}).get("data", "")
            if img_b64:
                with open(screenshot_path, "wb") as f:
                    f.write(base64.b64decode(img_b64))
                log(f"Saved screenshot to: {screenshot_path}")

            if "成功" in status_text:
                log("\n==========================================")
                log("🎉 100% OFFLINE POC VERIFIED SUCCESSFULLY!")
                log("==========================================")
                return True
            else:
                log(f"\n❌ Verification failed with status: {status_text}")
                return False

    finally:
        log("Cleaning up Edge test process and temporary profile...")
        proc.kill()
        proc.wait()
        try:
            shutil.rmtree(temp_profile, ignore_errors=True)
        except Exception:
            pass

if __name__ == "__main__":
    asyncio.run(verify())
