// Hors ligne : la page passe toujours d'abord par le réseau (chaque visiteur reçoit la
// dernière version), et la copie gardée ne sert que sans connexion. Les images et les
// audios, eux, sont servis depuis la copie pour aller vite.
const CACHE = "nuit-etoilee-v2";
const BASE = ["./", "index.html", "manifest.json", "img/01.jpg", "img/02.jpg", "img/03.jpg", "img/04.jpg", "img/05.jpg", "img/06.jpg", "img/08.jpg", "img/09.jpg", "img/affiche.jpg", "img/icone.png"];

self.addEventListener("install", e => e.waitUntil(caches.open(CACHE).then(c => c.addAll(BASE)).then(() => self.skipWaiting())));
self.addEventListener("activate", e => e.waitUntil(
  caches.keys().then(ks => Promise.all(ks.filter(k => k !== CACHE).map(k => caches.delete(k)))).then(() => self.clients.claim())));

const garder = (req, res) => { if (res.ok && new URL(req.url).origin === location.origin) { const copie = res.clone(); caches.open(CACHE).then(c => c.put(req, copie)); } return res; };

self.addEventListener("fetch", e => {
  const req = e.request;
  if (req.method !== "GET" || req.headers.has("range")) return;
  const url = new URL(req.url);
  const page = req.mode === "navigate" || /\.(html|js|css|json)$/.test(url.pathname) || url.pathname.endsWith("/");
  if (page) {
    e.respondWith(fetch(req).then(res => garder(req, res)).catch(() => caches.match(req).then(r => r || caches.match("index.html"))));
  } else {
    e.respondWith(caches.match(req).then(r => r || fetch(req).then(res => garder(req, res))));
  }
});
