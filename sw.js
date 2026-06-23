// SCORDAGOL service worker — makes the game installable (Add to Home Screen) and playable
// offline, WITHOUT introducing stale-content bugs: it is NETWORK-FIRST, so online players
// always get the freshest files (the engine's ?v= cache-busting keeps working). The cache is
// only a fallback for when the device is offline.
const CACHE = "scordagol-v2";
const CORE = [
  "./", "index.html", "manifest.webmanifest",
  "assets/ui/icon-192.png", "assets/ui/icon-512.png", "assets/ui/icon-180.png",
];

self.addEventListener("install", (e) => {
  self.skipWaiting();
  e.waitUntil(caches.open(CACHE).then((c) => c.addAll(CORE)).catch(() => {}));
});

self.addEventListener("activate", (e) => {
  e.waitUntil(
    caches.keys()
      .then((keys) => Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener("fetch", (e) => {
  const req = e.request;
  if (req.method !== "GET") return;
  let url;
  try { url = new URL(req.url); } catch (_) { return; }
  if (url.origin !== location.origin) return;                 // only manage same-origin GETs
  e.respondWith(
    fetch(req)
      .then((res) => {
        if (res && res.status === 200 && res.type === "basic") {  // cache fresh copies for offline
          const copy = res.clone();
          caches.open(CACHE).then((c) => c.put(req, copy)).catch(() => {});
        }
        return res;
      })
      .catch(() =>
        caches.match(req).then((hit) =>
          hit || (req.mode === "navigation" ? caches.match("index.html") : Response.error())
        )
      )
  );
});
