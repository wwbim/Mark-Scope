/**
 * Mark Scope - Service Worker
 * 100% Offline App Shell Caching for PWA Installation
 */

const CACHE_NAME = 'mark-scope-v1.0.0';
const APP_SHELL = [
  './',
  './index.html',
  './Deliverables/MarkScope.html',
  './manifest.json',
  './assets/icons/icon-192.png',
  './assets/icons/icon-512.png',
  './assets/icons/icon.svg',
  './favicon.ico'
];

self.addEventListener('install', (event) => {
  self.skipWaiting();
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll(APP_SHELL).catch((err) => {
        console.warn('Mark Scope SW: Non-critical pre-cache error:', err);
      });
    })
  );
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((name) => {
          if (name.startsWith('mark-scope-') && name !== CACHE_NAME) {
            return caches.delete(name);
          }
        })
      );
    }).then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', (event) => {
  // Only handle GET requests
  if (event.request.method !== 'GET') return;

  const url = new URL(event.request.url);

  // Bypass non-http/https (e.g. chrome-extension, file)
  if (!url.protocol.startsWith('http')) return;

  event.respondWith(
    caches.match(event.request).then((cachedResponse) => {
      if (cachedResponse) {
        return cachedResponse;
      }

      return fetch(event.request).then((networkResponse) => {
        // Cache valid responses for offline use
        if (networkResponse && networkResponse.status === 200) {
          const responseToCache = networkResponse.clone();
          caches.open(CACHE_NAME).then((cache) => {
            cache.put(event.request, responseToCache);
          });
        }
        return networkResponse;
      }).catch(() => {
        // If navigation request fails offline, fallback to main editor
        if (event.request.mode === 'navigate') {
          return caches.match('./Deliverables/MarkScope.html') || caches.match('./index.html');
        }
      });
    })
  );
});
