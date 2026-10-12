# -*- coding: utf-8 -*-
import asyncio, json, urllib.request, websockets, tempfile, subprocess, time, os, pathlib

PORT = 9944
temp_profile = tempfile.mkdtemp()
proc = subprocess.Popen([r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe', '--headless=new', f'--remote-debugging-port={PORT}', f'--user-data-dir={temp_profile}', 'about:blank'])
time.sleep(1)
try:
    with urllib.request.urlopen(f'http://127.0.0.1:{PORT}/json') as r:
        targets = json.loads(r.read().decode())
    ws_url = [t for t in targets if t.get('type') == 'page'][0]['webSocketDebuggerUrl']
    async def run():
        async with websockets.connect(ws_url) as ws:
            file_url = pathlib.Path(r'Deliverables\MarkScope.html').resolve().as_uri()
            await ws.send(json.dumps({'id': 1, 'method': 'Page.navigate', 'params': {'url': file_url}}))
            await asyncio.sleep(2)
            await ws.send(json.dumps({'id': 2, 'method': 'Runtime.evaluate', 'params': {
                'expression': '''
                JSON.stringify((() => {
                    const el = document.getElementById('vditor-container');
                    const table = el.querySelector('table');
                    return {
                        tableParentTag: table ? table.parentElement.tagName : 'no table',
                        tableParentClass: table ? table.parentElement.className : 'no table',
                        tableWidth: table ? table.offsetWidth : 0,
                        contentWidth: document.querySelector('.vditor-content') ? document.querySelector('.vditor-content').offsetWidth : 0,
                        irWidth: document.querySelector('.vditor-ir') ? document.querySelector('.vditor-ir').offsetWidth : 0
                    };
                })())
                '''
            }}))
            while True:
                res = await ws.recv()
                data = json.loads(res)
                if data.get('id') == 2:
                    print(data.get('result', {}).get('result', {}).get('value'))
                    break
    asyncio.run(run())
finally:
    proc.kill()
