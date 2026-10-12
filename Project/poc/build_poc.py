# -*- coding: utf-8 -*-
"""
Build script for Proof-of-Concept: 100% Offline Single-File Vditor instantiation.
"""
import base64
import os
import re

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LIBS_DIR = os.path.join(BASE_DIR, "libs", "vditor")
POC_DIR = os.path.join(BASE_DIR, "poc")
os.makedirs(POC_DIR, exist_ok=True)

def read_file(rel_path):
    p = os.path.join(LIBS_DIR, rel_path)
    with open(p, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()

def safe_script(js):
    return re.sub(r'</script', r'<\/script', js, flags=re.IGNORECASE)

def read_binary_b64(rel_path):
    p = os.path.join(LIBS_DIR, rel_path)
    with open(p, "rb") as f:
        return base64.b64encode(f.read()).decode("ascii")

def build_katex_css_with_fonts():
    css = read_file("js/katex/katex.min.css")
    def replace_font(match):
        font_file = match.group(1)
        if font_file.endswith(".woff2"):
            font_path = os.path.join("js", "katex", "fonts", font_file)
            if os.path.exists(os.path.join(LIBS_DIR, font_path)):
                b64 = read_binary_b64(font_path)
                return f"url('data:font/woff2;base64,{b64}')"
        return match.group(0)

    css_embedded = re.sub(r'url\(["\']?fonts/([^)"\']+)["\']?\)', replace_font, css)
    return css_embedded

SAMPLE_MD = r"""# 📝 欢迎体验 Mark Scope 离线单文件编辑器

Mark Scope 是 100% 离线单文件运行的现代化 Markdown 所见即所得编辑器。

---

## ⚡ 离线核心能力验证

### 1. 🧮 KaTeX 数学公式渲染
行内公式：质能方程为 $E = mc^2$，高斯积分 $\int_{-\infty}^{\infty} e^{-x^2} dx = \sqrt{\pi}$。

块级公式：
$$
f(x) = \frac{1}{\sigma \sqrt{2\pi}} e^{-\frac{1}{2} \left(\frac{x - \mu}{\sigma}\right)^2}
$$

### 2. 📊 Mermaid 流程图与图表
```mermaid
graph LR
    A[本地 .md 文件] --> B(Mark Scope 离线引擎)
    B --> C{所见即所得 / 即时渲染}
    C --> D[零网络依赖 100% 隐私安全]
    C --> E[一键保存/导出 HTML/PDF]
```

### 3. 💻 语法高亮代码块
```python
def mark_scope_offline_guard():
    status = "100% Client-Side Offline"
    print(f"Status: {status} - Zero Server Required!")
    return True
```

### 4. 📋 任务列表与表格
- [x] 验证 Lute 核心离线解析
- [x] 验证 Mermaid 离线拓扑图
- [x] 验证 KaTeX 离线公式矢量排版
- [x] 验证 代码语法高亮

| 功能项 | 离线支持 | 网络请求 | 表现状态 |
| :--- | :---: | :---: | :---: |
| Lute AST | 100% | 0 | 正常运作 |
| Math KaTeX | 100% | 0 | 矢量清晰 |
| Mermaid 图表 | 100% | 0 | 实时绘制 |
| Ant 图标库 | 100% | 0 | 矢量显示 |
"""

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Mark Scope - Offline PoC Test</title>
  <!-- Vditor Core CSS -->
  <style id="vditorIndexStyle">
__VDITOR_CSS__
  </style>
  <!-- KaTeX CSS with Base64 Fonts -->
  <style id="vditorKatexStyle">
__KATEX_CSS__
  </style>
  <!-- Highlight.js CSS -->
  <style id="vditorHljsStyle">
__HLJS_CSS__
  </style>
  <style>
    body {
      margin: 0;
      padding: 20px;
      background-color: #1a1e24;
      color: #e2e8f0;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }
    .poc-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 16px;
      padding-bottom: 12px;
      border-bottom: 1px solid #2d3748;
    }
    .poc-header h1 {
      margin: 0;
      font-size: 20px;
      font-weight: 600;
      color: #60a5fa;
    }
    .poc-status {
      font-size: 13px;
      padding: 4px 10px;
      border-radius: 4px;
      background: #065f46;
      color: #34d399;
      font-weight: 500;
    }
    #vditor-container {
      border: 1px solid #334155;
      border-radius: 8px;
      overflow: hidden;
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4);
    }
  </style>
