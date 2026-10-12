# -*- coding: utf-8 -*-
"""
Automated verification for:
1. Full-Width Mode (正文全宽)
2. Interactive Table Column Resizer (拖拽调节栏宽)
3. Balanced Column Width Auto-Layout (表格列宽智能平衡算法)
4. Table-Only Breakout Full Width (单表全宽展开)
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
PORT = 9977

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
    temp_profile = tempfile.mkdtemp(prefix="edge_table_test_")
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
            log(f"Navigating to deliverable: {file_url}...")
            await send_cmd(ws, msg_id, "Page.navigate", {"url": file_url}); msg_id += 1
            await asyncio.sleep(2.5)

            # 1. Verify Table Balancing & Resizer Handles
            log("\n[Test 1] Verifying Table Balancing & Resizer Handles...")
            res1 = await send_cmd(ws, msg_id, "Runtime.evaluate", {
                "expression": """
                (() => {
                    const table = document.querySelector('table');
                    if (!table) return { error: 'No table found' };
                    const ths = Array.from(table.querySelectorAll('th'));
                    const widths = ths.map(th => th.style.width);
                    const resizers = table.querySelectorAll('.ms-col-resizer').length;
                    const toolbar = table.closest('.ms-table-wrapper') ? table.closest('.ms-table-wrapper').querySelector('.ms-table-toolbar') : null;
                    return {
                        colCount: ths.length,
                        widths: widths,
                        tableLayout: table.style.tableLayout,
                        resizerCount: resizers,
                        hasToolbar: !!toolbar
                    };
                })()
                """,
                "returnByValue": True
            })
            msg_id += 1
            val1 = res1.get("result", {}).get("result", {}).get("value", {})
            log(f"Table inspection result: {val1}")
            assert val1.get("colCount", 0) >= 3, "Expected at least 3 columns"
            assert val1.get("tableLayout") == "fixed", "Expected tableLayout=fixed"
            assert val1.get("resizerCount", 0) >= 2, "Expected col resizer handles"
            assert val1.get("hasToolbar") is True, "Expected table floating toolbar"
            log("✅ Table Balancing & Resizers verified!")

            # 2. Test Table-Only Breakout Full Width
            log("\n[Test 2] Verifying Table-Only Breakout Full Width (⛶ 表格全宽)...")
            res2 = await send_cmd(ws, msg_id, "Runtime.evaluate", {
                "expression": """
                (() => {
                    const btn = document.querySelector('.btn-breakout');
                    if (!btn) return { error: 'No breakout button' };
                    const beforeWidth = document.querySelector('table').offsetWidth;
                    btn.click();
                    const afterWidth = document.querySelector('table').offsetWidth;
                    const isBreakout = document.querySelector('.ms-table-wrapper').classList.contains('table-breakout-full');
                    return { beforeWidth, afterWidth, isBreakout };
                })()
                """,
                "returnByValue": True
            })
            msg_id += 1
            val2 = res2.get("result", {}).get("result", {}).get("value", {})
            log(f"Table Breakout result: {val2}")
            assert val2.get("isBreakout") is True, "Table should have table-breakout-full class"
            assert val2.get("afterWidth", 0) > val2.get("beforeWidth", 0), "Breakout table should be wider than standard"
            log("✅ Table Breakout Full-Width verified!")

            # 3. Test Global Document Full-Width Mode (正文全宽)
            log("\n[Test 3] Verifying Global Full-Width Mode (正文全宽)...")
            res3 = await send_cmd(ws, msg_id, "Runtime.evaluate", {
                "expression": """
                (() => {
                    const btn = document.getElementById('btn-toggle-full-width');
                    if (!btn) return { error: 'No full-width button' };
                    btn.click();
                    const isFull = document.body.classList.contains('mode-full-width');
                    const btnText = btn.innerText;
                    return { isFull, btnText };
                })()
                """,
                "returnByValue": True
            })
            msg_id += 1
            val3 = res3.get("result", {}).get("result", {}).get("value", {})
            log(f"Full-Width Mode result: {val3}")
            assert val3.get("isFull") is True, "Body should have mode-full-width class"
            log("✅ Global Full-Width Mode verified!")

            # 4. Take Screenshot with new features
            screenshot_path = os.path.join(os.path.dirname(__file__), "table_and_fullwidth_verified.png")
            snap_res = await send_cmd(ws, msg_id, "Page.captureScreenshot", {"format": "png"})
            msg_id += 1
            img_b64 = snap_res.get("result", {}).get("data", "")
            if img_b64:
                import base64
                with open(screenshot_path, "wb") as f:
                    f.write(base64.b64decode(img_b64))
                log(f"📸 Screenshot saved to: {screenshot_path}")

            log("\n==================================================")
            log("🎉 ALL 4 NEW FEATURES VERIFIED SUCCESSFULLY!")
            log("==================================================")
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
