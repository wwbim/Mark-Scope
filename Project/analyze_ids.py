# -*- coding: utf-8 -*-
import re

with open('Project/libs/vditor/index.js', 'r', encoding='utf-8') as f:
    content = f.read()

# Search for any string ending in 'Script' or 'Style' or matching dist/js
matches = re.findall(r'[\'"]([a-zA-Z0-9_-]*(?:Script|Style)[a-zA-Z0-9_-]*)[\'"]', content)
print("Matches with Script/Style in name:")
for m in sorted(set(matches)):
    print(" -", m)

paths = re.findall(r'[\'"](/dist/[^\'"]+)[\'"]', content)
print("\nPaths with /dist/:")
for p in sorted(set(paths)):
    print(" -", p)
