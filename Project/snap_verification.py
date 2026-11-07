import asyncio, json, tempfile, subprocess, urllib.request, websockets, base64

async def snap():
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
            
            # Click pin button to keep outline open
            await ws.send(json.dumps({
                "id": 3,
                "method": "Runtime.evaluate",
                "params": {
                    "expression": "document.getElementById('btn-pin-outline').click()"
                }
            }))
            await asyncio.sleep(0.3)
            
            # Snap 1: level slider closeup
            res_slider = {
                "id": 4,
                "method": "Page.captureScreenshot",
                "params": {
                    "clip": {
                        "x": 995, "y": 335, "width": 260, "height": 40, "scale": 3
                    }
                }
            }
            await ws.send(json.dumps(res_slider))
            while True:
                resp = await ws.recv()
                d = json.loads(resp)
                if d.get("id") == 4:
                    with open("Project/slider_dots_perfect.png", "wb") as f:
                        f.write(base64.b64decode(d["result"]["data"]))
                    break
                    
            # Snap 2: Header title badge closeup
            res_title = {
                "id": 5,
                "method": "Page.captureScreenshot",
                "params": {
                    "clip": {
                        "x": 500, "y": 0, "width": 280, "height": 50, "scale": 3
                    }
                }
            }
            await ws.send(json.dumps(res_title))
            while True:
                resp = await ws.recv()
                d = json.loads(resp)
                if d.get("id") == 5:
                    with open("Project/title_badge_perfect.png", "wb") as f:
                        f.write(base64.b64decode(d["result"]["data"]))
                    break
                    
            # Snap 3: Toolbar & seamless background
            res_tb = {
                "id": 6,
                "method": "Page.captureScreenshot",
                "params": {
                    "clip": {
                        "x": 128, "y": 30, "width": 1024, "height": 110, "scale": 1
                    }
                }
            }
            await ws.send(json.dumps(res_tb))
            while True:
                resp = await ws.recv()
                d = json.loads(resp)
                if d.get("id") == 6:
                    with open("Project/toolbar_seamless_perfect.png", "wb") as f:
                        f.write(base64.b64decode(d["result"]["data"]))
                    break
    finally:
        proc.kill()
        proc.wait()

asyncio.run(snap())
