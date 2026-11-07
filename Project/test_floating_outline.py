# -*- coding: utf-8 -*-
"""
Automated verification for:
1. Collapsed dashes showing top 2 levels (level-top and indented level-sub)
2. Outline default depth set to H3
3. Top header '大纲' button removed
4. Active dash highlight updating on page scroll
5. Editor focus-within background darkening to #050811 (rgb(5, 8, 17))
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

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
EDGE_PATH = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
HTML_PATH = os.path.join(ROOT_DIR, "Deliverables", "MarkScope.html")
CDP_PORT = 9988

async def send_cmd(ws, msg_id, method, params=None):
    payload = {"id": msg_id, "method": method}
    if params: payload["params"] = params
    await ws.send(json.dumps(payload))
    while True:
        resp = await ws.recv()
        data = json.loads(resp)
        if data.get("id") == msg_id:
            return data

def get_val(res):
    r = res.get("result", {})
    if "result" in r and "value" in r["result"]:
        return r["result"]["value"]
    if "value" in r:
        return r["value"]
    return {}

async def verify():
    print("=" * 60)
    print("🚀 Verifying 5 Enhancements (2-Level Dashes, H3 Default, Scroll Sync, Darkening)...")
    print("=" * 60)

    temp_profile = tempfile.mkdtemp(prefix="edge_outline2_test_")
    cmd = [
        EDGE_PATH, "--headless=new", f"--remote-debugging-port={CDP_PORT}",
        f"--user-data-dir={temp_profile}", "--disable-gpu", "--no-sandbox",
        "--window-size=1280,850", "about:blank"
    ]
    proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    try:
        time.sleep(1.2)
        with urllib.request.urlopen(f"http://127.0.0.1:{CDP_PORT}/json") as resp:
            targets = json.loads(resp.read().decode())
        ws_url = [t for t in targets if t.get("type") == "page"][0]["webSocketDebuggerUrl"]

        async with websockets.connect(ws_url, max_size=50*1024*1024) as ws:
            msg_id = 1
            await send_cmd(ws, msg_id, "Page.enable"); msg_id += 1
            await send_cmd(ws, msg_id, "Runtime.enable"); msg_id += 1

            file_url = pathlib.Path(HTML_PATH).as_uri()
            print(f"Navigating to {file_url}...")
            await send_cmd(ws, msg_id, "Page.navigate", {"url": file_url})
            msg_id += 1
            await asyncio.sleep(2.5)

            # Check 1: Top header no longer contains #btn-toggle-outline
            print("\n[Check 1] Verifying Top Header '大纲' Button is Removed...")
            res1 = await send_cmd(ws, msg_id, "Runtime.evaluate", {
                "expression": "document.getElementById('btn-toggle-outline') !== null",
                "returnByValue": True
            })
            msg_id += 1
            has_toggle_btn = get_val(res1)
            print(f"Has btn-toggle-outline: {has_toggle_btn}")
            assert has_toggle_btn is False, "Top header '大纲' button must be removed"
            print("✅ Check 1: Top header '大纲' button successfully removed!")

            # Check 2: Collapsed Dashes showing top 2 levels with level-top and level-sub
            print("\n[Check 2] Inspecting 2-Level Collapsed Dashes...")
            res2 = await send_cmd(ws, msg_id, "Runtime.evaluate", {
                "expression": """
                (() => {
                    const dashes = Array.from(document.querySelectorAll('.ms-dash'));
                    const topDashes = dashes.filter(d => d.classList.contains('level-top'));
                    const subDashes = dashes.filter(d => d.classList.contains('level-sub'));
                    const activeDashes = dashes.filter(d => d.classList.contains('active'));

                    return {
                        totalDashes: dashes.length,
                        topDashesCount: topDashes.length,
                        subDashesCount: subDashes.length,
                        activeDashesCount: activeDashes.length,
                        activeTitle: activeDashes[0] ? activeDashes[0].title : null,
                        titles: dashes.map(d => ({ title: d.title, isSub: d.classList.contains('level-sub') }))
                    };
                })()
                """,
                "returnByValue": True
            })
            msg_id += 1
            v2 = get_val(res2)
            print(f"Dashes 2-Level Info: {v2}")
            assert v2.get("totalDashes", 0) >= 2, "Expected multiple dashes across 2 levels"
            assert v2.get("topDashesCount", 0) >= 1, "Expected at least 1 top-level dash"
            assert v2.get("subDashesCount", 0) >= 1, "Expected at least 1 indented sub-level dash"
            assert v2.get("activeDashesCount") == 1, "Expected EXACTLY 1 active white dash (single point focus)"
            print("✅ Check 2: 2-Level dashes (top full length & sub indented) verified!")

            # Capture screenshot of 2-Level Collapsed Dashes
            snap1 = await send_cmd(ws, msg_id, "Page.captureScreenshot", {"format": "png"})
            msg_id += 1
            img1 = snap1.get("result", {}).get("data", "")
            if img1:
                with open(os.path.join(ROOT_DIR, "Project", "dashes_2level_verified.png"), "wb") as f:
                    f.write(base64.b64decode(img1))
                print("📸 Saved: Project/dashes_2level_verified.png")

            # Check 3: Default Outline Depth set to H3
            print("\n[Check 3] Expanding Panel and verifying Default Depth is H3...")
            res3 = await send_cmd(ws, msg_id, "Runtime.evaluate", {
                "expression": """
                (() => {
                    const pinBtn = document.getElementById('btn-pin-outline');
                    pinBtn.click(); // Pin panel

                    const activeDots = Array.from(document.querySelectorAll('.level-dot.active'));
                    const dotLevels = activeDots.map(d => parseInt(d.getAttribute('data-level')));
                    const items = Array.from(document.querySelectorAll('.float-outline-item'));
                    const visibleItems = items.filter(i => i.style.display !== 'none');
                    const hiddenItems = items.filter(i => i.style.display === 'none');

                    return {
                        activeDotCount: activeDots.length,
                        maxActiveLevel: Math.max(...dotLevels),
                        totalOutlineItems: items.length,
                        visibleCount: visibleItems.length,
                        hiddenCount: hiddenItems.length,
                        visibleLevels: visibleItems.map(i => i.getAttribute('data-level'))
                    };
                })()
                """,
                "returnByValue": True
            })
            msg_id += 1
            v3 = get_val(res3)
            print(f"Default Depth Info: {v3}")
            assert v3.get("maxActiveLevel") == 3, "Default active level must be H3"
            assert v3.get("activeDotCount") == 3, "Exactly 3 dots (1,2,3) should be active by default"
            assert all(int(lvl) <= 3 for lvl in v3.get("visibleLevels", [])), "All visible items must be <= H3"
            print("✅ Check 3: Default outline depth is H3 verified!")

            # Unpin panel back to collapsed state
            await send_cmd(ws, msg_id, "Runtime.evaluate", {
                "expression": "document.getElementById('btn-pin-outline').click()"
            })
            msg_id += 1
            await asyncio.sleep(0.3)

            # Check 4: Testing Page Scroll Sync (Dash Highlight Updates)
            print("\n[Check 4] Testing Scroll Sync (Scrolling to H2 section)...")
            res4 = await send_cmd(ws, msg_id, "Runtime.evaluate", {
                "expression": """
                (() => {
                    const h2 = document.querySelector('h2');
                    if (!h2) return { error: 'No H2 found' };
                    h2.scrollIntoView({ behavior: 'instant', block: 'start' });

                    // Trigger outline scroll handler
                    if (window.markScopeApp && window.markScopeApp.outline) {
                        window.markScopeApp.outline.updateActiveHeadingOnScroll();
                    }

                    // Check active dash after scroll
                    const dashes = Array.from(document.querySelectorAll('.ms-dash'));
                    const activeDash = document.querySelector('.ms-dash.active');
                    return {
                        scrolledH2Title: h2.textContent.trim(),
                        activeDashIndex: dashes.indexOf(activeDash),
                        activeDashTitle: activeDash ? activeDash.title : null
                    };
                })()
                """,
                "returnByValue": True
            })
            msg_id += 1
            v4 = get_val(res4)
            print(f"Scroll Result: {v4}")
            assert v4.get("activeDashIndex", 0) > 0, "Active dash should update from 0 to subsequent dash on scroll"
            print("✅ Check 4: Dash highlight real-time scroll sync verified!")

            # Check 5: Editor Focus-within Background Darkening
            print("\n[Check 5] Verifying Editor Focus Background Darkening to #050811...")
            res5 = await send_cmd(ws, msg_id, "Runtime.evaluate", {
                "expression": """
                (async () => {
                    const editorArea = document.querySelector('.vditor-ir .vditor-reset') ||
                                       document.querySelector('.vditor-reset[contenteditable="true"]') ||
                                       document.querySelector('.vditor-reset') ||
                                       document.getElementById('vditor-container');
                    const viewport = document.querySelector('.editor-viewport');
                    const initialBg = window.getComputedStyle(viewport).backgroundColor;

                    // Focus inside editor
                    if (window.markScopeApp && window.markScopeApp.vditor) {
                        window.markScopeApp.vditor.focus();
                    }
                    if (editorArea) {
                        editorArea.focus();
                    }

                    // Allow 300ms smooth CSS transition to complete
                    await new Promise(r => setTimeout(r, 380));

                    const focusedBg = window.getComputedStyle(viewport).backgroundColor;
                    const vditorResetBg = window.getComputedStyle(editorArea).backgroundColor;

                    return {
                        initialBg,
                        focusedBg,
                        vditorResetBg,
                        isDarkened: focusedBg === 'rgb(5, 8, 17)' || vditorResetBg === 'rgb(5, 8, 17)'
                    };
                })()
                """,
                "awaitPromise": True,
                "returnByValue": True
            })
            msg_id += 1
            v5 = get_val(res5)
            print(f"Focus Darkening Info: {v5}")
            assert v5.get("isDarkened") is True, "Background must darken to rgb(5, 8, 17) (#050811) on focus"
            print("✅ Check 5: Editor focus-within background darkening verified!")

            # Capture screenshot of focused editor state
            snap2 = await send_cmd(ws, msg_id, "Page.captureScreenshot", {"format": "png"})
            msg_id += 1
            img2 = snap2.get("result", {}).get("data", "")
            if img2:
                with open(os.path.join(ROOT_DIR, "Project", "editor_focus_darkened_verified.png"), "wb") as f:
                    f.write(base64.b64decode(img2))
                print("📸 Saved: Project/editor_focus_darkened_verified.png")

            print("\n" + "=" * 60)
            print("🎉 ALL 5 ENHANCEMENT CHECKS PASSED 100%!")
            print("=" * 60)
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
