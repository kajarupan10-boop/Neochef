// NeoChef PWA Service Worker v5.0 - Force update
const CACHE_NAME = 'neochef-v5-' + Date.now();
const PING_INTERVAL = 4 * 60 * 1000;

const STATIC_ASSETS = [
  '/',
  '/manifest.json',
  '/apple-touch-icon.png',
  '/icon-192.png',
  '/icon-512.png',
  '/favicon.png'
];

self.addEventListener('install', (event) => {
  console.log('[SW] Installing v5...');
  // Force immediate activation
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  console.log('[SW] Activating v5...');
  event.waitUntil(
    // Delete ALL old caches
    caches.keys()
      .then(cacheNames => {
        return Promise.all(
          cacheNames.map(name => {
            console.log('[SW] Deleting old cache:', name);
            return caches.delete(name);
          })
        );
      })
      .then(() => {
        console.log('[SW] All old caches deleted');
        return clients.claim();
      })
  );
});

self.addEventListener('fetch', (event) => {
  const url = new URL(event.request.url);
  
  // API calls and JS files - ALWAYS network only (no cache)
  if (url.pathname.startsWith('/api/') || url.pathname.includes('.js')) {
    event.respondWith(fetch(event.request));
    return;
  }
  
  // Everything else - network first, fallback to cache
  event.respondWith(
    fetch(event.request)
      .then(response => {
        // Clone and cache successful responses
        if (response && response.status === 200) {
          const responseToCache = response.clone();
          caches.open(CACHE_NAME).then(cache => {
            cache.put(event.request, responseToCache);
          });
        }
        return response;
      })
      .catch(() => {
        return caches.match(event.request);
      })
  );
});

// Send message to update all clients
self.addEventListener('message', (event) => {
  if (event.data === 'skipWaiting') {
    self.skipWaiting();
  }
});
