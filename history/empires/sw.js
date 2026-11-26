/* This worker owns only the Empires unit at its registered Pages path. */
const base = new URL(self.registration.scope);
const prefix = 'history-studio-empires:' + base.pathname + ':';
const cacheName = prefix + 'c32ec3faff0f';
const files = ["app.js", "caravel.webp", "core.js", "index.html", "manifest.webmanifest", "matching.js", "practice.js", "sprite.svg", "style.css", "terms.js", "../icon-192.png", "../icon-512.png"].map(file => new URL(file, base).href);
const index = new URL('index.html', base).href;
self.addEventListener('install', event => {
  event.waitUntil((async () => {
    const cache = await caches.open(cacheName);
    await cache.addAll(files.map(url => new Request(url, {cache:'reload'})));
    await self.skipWaiting();
  })());
});
self.addEventListener('activate', event => {
  event.waitUntil((async () => {
    const names = await caches.keys();
    await Promise.all(names.filter(name => name.startsWith(prefix) && name !== cacheName).map(name => caches.delete(name)));
    await self.clients.claim();
  })());
});
self.addEventListener('fetch', event => {
  const url = new URL(event.request.url);
  url.search = '';
  if (event.request.method !== 'GET') return;
  const key = url.href === base.href ? index : url.href;
  if (!files.includes(key)) return;
  event.respondWith((async () => {
    const hit = await (await caches.open(cacheName)).match(key);
    return hit || fetch(event.request);
  })());
});