</head>
<body>

  <div class="poc-header">
    <h1>📝 Mark Scope - 100% 离线单文件可行性验证 (PoC)</h1>
    <div id="poc-status" class="poc-status">⏳ 正在初始化 Vditor...</div>
  </div>

  <div id="vditor-container"></div>

  <!-- Inline Core Parser & Libraries with standard IDs -->
  <script id="vditorLuteScript">
__LUTE_JS__
  </script>
  <script id="vditorIconScript">
__ANT_ICONS_JS__
  </script>
  <script id="vditorHljsScript">
__HLJS_JS__
  </script>
  <script id="vditorKatexScript">
__KATEX_JS__
  </script>
  <script id="vditorMermaidScript">
__MERMAID_JS__
  </script>

  <!-- Vditor Core Bundle -->
  <script id="vditorCoreScript">
__VDITOR_JS__
  </script>

  <!-- PoC Initialization Logic -->
  <script>
    const sampleMarkdown = __SAMPLE_MD_JSON__;

    window.addEventListener('DOMContentLoaded', () => {
      try {
        console.log("Checking prerequisites:", {
          hasLute: typeof window.Lute !== 'undefined',
          hasVditor: typeof window.Vditor !== 'undefined',
          hasKatex: typeof window.katex !== 'undefined',
          hasMermaid: typeof window.mermaid !== 'undefined',
          hasHljs: typeof window.hljs !== 'undefined'
        });

        const vditor = new Vditor('vditor-container', {
          value: sampleMarkdown,
          mode: 'ir', // 即时渲染模式 (Typora 风格)
          theme: 'dark',
          preview: {
            theme: {
              current: 'dark'
            },
            hljs: {
              style: 'atom-one-dark',
              lineNumber: true
            },
            math: {
              engine: 'KaTeX'
            }
          },
          toolbarConfig: {
            pin: true
          },
          cache: {
            enable: false
          },
          after: () => {
            const statusEl = document.getElementById('poc-status');
            statusEl.innerText = "✅ PoC 验证成功：100% 离线单文件运行就绪！";
            statusEl.style.background = "#065f46";
            statusEl.style.color = "#34d399";
            console.log("Vditor loaded successfully in 100% offline mode!");
          }
        });
      } catch (err) {
        console.error("PoC Init Error:", err);
        const statusEl = document.getElementById('poc-status');
        statusEl.innerText = "❌ 初始化失败: " + err.message;
        statusEl.style.background = "#7f1d1d";
        statusEl.style.color = "#f87171";
      }
    });
  </script>
</body>
</html>
"""

def main():
    import json
    print("Reading libraries...")
    vditor_css = read_file("index.css")
    vditor_js = read_file("index.min.js")
    lute_js = read_file("js/lute/lute.min.js")
    ant_icons_js = read_file("js/icons/ant.js")
    hljs_js = read_file("js/highlight.js/highlight.min.js")
    hljs_css = read_file("js/highlight.js/styles/atom-one-dark.min.css")
    katex_js = read_file("js/katex/katex.min.js")
    katex_css = build_katex_css_with_fonts()
    mermaid_js = read_file("js/mermaid/mermaid.min.js")

    poc_html_path = os.path.join(POC_DIR, "poc_offline_vditor.html")

    html = HTML_TEMPLATE.replace("__VDITOR_CSS__", vditor_css)
    html = html.replace("__KATEX_CSS__", katex_css)
    html = html.replace("__HLJS_CSS__", hljs_css)
    html = html.replace("__LUTE_JS__", safe_script(lute_js))
    html = html.replace("__ANT_ICONS_JS__", safe_script(ant_icons_js))
    html = html.replace("__HLJS_JS__", safe_script(hljs_js))
    html = html.replace("__KATEX_JS__", safe_script(katex_js))
    html = html.replace("__MERMAID_JS__", safe_script(mermaid_js))
    html = html.replace("__VDITOR_JS__", safe_script(vditor_js))
    html = html.replace("__SAMPLE_MD_JSON__", json.dumps(SAMPLE_MD))

    with open(poc_html_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"PoC built successfully: {poc_html_path}")
    print(f"File size: {os.path.getsize(poc_html_path):,} bytes ({os.path.getsize(poc_html_path)/1024/1024:.2f} MB)")

if __name__ == "__main__":
    main()
