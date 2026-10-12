# -*- coding: utf-8 -*-
r"""
=============================================================================
Mark Scope - Standalone Single-File Offline Builder
=============================================================================
Compiles all HTML, CSS, JS and offline third-party libraries (Vditor, Lute,
KaTeX, Mermaid, Highlight.js, Ant Icons) into a single 100% self-contained
offline executable HTML file:
  - Deliverables/MarkScope.html
  - Deliverables/index.html (mirror entry)
Author: WWBIM / Mark Scope Team
"""
import base64
import os
import re
import shutil
import sys
import time

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(BASE_DIR, "src")
LIBS_DIR = os.path.join(BASE_DIR, "libs", "vditor")
ROOT_DIR = os.path.dirname(BASE_DIR)
DELIVERABLES_DIR = os.path.join(ROOT_DIR, "Deliverables")

def read_text(path):
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()

def read_binary_b64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("ascii")

def safe_script(js_content):
    """
    Prevents browser HTML parser from prematurely closing script tags
    when JS code contains literal '</script>'.
    """
    return re.sub(r'</script', r'<\/script', js_content, flags=re.IGNORECASE)

def build_katex_css_with_fonts():
    """
    Inlines all KaTeX .woff2 fonts as Base64 data URIs so that math
    rendering works 100% offline with zero missing glyphs.
    """
    css_path = os.path.join(LIBS_DIR, "js", "katex", "katex.min.css")
    css = read_text(css_path)
    fonts_dir = os.path.join(LIBS_DIR, "js", "katex", "fonts")

    def replace_font(match):
        font_file = match.group(1)
        if font_file.endswith(".woff2"):
            full_font_path = os.path.join(fonts_dir, font_file)
            if os.path.exists(full_font_path):
                b64 = read_binary_b64(full_font_path)
                return f"url('data:font/woff2;base64,{b64}')"
        return match.group(0)

    css_embedded = re.sub(r'url\(["\']?fonts/([^)"\']+)["\']?\)', replace_font, css)
    return css_embedded

