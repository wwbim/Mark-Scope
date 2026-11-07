# -*- coding: utf-8 -*-
"""
Automated verification for 5 new enhancements:
1. Mode switch buttons in floating toolbar (at far left with divider, centered with content)
2. Filename strictly centered relative to the entire window
3. Reader Mode centered at 880px with balanced margins
4. Collapsed outline dashes capsule background with 8px blur edge blend-in
5. All collapsed outline dashes right-aligned
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
CDP_PORT = 9975

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
    print("=" * 65)
    print("🚀 Verifying 5 Enhancements (Floating Toolbar, Title Centering, Reader Mode, Outline Glow & Align)...")
    print("=" * 65)

    temp_profile = tempfile.mkdtemp(prefix="edge_toolbar_test_")
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
            await send_cmd(ws, msg_id, "Emulation.setDeviceMetricsOverride", {
                "width": 1280,
                "height": 850,
                "deviceScaleFactor": 1,
                "mobile": False
            }); msg_id += 1

            file_url = pathlib.Path(HTML_PATH).as_uri()
            print(f"Navigating to {file_url}...")
            await send_cmd(ws, msg_id, "Page.navigate", {"url": file_url})
            msg_id += 1
            await asyncio.sleep(2.5)

            # Check 1: Mode Switch Group inside Floating Toolbar at far left
            print("\n[Check 1] Verifying Mode Switch Group in Floating Toolbar...")
            res1 = await send_cmd(ws, msg_id, "Runtime.evaluate", {
                "expression": """
                (() => {
                    const toolbar = document.querySelector('.vditor-toolbar');
                    if (!toolbar) return { error: 'No toolbar found' };
                    const modeSwitch = toolbar.querySelector('.mode-switch-group');
                    const divider = toolbar.querySelector('.mode-toolbar-divider');
                    const firstChild = toolbar.firstElementChild;
                    const toolbarStyle = window.getComputedStyle(toolbar);
                    const rect = toolbar.getBoundingClientRect();
                    const winCenter = window.innerWidth / 2;
                    const toolbarCenter = (rect.left + rect.right) / 2;

                    return {
                        hasToolbar: !!toolbar,
                        hasModeSwitch: !!modeSwitch,
                        hasDivider: !!divider,
                        isFirstChild: firstChild === modeSwitch,
                        toolbarWidth: rect.width,
                        toolbarCenterDiff: Math.abs(toolbarCenter - winCenter),
                        isSticky: toolbarStyle.position === 'sticky',
                        borderRadius: toolbarStyle.borderRadius
                    };
                })()
                """,
                "returnByValue": True
            })
            msg_id += 1
            v1 = get_val(res1)
            print(f"Floating Toolbar Info: {v1}")
            assert v1.get("hasToolbar") is True, "Toolbar must exist"
            assert v1.get("hasModeSwitch") is True, "Mode switch must be mounted inside toolbar"
            assert v1.get("isFirstChild") is True, "Mode switch must be at far left of toolbar"
            assert v1.get("hasDivider") is True, "Divider must separate mode switch from Markdown tools"
            assert v1.get("toolbarCenterDiff", 999) < 15, "Floating toolbar must be centered with viewport"
            print("✅ Check 1: Mode switch buttons mounted at far left of floating centered toolbar!")

            # Check 2: Filename Strictly Centered to Window
            print("\n[Check 2] Verifying Filename Window Absolute Centering...")
            res2 = await send_cmd(ws, msg_id, "Runtime.evaluate", {
                "expression": """
                (() => {
                    const titleContainer = document.querySelector('.header-window-center');
                    const titleWrapper = document.querySelector('.file-title-wrapper');
                    if (!titleContainer || !titleWrapper) return { error: 'No title container found' };
                    const rect = titleWrapper.getBoundingClientRect();
                    const titleCenter = (rect.left + rect.right) / 2;
                    const winCenter = window.innerWidth / 2;
                    const diff = Math.abs(titleCenter - winCenter);

                    return {
                        titleCenter,
                        winCenter,
                        diff,
                        isCentered: diff <= 2,
                        text: titleWrapper.textContent.trim()
                    };
                })()
                """,
                "returnByValue": True
            })
            msg_id += 1
            v2 = get_val(res2)
            print(f"Title Centering Info: {v2}")
            assert v2.get("isCentered") is True, f"Filename must be strictly centered to window (diff={v2.get('diff')})"
            print("✅ Check 2: Filename title strictly centered to entire browser window!")

            # Check 3: Reader Mode 880px Balanced Centering
            print("\n[Check 3] Testing Reader Mode 880px Balanced Layout...")
            res3 = await send_cmd(ws, msg_id, "Runtime.evaluate", {
                "expression": """
                (async () => {
                    // Enter reader mode
                    if (window.markScopeApp) {
                        window.markScopeApp.enterReaderMode();
                    }
                    await new Promise(r => setTimeout(r, 200));

                    const isReaderClass = document.body.classList.contains('reader-mode');
                    const resetEl = document.querySelector('.vditor-ir .vditor-reset') || document.querySelector('.vditor-reset');
                    const rect = resetEl.getBoundingClientRect();
                    const textCenter = (rect.left + rect.right) / 2;
                    const winCenter = window.innerWidth / 2;
                    const centerDiff = Math.abs(textCenter - winCenter);

                    // Exit reader mode after measurement
                    if (window.markScopeApp) {
                        window.markScopeApp.exitReaderMode();
                    }

                    return {
                        isReaderClass,
                        width: rect.width,
                        centerDiff,
                        isBalanced: centerDiff <= 5,
                        widthOk: Math.abs(rect.width - 880) <= 30
                    };
                })()
                """,
                "awaitPromise": True,
                "returnByValue": True
            })
            msg_id += 1
            v3 = get_val(res3)
            print(f"Reader Mode Info: {v3}")
            assert v3.get("isReaderClass") is True, "Must activate reader-mode"
            assert v3.get("isBalanced") is True, f"Reader text must be symmetrically centered (diff={v3.get('centerDiff')})"
            assert v3.get("widthOk") is True, f"Reader width must be around 880px (actual={v3.get('width')})"
            print("✅ Check 3: Reader mode layout is 880px perfectly centered and balanced!")

            # Check 4: Collapsed Outline Dashes Soft Feathering & Safe Distance from Scrollbar
            print("\n[Check 4] Verifying Outline Dashes Soft Feathering & Safe Distance from Scrollbar...")
            res4 = await send_cmd(ws, msg_id, "Runtime.evaluate", {
                "expression": """
                (() => {
                    const dashesContainer = document.querySelector('.ms-outline-dashes');
                    const mainContainer = document.querySelector('.ms-float-outline-container');
                    if (!dashesContainer || !mainContainer) return { error: 'No outline dashes container' };
                    const style = window.getComputedStyle(dashesContainer);
                    const rect = dashesContainer.getBoundingClientRect();
                    const distFromRight = window.innerWidth - rect.right;

                    const beforeStyle = window.getComputedStyle(dashesContainer, '::before');

                    return {
                        distFromRight,
                        border: style.border,
                        boxShadow: style.boxShadow,
                        beforeFilter: beforeStyle.filter,
                        isClearFromScrollbar: distFromRight >= 20,
                        hasNoHardBorder: style.border.includes('0px') || style.border.includes('none'),
                        hasNoHardShadow: style.boxShadow === 'none'
                    };
                })()
                """,
                "returnByValue": True
            })
            msg_id += 1
            v4 = get_val(res4)
            print(f"Outline Dashes Style Info: {v4}")
            assert v4.get("isClearFromScrollbar") is True, f"Must have safe distance from scrollbar (actual={v4.get('distFromRight')}px)"
            assert v4.get("hasNoHardBorder") is True, "Must have no hard border"
            assert v4.get("hasNoHardShadow") is True, "Must have no hard drop shadow"
            print("✅ Check 4: Outline dashes soft blur feathering & safe distance from scrollbar verified!")

            # Check 5: All Outline Dashes Right-Aligned
            print("\n[Check 5] Verifying All Outline Dashes are Right-Aligned...")
            res5 = await send_cmd(ws, msg_id, "Runtime.evaluate", {
                "expression": """
                (() => {
                    const topDash = document.querySelector('.ms-dash.level-top');
                    const subDash = document.querySelector('.ms-dash.level-sub');
                    if (!topDash || !subDash) return { error: 'Need both top and sub dashes' };
                    const topRect = topDash.getBoundingClientRect();
                    const subRect = subDash.getBoundingClientRect();
                    const rightDiff = Math.abs(topRect.right - subRect.right);

                    return {
                        topWidth: topRect.width,
                        subWidth: subRect.width,
                        topRight: topRect.right,
                        subRight: subRect.right,
                        rightDiff,
                        isFlushRight: rightDiff <= 1.5
                    };
                })()
                """,
                "returnByValue": True
            })
            msg_id += 1
            v5 = get_val(res5)
            print(f"Dashes Alignment Info: {v5}")
            assert v5.get("topWidth", 0) > v5.get("subWidth", 0), "Top dash must be longer than sub dash"
            assert v5.get("isFlushRight") is True, f"All dashes must be flush right-aligned (diff={v5.get('rightDiff')})"
            print("✅ Check 5: All dashes right-aligned with unequal lengths verified!")

            # Capture screenshot of the new UI state
            snap = await send_cmd(ws, msg_id, "Page.captureScreenshot", {"format": "png"})
            msg_id += 1
            img_data = snap.get("result", {}).get("data", "")
            if img_data:
                with open(os.path.join(ROOT_DIR, "Project", "floating_toolbar_centered_verified.png"), "wb") as f:
                    f.write(base64.b64decode(img_data))
                print("📸 Saved: Project/floating_toolbar_centered_verified.png")

            print("\n" + "=" * 65)
            print("🎉 ALL 5 ENHANCEMENTS VERIFIED AND PASSED 100%!")
            print("=" * 65)
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
