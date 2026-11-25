"""Refresh the Empires offline cache version and the GitHub Pages docs mirror."""
from hashlib import sha256
from pathlib import Path
from shutil import copyfile

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "history" / "empires"
MIRROR = ROOT / "docs" / "history" / "empires"
copyfile(ROOT / "history-src" / "core.js", SOURCE / "core.js")
assets = sorted(path for path in SOURCE.iterdir() if path.is_file() and path.name != "sw.js")
digest = sha256()
for path in assets:
    digest.update(path.name.encode() + b"\x00" + path.read_bytes())
version = digest.hexdigest()[:12]
urls = [path.name for path in assets] + ["../icon-192.png", "../icon-512.png"]
worker = """/* This worker owns only the Empires unit at its registered Pages path. */
const base = new URL(self.registration.scope);
const prefix = 'history-studio-empires:' + base.pathname + ':';
const cacheName = prefix + '__VERSION__';
const files = __FILES__.map(file => new URL(file, base).href);
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
"""
import json
(SOURCE / "sw.js").write_text(worker.replace("__VERSION__", version).replace("__FILES__", json.dumps(urls)))
MIRROR.mkdir(parents=True, exist_ok=True)
for path in [*assets, SOURCE / "sw.js"]:
    copyfile(path, MIRROR / path.name)
print(f"Empires release {version}, {len(assets) + 1} files mirrored")
