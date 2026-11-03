/* Independent history cache. Never removes or reads Spanish cache entries. */
const BASE=new URL(self.registration.scope),PREFIX='alaina-history-'+BASE.pathname+':',CACHE=PREFIX+'v1.0.0';
const FILES=['./','./index.html','./manifest.webmanifest','./icon-192.png','./icon-512.png'];
const ALLOWED=FILES.map(p=>new URL(p,BASE).pathname),INDEX=new URL('./index.html',BASE).href;
self.addEventListener('install',e=>e.waitUntil(caches.open(CACHE).then(c=>c.addAll(FILES)).then(()=>self.skipWaiting())));
self.addEventListener('activate',e=>e.waitUntil(caches.keys().then(keys=>Promise.all(keys.filter(k=>k.startsWith(PREFIX)&&k!==CACHE).map(k=>caches.delete(k)))).then(()=>self.clients.claim())));
self.addEventListener('fetch',e=>{const u=new URL(e.request.url);if(e.request.method!=='GET'||u.origin!==BASE.origin||!ALLOWED.includes(u.pathname))return;
 if(e.request.mode==='navigate')e.respondWith(fetch(e.request).then(async r=>{if(r.ok){const c=await caches.open(CACHE);await c.put(INDEX,r.clone());}return r;}).catch(()=>caches.match(INDEX)));
 else e.respondWith(caches.match(e.request,{ignoreSearch:true}).then(c=>c||fetch(e.request)));
});
