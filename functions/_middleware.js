// PAUSA (25 nov 2026, por indicación legal): mientras PAUSA sea true, todo el sitio (odoolisto.com y *.pages.dev)
// responde con una página neutra 503 sin marca ni datos. Para reactivar: PAUSA = false y push a main.
// Instrucciones completas en RESTAURAR.md.
const PAUSA = true;

const HTML = `<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow"><title>Temporalmente no disponible</title><style>body{margin:0;min-height:100vh;display:grid;place-items:center;background:#f6f7f8;color:#1f2933;font:16px/1.5 -apple-system,Helvetica,Arial,sans-serif;text-align:center;padding:24px}h1{font-size:22px;font-weight:600;margin:0 0 8px}p{margin:0;color:#5f6b7a}</style></head><body><main><h1>Temporalmente no disponible</h1><p>Esta web no está disponible temporalmente. Disculpa las molestias.</p></main></body></html>`;

export async function onRequest({ next }) {
  if (!PAUSA) return next();
  return new Response(HTML, { status: 503, headers: { "content-type": "text/html; charset=utf-8", "cache-control": "no-store", "retry-after": "86400", "x-robots-tag": "noindex, nofollow" } });
}
