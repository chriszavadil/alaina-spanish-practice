"""Prepare exact migration assertions and a valid fresh-browser test fixture."""
from pathlib import Path
p=Path(__file__).with_name('expand_history_scenarios.py')
s=p.read_text(encoding='utf-8')
a="for name in ['history-src/app.js','history-src/shell.html','history-src/sw.js']:"
b="for name in ['history-src/shell.html','history-src/sw.js']:"
if a in s:
 assert s.count(a)==1
 s=s.replace(a,b)
else:assert b in s
# app.js reads VERSION from DATA.version; it has no hard-coded release number.
a="initial=db(p);initial['scenarioLast']"
b="initial=db(p) or {};initial['scenarioLast']"
if a in s:
 assert s.count(a)==1
 s=s.replace(a,b)
else:assert b in s
# A fresh app may not have written localStorage until the first study action.
# The load validator supplies defaults; this fixture only seeds the variant index.
p.write_text(s,encoding='utf-8')
