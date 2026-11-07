# -*- coding: utf-8 -*-
import subprocess
import urllib.request
import urllib.parse
import json
import os
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

def get_github_token():
    input_data = "protocol=https\nhost=github.com\n".encode("utf-8")
    proc = subprocess.Popen(["git", "credential", "fill"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = proc.communicate(input_data)
    for line in out.decode("utf-8", errors="ignore").splitlines():
        if line.startswith("password="):
            return line[len("password="):].strip()
    return None

token = get_github_token()
if not token:
    print("❌ Error: Could not get GitHub token from git credential helper.")
    sys.exit(1)

repo = "wwbim/Mark-Scope"
tag = "v1.2610130030"
title = "Mark Scope v1.2610130030 - 100% 离线单文件 Markdown 编辑与阅读器"
body = """## 📝 Mark Scope v1.2610130030 正式版发布

> 💾 **100% 离线自包含单文件（附件下载直接双击运行）**  
> 🌐 **在线即刻体验 / GitHub Pages**: [https://wwbim.github.io/Mark-Scope/](https://wwbim.github.io/Mark-Scope/)  
> 📦 **单文件在线直达**: [https://wwbim.github.io/Mark-Scope/Deliverables/MarkScope.html](https://wwbim.github.io/Mark-Scope/Deliverables/MarkScope.html)

---

### 🌟 核心特色与技术亮点 / Highlights
1. **100% 离线单文件封装 (Standalone Single-File)**: 所有依赖（Lute、Highlight.js、KaTeX 数学字体、Mermaid、Ant 图标及样式）内嵌融铸为单一 `MarkScope.html`（~9MB），零网络请求、零外链依赖，双击即用。
2. **File System Access API 原生覆盖保存 (Ctrl+S)**: 打开或保存后自动与本地原文件绑定，按下 `Ctrl+S` 静默覆盖保存原文件，彻底告别重复生成下载副本的烦恼。
3. **毫秒级抗崩溃本地草稿容灾**: 内置 300ms 防抖本地持久化快照与 `beforeunload` 防误关拦截，意外关闭或断电重启后一键无损找回。
4. **智能表格自适应平衡排版与全宽突破**: 消除原生横向滚动条，自动根据内容体量计算最佳列宽比例，支持列宽分割线自由拖拽与单表全宽突破。
5. **浮动居中胶囊工具栏与全窗口物理居中标题**: 模式切换下沉至浮动岛，严格与正文版心居中对齐；标题栏文档名全窗口物理居中且防遮挡。
6. **880px 对称舒适阅读模式与右侧极简大纲**: 纯净阅读视图黄金版心排版，配备右侧微质感光晕大纲横条（Minimap），支持滚动实时高亮与快速跳转。
7. **PWA 渐进式应用安装与系统级文件关联**: 支持浏览器一键安装为独立桌面窗口，支持设为操作系统默认 `.md` 打开方式。

---

### 📦 资产下载 / Asset Download
- **`MarkScope.html`**: 核心单文件可执行文件（直接下载并在任意浏览器双击打开即可离线使用）。
"""

headers = {
    "Authorization": f"Bearer {token}",
    "Accept": "application/vnd.github.v3+json",
    "User-Agent": "MarkScope-Release-Script"
}

# 1. Create Release
print(f"Creating GitHub release for {tag} on {repo}...")
release_payload = json.dumps({
    "tag_name": tag,
    "target_commitish": "main",
    "name": title,
    "body": body,
    "draft": False,
    "prerelease": False
}).encode("utf-8")

req = urllib.request.Request(
    f"https://api.github.com/repos/{repo}/releases",
    data=release_payload,
    headers=headers,
    method="POST"
)

try:
    with urllib.request.urlopen(req) as resp:
        release_data = json.loads(resp.read().decode("utf-8"))
except urllib.error.HTTPError as e:
    err_body = e.read().decode("utf-8")
    print(f"Release creation returned {e.code}: {err_body}")
    # If release already exists, fetch it
    req_get = urllib.request.Request(f"https://api.github.com/repos/{repo}/releases/tags/{tag}", headers=headers)
    with urllib.request.urlopen(req_get) as resp:
        release_data = json.loads(resp.read().decode("utf-8"))

release_id = release_data["id"]
upload_url_template = release_data["upload_url"] # e.g. "https://uploads.github.com/repos/wwbim/Mark-Scope/releases/123/assets{?name,label}"
upload_base = upload_url_template.split("{")[0]
html_url = release_data.get("html_url", "")
print(f"✅ Release created/found: ID={release_id}, URL={html_url}")

# 2. Upload MarkScope.html asset
file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "Deliverables", "MarkScope.html"))
if not os.path.exists(file_path):
    # fallback to local Deliverables
    file_path = os.path.abspath("Deliverables/MarkScope.html")

print(f"Uploading standalone file: {file_path} ({os.path.getsize(file_path):,} bytes)...")
with open(file_path, "rb") as f:
    file_bytes = f.read()

asset_name = "MarkScope.html"
upload_url = f"{upload_base}?name={urllib.parse.quote(asset_name)}&label={urllib.parse.quote('MarkScope.html (Standalone Offline Viewer & Editor)')}"

upload_headers = {
    "Authorization": f"Bearer {token}",
    "Accept": "application/vnd.github.v3+json",
    "User-Agent": "MarkScope-Release-Script",
    "Content-Type": "text/html",
    "Content-Length": str(len(file_bytes))
}

upload_req = urllib.request.Request(
    upload_url,
    data=file_bytes,
    headers=upload_headers,
    method="POST"
)

try:
    with urllib.request.urlopen(upload_req) as resp:
        asset_data = json.loads(resp.read().decode("utf-8"))
        print(f"✅ Asset uploaded successfully!")
        print(f"   Download URL: {asset_data.get('browser_download_url')}")
        print(f"   Size: {asset_data.get('size'):,} bytes")
except urllib.error.HTTPError as e:
    err_body = e.read().decode("utf-8")
    print(f"❌ Asset upload failed ({e.code}): {err_body}")
    sys.exit(1)

print("\n🎉 GitHub Release published successfully!")
print(f"Release URL: {html_url}")
