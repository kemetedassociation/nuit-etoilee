// Garde le site, les images et les audios déjà écoutés disponibles hors ligne.
const CACHE = "nuit-etoilee-v1";
const BASE = ["./", "index.html", "manifest.json", "img/01.jpg", "img/02.jpg", "img/03.jpg", "img/04.jpg", "img/05.jpg", "img/06.jpg", "img/08.jpg", "img/09.jpg", "img/icone.png"];
self.addEventListener("install", e => e.waitUntil(caches.open(CACHE).then(c => c.addAll(BASE)).then(() => self.skipWaiting())));
self.addEventListener("activate", e => e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k !== CACHE).map(k => caches.delete(k)))).then(() => self.clients.claim())));
self.addEventListener("fetch", e => {
  if (e.request.method !== "GET" || e.request.headers.has("range")) return;
  e.respondWith(caches.match(e.request).then(r => r || fetch(e.request).then(res => {
    if (res.ok && new URL(e.request.url).origin === location.origin) { const copie = res.clone(); caches.open(CACHE).then(c => c.put(e.request, copie)); }
    return res;
  })));
});
