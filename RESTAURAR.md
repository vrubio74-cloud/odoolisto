# Web en pausa (desde el 25 nov 2026)

Por indicación legal, odoolisto.com y la copia en `*.pages.dev` responden con una página neutra (503, `noindex`,
sin marca ni datos). El sitio completo, el blog incluido, sigue en el repositorio, sin borrar nada, y el dominio no
se ha tocado.

## Cómo reactivarla

1. En `functions/_middleware.js`, cambiar `const PAUSA = true;` por `const PAUSA = false;` (o borrar la carpeta `functions`).
2. Commit y `git push origin main`. Cloudflare Pages (proyecto `odoolisto-web`) publica en 1-3 minutos.
3. Comprobar: `curl -sI https://odoolisto.com/` debe dar 200.
4. En Search Console, volver a enviar `sitemap.xml` y pedir la indexación de la portada.
5. Reactivar el agente del blog si se había parado.

El estado del sitio justo antes de la pausa está en la etiqueta `antes-de-pausa-2026-11-25`.
