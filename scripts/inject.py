#!/usr/bin/env python3
"""template.html içindeki __T__ ve __W__ yerine timeline.json'u koyar → index.html
Kullanım: inject.py template.html timeline.json [index.html]"""
import json, sys
from pathlib import Path
tpl, tl = Path(sys.argv[1]), json.loads(Path(sys.argv[2]).read_text())
out = Path(sys.argv[3] if len(sys.argv) > 3 else tpl.with_name("index.html"))
out.write_text(tpl.read_text().replace("__T__", json.dumps(tl["T"])).replace("__W__", json.dumps(tl["W"], ensure_ascii=False)))
print(out)
