"""Build a separate app. The Spanish HTML, core, data and storage remain unchanged."""
from pathlib import Path
import hashlib,json,math,struct,zlib
ROOT=Path(__file__).resolve().parents[1];SRC=ROOT/'history-src'
before={f:hashlib.sha256((ROOT/f).read_bytes()).hexdigest() for f in ['index.html','docs/index.html','src/core.js','src/data.json','src/unit2.json']}
data=json.loads((SRC/'data.json').read_text(encoding='utf-8'));assert len(data['cards'])==15 and len({c['id'] for c in data['cards']})==15
h=(SRC/'shell.html').read_text(encoding='utf-8')
for key,f in [('/*__STYLE__*/','style.css'),('/*__CORE__*/','core.js'),('/*__APP__*/','app.js')]:h=h.replace(key,(SRC/f).read_text(encoding='utf-8'))
h=h.replace('__DATA__',json.dumps(data,ensure_ascii=False,separators=(',',':')).replace('</','<\\/'))
# Ensure an old broad parent worker updates too, so each app retains only its own offline entry.
h=h.replace("rememberBadges();home();","if('serviceWorker'in navigator&&/^https?:$/.test(location.protocol)){navigator.serviceWorker.getRegistration('../').then(r=>{if(r&&new URL(r.scope).pathname===new URL('../',location.href).pathname)r.update().catch(()=>{});}).catch(()=>{});}\nrememberBadges();home();")
manifest={'name':'Alaina’s History Studio','short_name':'History Studio','id':'./','start_url':'./','scope':'./','display':'standalone','background_color':'#f5f1e9','theme_color':'#173b3d','icons':[{'src':f'./icon-{n}.png','sizes':f'{n}x{n}','type':'image/png','purpose':'any'} for n in [192,512]]}
def png(n):
 rows=[]
 for y in range(n):
  row=bytearray()
  for x in range(n):
   xx=x/n;yy=y/n;col=(245,241,233)
   if (xx-.5)**2+(yy-.5)**2<.44**2:col=(23,59,61)
   if (.28<xx<.39 and .27<yy<.73) or (.61<xx<.72 and .27<yy<.73) or (.35<xx<.66 and .45<yy<.55):col=(228,187,112)
   row.extend(col)
  rows.append(b'\0'+row)
 def chunk(t,d):return struct.pack('>I',len(d))+t+d+struct.pack('>I',zlib.crc32(t+d)&0xffffffff)
 return b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',n,n,8,2,0,0,0))+chunk(b'IDAT',zlib.compress(b''.join(rows)))+chunk(b'IEND',b'')
for folder in ['history','docs/history']:
 p=ROOT/folder;p.mkdir(exist_ok=True)
 (p/'index.html').write_text(h,encoding='utf-8');(p/'sw.js').write_text((SRC/'sw.js').read_text(),encoding='utf-8');(p/'manifest.webmanifest').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
 for n in [192,512]:(p/f'icon-{n}.png').write_bytes(png(n))
# Only a routing fix in the parent worker: do not cache sibling app navigation as the Spanish homepage.
for f in ['sw.js','docs/sw.js']:
 p=ROOT/f;s=p.read_text(encoding='utf-8')
 if 'v1.4.2-route-isolation' not in s:
  assert "const CACHE = PREFIX + 'v1.4.2';" in s
  s=s.replace("const CACHE = PREFIX + 'v1.4.2';","const CACHE = PREFIX + 'v1.4.2-route-isolation';")
  s=s.replace("if (event.request.mode === 'navigate') {","if (event.request.mode === 'navigate' && allowed.includes(url.pathname)) {")
  p.write_text(s,encoding='utf-8')
for f,digest in before.items():assert hashlib.sha256((ROOT/f).read_bytes()).hexdigest()==digest,f
assert 'alaina-spanish-practice-v1' not in h
print('HISTORY_BUILT',len(h.encode()),'bytes; 15 unique terms; four modes. Spanish app/data bytes unchanged.')
print('HISTORY_SHA256',hashlib.sha256(h.encode()).hexdigest())
(ROOT/'HISTORY_BUILD.json').write_text(json.dumps({'history_sha256':hashlib.sha256(h.encode()).hexdigest(),'preserved_spanish_files':before,'terms':15,'history_storage':'alaina-history-studio-v1','parent_change':'navigation allowlist and cache-version refresh only'},indent=2))
