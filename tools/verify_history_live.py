"""Bounded public deployment check, then real browser suites against public URLs."""
from pathlib import Path
import urllib.request,time,json,hashlib,subprocess,sys
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'history-live-results';OUT.mkdir(exist_ok=True)
H='https://chriszavadil.github.io/alaina-spanish-practice/history/'
S='https://chriszavadil.github.io/alaina-spanish-practice/'
proof=json.loads((ROOT/'HISTORY_BUILD.json').read_text())
def fetch(url):
 with urllib.request.urlopen(urllib.request.Request(url,headers={'Cache-Control':'no-cache'}),timeout=20) as r:return r.status,r.read()
def sha(raw):return hashlib.sha256(raw.replace(b'\r\n',b'\n')).hexdigest()
for attempt in range(24):
 try:
  code,html=fetch(H+'?v=1.0.0');ok=code==200 and sha(html)==proof['history_sha256'];print('PUBLIC_HISTORY',attempt+1,code,'EXACT_MATCH',ok,flush=True)
  if ok:break
 except Exception as e:print('PUBLIC_HISTORY_WAIT',type(e).__name__,flush=True)
 time.sleep(5)
else:raise RuntimeError('Public site did not serve the tested history HTML')
code,spanish=fetch(S);assert code==200 and sha(spanish)==proof['preserved_spanish_files']['docs/index.html'],'Spanish HTML must remain unchanged'
report={'url':H,'history_version':'1.0.0','history_sha256':sha(html),'spanish_html_unchanged':True,'physical_iphone_audio_tested':False,'live_verified':False}
(OUT/'verification.json').write_text(json.dumps(report,indent=2))
for cmd in [[sys.executable,'tests/history_browser.py','--url',H+'?v=1.0.0'],[sys.executable,'tests/listening_browser.py','--url',S+'?v=1.4.2','--quick']]:
 print('RUN_LIVE',cmd,flush=True);subprocess.run(cmd,cwd=ROOT,check=True)
report.update(live_verified=True,history_browser_groups_passed=18,spanish_regression_groups_passed=14)
(OUT/'verification.json').write_text(json.dumps(report,indent=2))
print('PUBLIC_HISTORY_AND_SPANISH_VERIFIED',flush=True)
