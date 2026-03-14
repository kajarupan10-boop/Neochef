// NeoChef PWA Service Worker v3.0 - FORCE REFRESH
const CACHE_NAME = 'neochef-v3-' + Date.now();
const PING_INTERVAL = 4 * 60 * 1000;

// Ne plus mettre en cache les fichiers JS/HTML
const STATIC_ASSETS = [
  '/manifest.json',
  '/apple-touch-icon.png',
  '/apple-touch-icon-180x180.png',
  '/icon-192.png',
  '/icon-512.png',
  '/favicon.png'
];

self.addEventListener('install', (event) => {
  console.log('[SW] Installing v3 - Force refresh...');
  event.waitUntil(
    caches.keys().then(cacheNames => {
      // Delete ALL old caches
      return Promise.all(
        cacheNames.map(name => {
          console.log('[SW] Deleting old cache:', name);
          return caches.delete(name);
        })
      );
    })
    .then(() => caches.open(CACHE_NAME))
    .then(cache => cache.addAll(STATIC_ASSETS))
    .then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', (event) => {
  console.log('[SW] Activating v3...');
  event.waitUntil(
    caches.keys()
      .then(cacheNames => {
        return Promise.all(
          cacheNames
            .filter(name => name !== CACHE_NAME)
            .map(name => caches.delete(name))
        );
      })
      .then(() => clients.claim())
      .then(() => {
        setInterval(() => {
          fetch('/api/health').catch(() => {});
        }, PING_INTERVAL);
      })
  );
});

self.addEventListener('fetch', (event) => {
  const url = new URL(event.request.url);
  
  // API calls - network only
  if (url.pathname.startsWith('/api/')) {
    event.respondWith(fetch(event.request));
    return;
  }
  
  // JS and HTML files - ALWAYS network first, no cache
  if (url.pathname.endsWith('.js') || url.pathname.endsWith('.html') || url.pathname.includes('/_expo/')) {
    event.respondWith(
      fetch(event.request, { cache: 'no-store' })
        .catch(() => caches.match(event.request))
    );
    return;
  }
  
  // Other static assets - network first with cache fallback
  event.respondWith(
    fetch(event.request)
      .then(response => {
        if (!response || response.status !== 200) {
          return response;
        }
        const responseToCache = response.clone();
        caches.open(CACHE_NAME)
          .then(cache => cache.put(event.request, responseToCache));
        return response;
      })
      .catch(() => caches.match(event.request))
  );
});

// Listen for skip waiting message
self.addEventListener('message', (event) => {
  if (event.data === 'skipWaiting') {
    self.skipWaiting();
  }
});
