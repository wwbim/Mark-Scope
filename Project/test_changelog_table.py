# -*- coding: utf-8 -*-
"""
Verification test specifically targeting CHANGELOG.md table rendering:
- Eliminates horizontal scrollbar
- Adaptive column balancing on real-world long milestone text
- Interactive column resize handle functionality
- Screenshot capture
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
CHANGELOG_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "Deliverables", "CHANGELOG.md"))
PORT = 9993

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
    temp_profile = tempfile.mkdtemp(prefix="edge_changelog_test_")
    cmd = [
        EDGE_PATH, "--headless=new", f"--remote-debugging-port={PORT}",
        f"--user-data-dir={temp_profile}", "--disable-gpu", "--no-sandbox",
        "--window-size=1280,850", "--allow-file-access-from-files", "about:blank"
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
            log(f"Navigating to {file_url}...")
            await send_cmd(ws, msg_id, "Page.navigate", {"url": file_url}); msg_id += 1
            await asyncio.sleep(2.0)

            # Read CHANGELOG content
            with open(CHANGELOG_PATH, "r", encoding="utf-8") as f:
                changelog_text = f.read()

            log("Loading CHANGELOG.md into Mark Scope...")
            await send_cmd(ws, msg_id, "Runtime.evaluate", {
                "expression": f"window.markScopeApp.loadDocument({json.dumps(changelog_text)}, 'CHANGELOG.md')"
            })
            msg_id += 1
            await asyncio.sleep(1.2)

            # Inspect CHANGELOG table
            log("\n[Check 1] Inspecting CHANGELOG Table in DOM...")
            res1 = await send_cmd(ws, msg_id, "Runtime.evaluate", {
                "expression": """
                (() => {
                    const table = document.querySelector('table');
                    if (!table) return { error: 'No table found in CHANGELOG.md' };

                    const ths = Array.from(table.querySelectorAll('th'));
                    const cols = Array.from(table.querySelectorAll('col'));
                    const resizers = Array.from(table.querySelectorAll('.ms-col-resizer'));

                    const resizerHeights = resizers.map(r => r.offsetHeight);
                    const colWidths = (cols.length > 0 ? cols : ths).map(c => c.style.width);

                    return {
                        colCount: ths.length,
                        colWidths: colWidths,
                        tableDisplay: window.getComputedStyle(table).display,
                        tableLayout: window.getComputedStyle(table).tableLayout,
                        scrollWidth: table.scrollWidth,
                        clientWidth: table.clientWidth,
                        hasHorizontalOverflow: table.scrollWidth > table.clientWidth + 2,
                        resizerCount: resizers.length,
                        resizerHeights: resizerHeights
                    };
                })()
                """,
                "returnByValue": True
            })
            msg_id += 1
            val1 = res1.get("result", {}).get("result", {}).get("value", {})
            log(f"CHANGELOG Table Data: {val1}")

            assert val1.get("colCount") == 4, "Expected 4 columns in CHANGELOG table"
            assert val1.get("tableDisplay") == "table", "Expected display: table"
            assert val1.get("tableLayout") == "fixed", "Expected table-layout: fixed"
            assert val1.get("hasHorizontalOverflow") is False, "Expected ZERO horizontal scrollbar on table!"
            assert all(h > 15 for h in val1.get("resizerHeights", [])), "Expected all resizer handles to have height > 15px!"
            log("✅ Table Display, Fixed Layout, and ZERO Horizontal Overflow Confirmed!")

            # Simulate interactive column resizing via drag
            log("\n[Check 2] Simulating Column Drag Resizing...")
            res2 = await send_cmd(ws, msg_id, "Runtime.evaluate", {
                "expression": """
                (() => {
                    const table = document.querySelector('table');
                    const resizer = table.querySelector('.ms-col-resizer');
                    if (!resizer) return { error: 'No resizer' };

                    const rect = resizer.getBoundingClientRect();
                    const startX = rect.left + rect.width / 2;
                    const startY = rect.top + rect.height / 2;

                    // Trigger mousedown
                    resizer.dispatchEvent(new MouseEvent('mousedown', {
                        clientX: startX,
                        clientY: startY,
                        bubbles: true,
                        cancelable: true
                    }));

                    // Trigger mousemove with +50px drag to the right
                    window.dispatchEvent(new MouseEvent('mousemove', {
                        clientX: startX + 50,
                        clientY: startY,
                        bubbles: true,
                        cancelable: true
                    }));

                    // Trigger mouseup
                    window.dispatchEvent(new MouseEvent('mouseup', {
                        clientX: startX + 50,
                        clientY: startY,
                        bubbles: true,
                        cancelable: true
                    }));

                    const cols = Array.from(table.querySelectorAll('col'));
                    return {
                        col0Width: cols[0] ? cols[0].style.width : '',
                        col1Width: cols[1] ? cols[1].style.width : '',
                        customSet: table.dataset.customColWidths === 'true'
                    };
                })()
                """,
                "returnByValue": True
            })
            msg_id += 1
            val2 = res2.get("result", {}).get("result", {}).get("value", {})
            log(f"Drag resize result: {val2}")
            assert val2.get("customSet") is True, "Table should record customColWidths after drag"
            log("✅ Column drag resizing verified!")

            # Simulate double-click to reset back to auto-balanced widths
            log("\n[Check 3] Simulating Double-Click to Reset Balanced Widths...")
            res3 = await send_cmd(ws, msg_id, "Runtime.evaluate", {
                "expression": """
                (() => {
                    const table = document.querySelector('table');
                    const resizer = table.querySelector('.ms-col-resizer');
                    resizer.dispatchEvent(new MouseEvent('dblclick', { bubbles: true, cancelable: true }));

                    const cols = Array.from(table.querySelectorAll('col'));
                    return {
                        colWidthsAfterReset: cols.map(c => c.style.width),
                        customCleared: !table.dataset.customColWidths
                    };
                })()
                """,
                "returnByValue": True
            })
            msg_id += 1
            val3 = res3.get("result", {}).get("result", {}).get("value", {})
            log(f"Reset result: {val3}")
            assert val3.get("customCleared") is True, "Double-click should clear customColWidths"
            log("✅ Double-click reset verified!")

            # Scroll to table and take screenshot
            await send_cmd(ws, msg_id, "Runtime.evaluate", {
                "expression": "document.querySelector('table').scrollIntoView({ behavior: 'instant', block: 'center' })"
            })
            msg_id += 1
            await asyncio.sleep(0.5)

            screenshot_path = os.path.join(os.path.dirname(__file__), "changelog_table_verified.png")
            snap_res = await send_cmd(ws, msg_id, "Page.captureScreenshot", {"format": "png"})
            msg_id += 1
            img_b64 = snap_res.get("result", {}).get("data", "")
            if img_b64:
                with open(screenshot_path, "wb") as f:
                    f.write(base64.b64decode(img_b64))
                log(f"📸 Screenshot saved to: {screenshot_path}")

            log("\n==================================================")
            log("🎉 CHANGELOG TABLE TESTS ALL PASSED 100%!")
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
