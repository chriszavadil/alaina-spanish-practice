"""Keep the migration version assertions on files that contain literal versions."""
from pathlib import Path
p=Path(__file__).with_name('expand_history_scenarios.py')
s=p.read_text(encoding='utf-8')
a="for name in ['history-src/app.js','history-src/shell.html','history-src/sw.js']:"
b="for name in ['history-src/shell.html','history-src/sw.js']:"
if a in s:
 assert s.count(a)==1
 s=s.replace(a,b)
 p.write_text(s,encoding='utf-8')
else:assert b in s
# app.js reads VERSION from DATA.version; it has no hard-coded release number.
