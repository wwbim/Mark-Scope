# -*- coding: utf-8 -*-
import os
import re

def safe_script(content):
    return re.sub(r'</script', r'<\/script', content, flags=re.IGNORECASE)

files = [
    'Project/libs/vditor/index.min.js',
    'Project/libs/vditor/js/lute/lute.min.js',
    'Project/libs/vditor/js/icons/ant.js',
    'Project/libs/vditor/js/highlight.js/highlight.min.js',
    'Project/libs/vditor/js/katex/katex.min.js',
    'Project/libs/vditor/js/mermaid/mermaid.min.js'
]

for f in files:
    with open(f, 'r', encoding='utf-8', errors='ignore') as fp:
        raw = fp.read()
    escaped = safe_script(raw)
    matches_before = len(re.findall(r'</script', raw, re.I))
    matches_after = len(re.findall(r'</script', escaped, re.I))
    print(f"{f}: before={matches_before}, after={matches_after}")
