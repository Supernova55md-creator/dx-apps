/* DXナビ（dx-apps）共通 service worker
   アプリを更新・追加したら VERSION を必ず変える（例 a→b、日付更新）。新しいアプリは APPS に slug を追加する。
   キャッシュ名は "dxnavi-" で始める。同じドメインの病棟アプリ（ward-apps）のキャッシュには触らない。 */
const VERSION = "dxnavi-2026-11-16g";
const APPS = ["ks", "nq", "rh", "tn", "qs", "ms"];
const ROOT = ["./", "index.html", "manifest.webmanifest", "icon-192.png", "icon-512.png", "apple-touch-icon.png"];
const PER_APP = ["", "index.html", "app.enc", "icon-192.png", "icon-512.png", "apple-touch-icon.png"];
const ASSETS = ROOT.concat(...APPS.map((a) => PER_APP.map((f) => a + "/" + f)));

self.addEventListener("install", (e) => {
  e.waitUntil(caches.open(VERSION)
    .then((c) => Promise.allSettled(ASSETS.map((u) => c.add(new Request(u, { cache: "reload" })))))
    .then(() => self.skipWaiting()));
});

self.addEventListener("activate", (e) => {
  e.waitUntil(caches.keys()
    .then((keys) => Promise.all(keys.filter((k) => k.startsWith("dxnavi-") && k !== VERSION).map((k) => caches.delete(k))))
    .then(() => self.clients.claim()));
});

self.addEventListener("fetch", (e) => {
  const req = e.request;
  if (req.method !== "GET") return;
  const url = new URL(req.url);
  if (url.origin !== self.location.origin) return;
  if (url.pathname.endsWith("/sw.js")) return;
  if (url.pathname.endsWith(".enc")) { // 暗号化した中身：常にサーバーを優先し、オフライン時だけキャッシュ
    e.respondWith(fetch(req.url, { cache: "no-cache" })
      .then((res) => { if (res.ok) { const copy = res.clone(); caches.open(VERSION).then((c) => c.put(req, copy)); } return res; })
      .catch(async () => (await caches.match(req, { ignoreSearch: true })) || Response.error()));
    return;
  }
  if (req.mode === "navigate") {
    e.respondWith(
      fetch(req.url, { cache: "no-cache", credentials: "same-origin" })
        .then((res) => { if (res.ok) { const copy = res.clone(); caches.open(VERSION).then((c) => c.put(req, copy)); } return res; })
        .catch(async () => (await caches.match(req, { ignoreSearch: true })) || (await caches.match(new URL("index.html", url).href)) || Response.error())
    );
    return;
  }
  e.respondWith(caches.match(req, { ignoreSearch: true }).then((hit) => hit || fetch(req).then((res) => {
    if (res.ok) { const copy = res.clone(); caches.open(VERSION).then((c) => c.put(req, copy)); }
    return res;
  })));
});
