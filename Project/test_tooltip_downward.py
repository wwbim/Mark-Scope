import asyncio, json, tempfile, subprocess, urllib.request, websockets, base64

async def test_tooltip():
    temp_profile = tempfile.mkdtemp()
    cmd = [
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        "--headless=new", "--remote-debugging-port=9978",
        f"--user-data-dir={temp_profile}", "--disable-gpu", "--no-sandbox",
        "--window-size=1280,850", "about:blank"
    ]
    proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        await asyncio.sleep(1.2)
        with urllib.request.urlopen("http://127.0.0.1:9978/json") as resp:
            targets = json.loads(resp.read().decode())
        ws_url = [t for t in targets if t.get("type") == "page"][0]["webSocketDebuggerUrl"]
        async with websockets.connect(ws_url) as ws:
            await ws.send(json.dumps({"id": 1, "method": "Emulation.setDeviceMetricsOverride", "params": {"width": 1280, "height": 850, "deviceScaleFactor": 1, "mobile": False}}))
            await ws.send(json.dumps({"id": 2, "method": "Page.navigate", "params": {"url": "file:///H:/我的云端硬盘/Software Develop/Mark Scope/Deliverables/MarkScope.html"}}))
            await asyncio.sleep(2.0)
            
            # Hover over a toolbar button, e.g. the bold button
            # Trigger class .vditor-tooltipped--hover or dispatch mouseover
            await ws.send(json.dumps({
                "id": 3,
                "method": "Runtime.evaluate",
                "params": {
                    "expression": """(() => {
                        const boldBtn = document.querySelector('.vditor-toolbar [data-type="bold"] button') || document.querySelector('.vditor-toolbar .vditor-tooltipped');
                        boldBtn.classList.add('vditor-tooltipped--hover');
                        const s = window.getComputedStyle(boldBtn, '::after');
                        const r = boldBtn.getBoundingClientRect();
                        return {
                            ariaLabel: boldBtn.getAttribute('aria-label'),
                            top: s.top,
                            bottom: s.bottom,
                            marginTop: s.marginTop,
                            btnRect: { top: r.top, bottom: r.bottom, height: r.height, left: r.left }
                        };
                    })()""",
                    "returnByValue": True
                }
            }))
            resp3 = await ws.recv()
            while True:
                data = json.loads(resp3)
                if data.get("id") == 3:
                    info = data["result"]["result"]["value"]
                    print("Tooltip info:", info)
                    break
                resp3 = await ws.recv()
            
            # Capture screenshot around toolbar with tooltip visible
            res_snap = {
                "id": 4,
                "method": "Page.captureScreenshot",
                "params": {
                    "clip": {
                        "x": 380, "y": 45, "width": 400, "height": 110, "scale": 2
                    }
                }
            }
            await ws.send(json.dumps(res_snap))
            while True:
                resp = await ws.recv()
                d = json.loads(resp)
                if d.get("id") == 4:
                    with open("Project/toolbar_tooltip_downward.png", "wb") as f:
                        f.write(base64.b64decode(d["result"]["data"]))
                    print("Saved: Project/toolbar_tooltip_downward.png")
                    break
    finally:
        proc.kill()
        proc.wait()

asyncio.run(test_tooltip())
