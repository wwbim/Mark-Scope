# -*- coding: utf-8 -*-
"""
Download and extract Vditor distribution files into Project/libs/vditor.
Supports extracting core and requested offline bundles:
- Core: index.min.js, index.css, dist/css/content-theme/*
- Parser: dist/js/lute/lute.min.js
- Icons: dist/js/icons/ant.js
- KaTeX: dist/js/katex/*
- Mermaid: dist/js/mermaid/*
- Highlighting: dist/js/highlight.js/*
"""
import io
import os
import shutil
import tarfile
import urllib.request

VERSION = "3.11.3"  # Stable LTS branch of Vditor 3.x
URL = f"https://registry.npmjs.org/vditor/-/vditor-{VERSION}.tgz"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LIBS_DIR = os.path.join(BASE_DIR, "libs", "vditor")

def main():
    print(f"Downloading Vditor v{VERSION} from {URL}...")
    req = urllib.request.Request(URL, headers={"User-Agent": "MarkScope-Builder/1.0"})
    with urllib.request.urlopen(req) as resp:
        tar_bytes = resp.read()
    print(f"Downloaded {len(tar_bytes):,} bytes. Extracting to {LIBS_DIR}...")

    os.makedirs(LIBS_DIR, exist_ok=True)

    with tarfile.open(fileobj=io.BytesIO(tar_bytes)) as tf:
        members = tf.getmembers()
        prefix = "package/dist/"
        count = 0
        for m in members:
            if m.name.startswith(prefix) and not m.isdir():
                rel_path = m.name[len(prefix):]
                dest_path = os.path.join(LIBS_DIR, rel_path)
                os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                with tf.extractfile(m) as src_f, open(dest_path, "wb") as dst_f:
                    shutil.copyfileobj(src_f, dst_f)
                count += 1

    print(f"Extracted {count} files successfully into {LIBS_DIR}.")

if __name__ == "__main__":
    main()
