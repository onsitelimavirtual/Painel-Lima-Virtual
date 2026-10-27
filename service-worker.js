const CACHE="painel-lima-virtual-2-2-final";
const CORE=["./","./index.html","./manifest.webmanifest","./subsystems/inkis-ia/index.html"];
self.addEventListener("install",e=>{self.skipWaiting();e.waitUntil(caches.open(CACHE).then(c=>c.addAll(CORE).catch(()=>{})))});
self.addEventListener("activate",e=>{e.waitUntil(Promise.all([self.clients.claim(),caches.keys().then(keys=>Promise.all(keys.filter(k=>k!==CACHE).map(k=>caches.delete(k))))]))});
self.addEventListener("fetch",e=>{
 const u=new URL(e.request.url);
 if(u.origin!==self.location.origin||e.request.method!=="GET")return;
 if(e.request.mode==="navigate"||u.pathname.endsWith("/index.html")||u.pathname.endsWith("/manifest.webmanifest")){
  e.respondWith(fetch(e.request,{cache:"no-store"}).then(r=>{const c=r.clone();caches.open(CACHE).then(x=>x.put(e.request,c));return r}).catch(()=>caches.match(e.request).then(r=>r||caches.match("./index.html"))));
  return;
 }
 e.respondWith(caches.match(e.request).then(cached=>cached||fetch(e.request).then(r=>{const c=r.clone();caches.open(CACHE).then(x=>x.put(e.request,c));return r})));
});