const SHELL_CACHE = 'sqt-shell-v2';
const DATA_CACHE = 'sqt-data-v2';
const SHELL_ASSETS = ['./', './index.html', './sqt-grove-clock.js', './sqt-core.js', './sqt-grove-clock.css', './manifest.json'];
const DATA_ASSETS = ['./circuit-current.json', './calendar_matrix.json'];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(SHELL_CACHE).then((cache) => cache.addAll(SHELL_ASSETS)).then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(keys.filter((k) => !['sqt-shell-v2', 'sqt-data-v2'].includes(k)).map((k) => caches.delete(k)))
    ).then(() => self.clients.claim())
  );
});

async function staleWhileRevalidate(request) {
  const cache = await caches.open(DATA_CACHE);
  const cached = await cache.match(request);
  const fetchPromise = fetch(request).then((response) => {
    if (response.ok) cache.put(request, response.clone());
    return response;
  });
  return cached || fetchPromise;
}

self.addEventListener('fetch', (event) => {
  const url = new URL(event.request.url);
  if (DATA_ASSETS.some((p) => url.pathname.endsWith(p.replace('./', '')))) {
    event.respondWith(staleWhileRevalidate(event.request));
    return;
  }
  if (SHELL_ASSETS.some((p) => url.pathname.endsWith(p.replace('./', '')) || url.pathname.endsWith('/'))) {
    event.respondWith(caches.match(event.request).then((r) => r || fetch(event.request)));
    return;
  }
});