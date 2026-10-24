const CACHE_NAME = 'boloka-static-v1'
const APP_SHELL = ['/','/index.html']

self.addEventListener('install', (event) => {
  event.waitUntil(caches.open(CACHE_NAME).then((cache) => cache.addAll(APP_SHELL)))
  self.skipWaiting()
})

self.addEventListener('activate', (event) => {
  const cleanup = caches.keys().then((keys) => {
    const oldCaches = keys.filter((key) => key.startsWith('boloka-static-') && key !== CACHE_NAME)
    return Promise.all(oldCaches.map((key) => caches.delete(key)))
  })
  event.waitUntil(Promise.all([cleanup, self.clients.claim()]))
})

self.addEventListener('fetch', (event) => {
  const request = event.request
  const url = new URL(request.url)
  if (request.method !== 'GET' || url.origin !== self.location.origin) return

  // Private account/API responses are intentionally never cached.
  if (url.pathname.startsWith('/api/')) return

  if (request.mode === 'navigate') {
    event.respondWith(fetch(request).then((response) => {
      if (response.ok) caches.open(CACHE_NAME).then((cache) => cache.put('/index.html', response.clone()))
      return response
    }).catch(async () => (await caches.match('/index.html')) || (await caches.match('/'))))
    return
  }

  if (['script','style','font','image'].includes(request.destination)) {
    event.respondWith(caches.open(CACHE_NAME).then(async (cache) => {
      const cached = await cache.match(request)
      const update = fetch(request).then((response) => {
        if (response.ok) {
          cache.put(request, response.clone())
          cache.keys().then((keys) => keys.slice(60).forEach((key) => cache.delete(key)))
        }
        return response
      }).catch(() => null)
      return cached || update
    }))
  }
})