def build_mark_scope():
    print("=" * 60)
    print("🚀 Starting Mark Scope Single-File Build Pipeline...")
    print("=" * 60)
    start_time = time.time()

    # 1. Verify existence of required libs
    required_libs = [
        os.path.join(LIBS_DIR, "index.min.js"),
        os.path.join(LIBS_DIR, "index.css"),
        os.path.join(LIBS_DIR, "js", "lute", "lute.min.js"),
        os.path.join(LIBS_DIR, "js", "icons", "ant.js"),
        os.path.join(LIBS_DIR, "js", "highlight.js", "highlight.min.js"),
        os.path.join(LIBS_DIR, "js", "katex", "katex.min.js"),
        os.path.join(LIBS_DIR, "js", "mermaid", "mermaid.min.js"),
    ]
    for lib in required_libs:
        if not os.path.exists(lib):
            print(f"❌ Error: Missing required library file: {lib}")
            sys.exit(1)

    # 2. Read Source Files
    print("[1/5] Reading application source components...")
    html_template = read_text(os.path.join(SRC_DIR, "index.html"))
    shell_css = read_text(os.path.join(SRC_DIR, "styles.css"))
    draft_manager_js = read_text(os.path.join(SRC_DIR, "draft_manager.js"))
    file_io_js = read_text(os.path.join(SRC_DIR, "file_io.js"))
    outline_js = read_text(os.path.join(SRC_DIR, "outline.js"))
    table_manager_js = read_text(os.path.join(SRC_DIR, "table_manager.js"))
    statusbar_js = read_text(os.path.join(SRC_DIR, "statusbar.js"))
    app_js = read_text(os.path.join(SRC_DIR, "app.js"))

    # 3. Read & Prepare Third-party Dependencies
    print("[2/5] Reading and packaging offline third-party dependencies...")
    vditor_css = read_text(os.path.join(LIBS_DIR, "index.css"))
    vditor_js = read_text(os.path.join(LIBS_DIR, "index.min.js"))
    lute_js = read_text(os.path.join(LIBS_DIR, "js", "lute", "lute.min.js"))
    ant_icons_js = read_text(os.path.join(LIBS_DIR, "js", "icons", "ant.js"))
    hljs_js = read_text(os.path.join(LIBS_DIR, "js", "highlight.js", "highlight.min.js"))
    hljs_css = read_text(os.path.join(LIBS_DIR, "js", "highlight.js", "styles", "atom-one-dark.min.css"))
    katex_js = read_text(os.path.join(LIBS_DIR, "js", "katex", "katex.min.js"))
    katex_css = build_katex_css_with_fonts()
    mermaid_js = read_text(os.path.join(LIBS_DIR, "js", "mermaid", "mermaid.min.js"))

    # 4. Assemble Single HTML
    print("[3/5] Inlining assets and applying script safety escapes...")
    out_html = html_template

    # Replace CSS placeholders
    out_html = out_html.replace("/* __INLINE_VDITOR_CSS__ */", vditor_css)
    out_html = out_html.replace("/* __INLINE_KATEX_CSS__ */", katex_css)
    out_html = out_html.replace("/* __INLINE_HLJS_CSS__ */", hljs_css)
    out_html = out_html.replace("/* __INLINE_SHELL_CSS__ */", shell_css)

    # Replace JS placeholders with safe_script
    out_html = out_html.replace("/* __INLINE_LUTE_JS__ */", safe_script(lute_js))
    out_html = out_html.replace("/* __INLINE_ANT_ICONS_JS__ */", safe_script(ant_icons_js))
    out_html = out_html.replace("/* __INLINE_HLJS_JS__ */", safe_script(hljs_js))
    out_html = out_html.replace("/* __INLINE_KATEX_JS__ */", safe_script(katex_js))
    out_html = out_html.replace("/* __INLINE_MERMAID_JS__ */", safe_script(mermaid_js))
    out_html = out_html.replace("/* __INLINE_VDITOR_JS__ */", safe_script(vditor_js))

    # Replace Application Scripts
    out_html = out_html.replace("/* __INLINE_DRAFT_MANAGER_JS__ */", safe_script(draft_manager_js))
    out_html = out_html.replace("/* __INLINE_FILE_IO_JS__ */", safe_script(file_io_js))
    out_html = out_html.replace("/* __INLINE_OUTLINE_JS__ */", safe_script(outline_js))
    out_html = out_html.replace("/* __INLINE_TABLE_MANAGER_JS__ */", safe_script(table_manager_js))
    out_html = out_html.replace("/* __INLINE_STATUSBAR_JS__ */", safe_script(statusbar_js))
    out_html = out_html.replace("/* __INLINE_APP_JS__ */", safe_script(app_js))

    # 5. Write to Deliverables
    print("[4/5] Writing production deliverables...")
    os.makedirs(DELIVERABLES_DIR, exist_ok=True)
    mark_scope_path = os.path.join(DELIVERABLES_DIR, "MarkScope.html")
    index_path = os.path.join(DELIVERABLES_DIR, "index.html")

    with open(mark_scope_path, "w", encoding="utf-8") as f:
        f.write(out_html)

    shutil.copyfile(mark_scope_path, index_path)

    elapsed = time.time() - start_time
    file_size_mb = os.path.getsize(mark_scope_path) / (1024 * 1024)

    print("[5/5] Build Completed Successfully!")
    print(f"  📁 Output HTML: {mark_scope_path}")
    print(f"  📁 Mirror HTML: {index_path}")
    print(f"  📦 Total Size : {file_size_mb:.2f} MB ({os.path.getsize(mark_scope_path):,} bytes)")
    print(f"  ⏱️ Time Elapsed: {elapsed:.2f} seconds")
    print("=" * 60)
    return mark_scope_path

if __name__ == "__main__":
    build_mark_scope()
