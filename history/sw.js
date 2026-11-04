/* Independent, version-scoped history cache. Never reads or removes Spanish data. */
const BASE=new URL(self.registration.scope),VERSION='v1.1.2';
const PREFIX='alaina-history-'+BASE.pathname+':',CACHE=PREFIX+VERSION;
const FILES=['./','./index.html','./manifest.webmanifest','./icon-192.png','./icon-512.png'];
const ALLOWED=FILES.map(p=>new URL(p,BASE).pathname),INDEX=new URL('./index.html',BASE).href;
self.addEventListener('install',event=>event.waitUntil((async()=>{
 const cache=await caches.open(CACHE);
 // A new version must not seed itself with a previous release from the HTTP cache.
 await cache.addAll(FILES.map(path=>new Request(new URL(path,BASE).href,{cache:'reload'})));
 await self.skipWaiting();
})()));
self.addEventListener('activate',event=>event.waitUntil((async()=>{
 const keys=await caches.keys();
 await Promise.all(keys.filter(k=>k.startsWith(PREFIX)&&k!==CACHE).map(k=>caches.delete(k)));
 await self.clients.claim();
})()));
self.addEventListener('message',event=>{
 if(event.data?.type==='HISTORY_CACHE_VERSION')event.ports[0]?.postMessage({version:VERSION,cache:CACHE});
});
self.addEventListener('fetch',event=>{
 const url=new URL(event.request.url);
 if(event.request.method!=='GET'||url.origin!==BASE.origin||!ALLOWED.includes(url.pathname))return;
 if(event.request.mode==='navigate')event.respondWith((async()=>{
  const cache=await caches.open(CACHE);
  try{
   const response=await fetch(new Request(event.request,{cache:'no-cache'}));
   if(response.ok){
    // Failure to save offline must not turn a successful network response into an error.
    try{await cache.put(INDEX,response.clone());}catch(_){}
   }
   return response;
  }catch(_){
   // Search this release only; a late old-worker write must never revive an old app.
   return await cache.match(INDEX)||new Response('Reconnect to load History Studio. Your saved practice has not been cleared.',{status:503,headers:{'Content-Type':'text/plain; charset=utf-8'}});
  }
 })());
 else event.respondWith((async()=>{
  const cache=await caches.open(CACHE);
  return await cache.match(event.request,{ignoreSearch:true})||fetch(event.request);
 })());
});
