"""Audit exact preservation and the rendered sixty-scenario payload."""
from pathlib import Path
import json,subprocess,hashlib,re
r=Path(__file__).resolve().parents[1];base='4be9257df1a506c749b96396469fffcbcb2f113a'
def old(f):return subprocess.check_output(['git','show',base+':'+f],cwd=r).decode('utf-8')
d=json.loads((r/'history-src/data.json').read_text());prior=json.loads(old('history-src/data.json'))
assert d['version']=='1.1.1' and len(d['cards'])==15
for c,o in zip(d['cards'],prior['cards']):
 assert c['id']==o['id'] and len(c['scenarios'])==4 and c['scenarios'][:2]==o['scenarios']
 assert {k:v for k,v in c.items() if k!='scenarios'}=={k:v for k,v in o.items() if k!='scenarios'}
assert d['sources']==prior['sources'] and d['categories']==prior['categories']
texts=[s['text'] for c in d['cards'] for s in c['scenarios']];assert len(texts)==len(set(texts))==60
h=(r/'history/index.html').read_text();assert h==(r/'docs/history/index.html').read_text()
assert json.loads(re.search(r'<script id="history-data" type="application/json">(.*?)</script>',h,re.S)[1])==d
assert '60 illustrative situations' in h and 'Four different examples for every word.' in h
assert '30 illustrative situations' not in h and 'Two illustrative situations' not in h
# Code changes are restricted to UI count labels; existing rotation, saved-round and grading logic remain identical.
a=old('history-src/app.js').replace('30 illustrative situations','60 illustrative situations').replace('Two different examples for every word.','Four different examples for every word.').replace('Two illustrative situations showing this word in context.','Four illustrative situations showing this word in context.').replace('two per term','four per term')
assert (r/'history-src/app.js').read_text()==a
assert (r/'history-src/core.js').read_text()==old('history-src/core.js')
span=['index.html','docs/index.html','src/core.js','src/data.json','src/unit2.json','sw.js','docs/sw.js','manifest.webmanifest','docs/manifest.webmanifest']
for f in span:assert (r/f).read_text()==old(f),f
p=r/'SCENARIO_EXPANSION_BUILD.json';proof=json.loads(p.read_text());proof['history_sha256']=hashlib.sha256(h.encode()).hexdigest();proof['content_audit_passed']=True;p.write_text(json.dumps(proof,indent=2)+'\n')
print('AUDIT PASS: 60 distinct scenarios, 30 originals preserved, four per term, rotation/grading/storage logic unchanged, Spanish assets identical.',flush=True)
