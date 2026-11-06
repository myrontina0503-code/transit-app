// 離線快取:自己的檔案用「網路優先」,YouBike 即時資料不快取
const CACHE = 'transit-20261106a';
const SHELL = ['./', './index.html', './manifest.webmanifest', './icon-180.png', './icon-512.png', './data/transit.json'];
self.addEventListener('install', e => { e.waitUntil(caches.open(CACHE).then(c => c.addAll(SHELL))); self.skipWaiting(); });
self.addEventListener('activate', e => {
  e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k !== CACHE).map(k => caches.delete(k)))));
  self.clients.claim();
});
self.addEventListener('fetch', e => {
  const req = e.request;
  if (req.method !== 'GET' || new URL(req.url).origin !== location.origin) return;
  e.respondWith(fetch(req).then(r => { const c = r.clone(); caches.open(CACHE).then(x => x.put(req, c)); return r; })
    .catch(() => caches.match(req).then(r => r || caches.match('./'))));
});
