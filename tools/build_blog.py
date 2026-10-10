#!/usr/bin/env python3
"""Genera el blog de odoolisto.com como páginas reales (una URL por artículo).

Fuente:   blog/posts/<slug>.html  — fragmento del artículo con una primera línea
          <!-- META {"n": 23, "slug": "...", "title": "...", "description": "...",
                     "date": "2026-09-30", "category": "Comparativa", "readtime": "9 min"} -->
Salida:   blog/<slug>/index.html  · blog/index.html · assets/site.css · sitemap.xml

Uso:  python3 tools/build_blog.py      (desde la raíz del repo)
"""
import json, re, html, pathlib, datetime

ROOT = pathlib.Path(__file__).resolve().parent.parent
SITE = "https://odoolisto.com"
MESES = ["ene","feb","mar","abr","may","jun","jul","ago","sep","oct","nov","dic"]
POSTS_DIR = ROOT / "blog" / "posts"

HASH_PAGES = {
    "home": "/", "checkout": "/#contratar", "modules": "/#modulos", "about": "/#nosotros",
    "contact": "/#contacto", "terms": "/#terminos", "privacy": "/#privacidad",
    "legal": "/#legal", "cookies": "/#cookies", "blog": "/blog/",
}

TRACKING = """<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  if (!/^(localhost|127\\.0\\.0\\.1)$/.test(location.hostname)) {
    gtag('config', 'AW-18242312681');
    gtag('config', 'G-TTBKX48K3B');
  }
</script>
<script async src="https://www.googletagmanager.com/gtag/js?id=AW-18242312681"></script>
<script type="text/javascript">
    if (!/^(localhost|127\\.0\\.0\\.1)$/.test(location.hostname)) (function(c,l,a,r,i,t,y){
        c[a]=c[a]||function(){(c[a].q=c[a].q||[]).push(arguments)};
        t=l.createElement(r);t.async=1;t.src="https://www.clarity.ms/tag/"+i;
        y=l.getElementsByTagName(r)[0];y.parentNode.insertBefore(t,y);
    })(window, document, "clarity", "script", "xenf784cuk");
</script>"""

HEADER = """<a class="ai-bar" href="/#ia">🤖 <strong>Nuevo: OdooListo IA.</strong> Pregúntale a tu empresa y te responde en segundos → Ver vídeo</a>
<header class="bl-head">
  <a class="bl-logo logo" href="/"><div class="logo-i"><svg viewBox="0 0 22 22" fill="none"><rect x="2" y="2" width="8" height="8" rx="2.5" fill="white" opacity=".95"/><rect x="12" y="2" width="8" height="8" rx="2.5" fill="white" opacity=".7"/><rect x="2" y="12" width="8" height="8" rx="2.5" fill="white" opacity=".7"/><rect x="12" y="12" width="8" height="8" rx="2.5" fill="#00A09D" opacity=".9"/></svg></div> OdooListo</a>
  <nav class="bl-nav">
    <a href="/blog/">Blog</a>
    <a href="/#ia">OdooListo IA</a>
    <a class="bl-cta" href="/#contratar">Contratar</a>
  </nav>
</header>"""

EXTRA_CSS = """
.bl-head{position:sticky;top:0;z-index:200;display:flex;align-items:center;justify-content:space-between;gap:12px;padding:10px 5%;background:rgba(255,255,255,.96);border-bottom:1px solid var(--g1);backdrop-filter:blur(10px)}
.bl-logo{display:flex;align-items:center;gap:8px;font-weight:800;color:var(--navy);text-decoration:none;font-size:1.05rem}
.bl-nav{display:flex;align-items:center;gap:16px}
.bl-nav a{color:var(--navy);text-decoration:none;font-weight:700;font-size:.88rem}
.bl-nav a.bl-cta{background:var(--teal);color:#fff;padding:8px 16px;border-radius:20px}
.bl-post > a:first-child{display:inline-block;text-decoration:none}
.bl-list{max-width:900px;margin:0 auto;padding:40px 5% 80px}
.bl-item{display:block;padding:20px 0;border-bottom:1px solid var(--g1);text-decoration:none}
.bl-item h2{font-family:var(--serif);color:var(--navy);font-size:1.3rem;margin:4px 0 6px}
.bl-item p{color:var(--g4);font-size:.92rem;margin:0}
.bl-meta{color:var(--g3);font-size:.8rem}
.bl-foot{text-align:center;padding:30px 5%;color:var(--g3);font-size:.82rem;border-top:1px solid var(--g1)}
.bl-foot a{color:var(--teal)}
@media(max-width:600px){.bl-nav a:not(.bl-cta){display:none}}
"""

SCRIPTS = """<script>
var BLOG_SLUGS = %s;
function go(id){
  var m = {%s};
  if (BLOG_SLUGS[id]) { location.href = '/blog/' + BLOG_SLUGS[id] + '/'; return; }
  location.href = m[id] || '/';
}
function goCheckout(){ location.href = '/#contratar'; }
function openVideo(id){ window.open('https://www.youtube.com/watch?v=' + id, '_blank', 'noopener'); }
function setLang(){}
document.addEventListener('click', function(ev){
  var a = ev.target.closest ? ev.target.closest('a[href]') : null;
  if (!a) return;
  var href = a.getAttribute('href') || '';
  try {
    if (href.indexOf('wa.me/') > -1) gtag('event', 'whatsapp_click', {'ubicacion': 'blog', 'transport_type':'beacon'});
    else if (href.indexOf('calendly.com/') > -1) gtag('event', 'calendly_click', {'tipo': 'demo', 'ubicacion': 'blog', 'transport_type':'beacon'});
    else if (href.indexOf('/#contratar') > -1) gtag('event', 'blog_cta_click', {'transport_type':'beacon'});
  } catch(e){}
}, true);
</script>"""


def esc(t):
    return html.escape(t, quote=True)


def read_posts():
    posts = []
    for f in sorted(POSTS_DIR.glob("*.html")):
        raw = f.read_text(encoding="utf-8")
        m = re.match(r"<!-- META (\{.*?\}) -->\n", raw, re.S)
        if not m:
            raise SystemExit(f"{f.name}: falta la línea META")
        meta = json.loads(m.group(1))
        meta["body"] = raw[m.end():]
        if "date_label" not in meta:
            y, mo, d = meta["date"].split("-")
            meta["date_label"] = f"{int(d)} {MESES[int(mo)-1]} {y}"
        posts.append(meta)
    posts.sort(key=lambda p: (p["date"], p["n"]), reverse=True)
    return posts


def link_internal(body, slugs):
    """Convierte go('x') en enlaces reales, para que Google los siga."""
    def url(target):
        return f"/blog/{slugs[target]}/" if target in slugs else HASH_PAGES.get(target, "/")
    body = re.sub(r"<button([^>]*?)\s*onclick=\"go\('([\w-]+)'\)\"([^>]*)>(.*?)</button>",
                  lambda m: f'<a{m.group(1)} href="{url(m.group(2))}"{m.group(3)}>{m.group(4)}</a>', body, flags=re.S)
    body = re.sub(r"<a([^>]*?)\s*onclick=\"go\('([\w-]+)'\)\"",
                  lambda m: f'<a{m.group(1)} href="{url(m.group(2))}"', body)
    return body


def page(title, description, canonical, body, scripts, jsonld=None, og_type="website"):
    ld = f'<script type="application/ld+json">{json.dumps(jsonld, ensure_ascii=False)}</script>\n' if jsonld else ""
    return f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<script>if (/\\.pages\\.dev$/.test(location.hostname)) location.replace('https://odoolisto.com' + location.pathname + location.search + location.hash);</script>
{TRACKING}
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{esc(title)}</title>
<meta name="description" content="{esc(description)}">
<link rel="canonical" href="{canonical}">
<meta property="og:type" content="{og_type}">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(description)}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{SITE}/logo.png">
<link rel="icon" href="/logo.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800&family=Playfair+Display:ital,wght@0,700;1,700&display=swap">
<link rel="stylesheet" href="/assets/site.css">
{ld}</head>
<body>
{HEADER}
{body}
<footer class="bl-foot">OdooListo · Athilan Pignus, S.L. · <a href="/">Inicio</a> · <a href="/blog/">Blog</a> · <a href="/#terminos">Términos</a> · <a href="/#privacidad">Privacidad</a></footer>
{WA_FLOAT}
{scripts}
</body>
</html>
"""


def main():
    global WA_FLOAT
    index = (ROOT / "index.html").read_text(encoding="utf-8")
    css = re.search(r"<style>(.*?)</style>", index, re.S).group(1)
    (ROOT / "assets").mkdir(exist_ok=True)
    (ROOT / "assets" / "site.css").write_text(css + EXTRA_CSS, encoding="utf-8")
    i = index.index('<div class="wa-float">')
    j = index.index("</div>", index.index("</svg>", index.index('class="wa-btn"', i))) + len("</div>")
    WA_FLOAT = index[i:j]

    posts = read_posts()
    slugs = {f"post{p['n']}": p["slug"] for p in posts}
    scripts = SCRIPTS % (json.dumps(slugs), ",".join(f"'{k}':'{v}'" for k, v in HASH_PAGES.items()))

    for p in posts:
        canonical = f"{SITE}/blog/{p['slug']}/"
        body = link_internal(p["body"], slugs)
        ld = {"@context": "https://schema.org", "@type": "BlogPosting", "headline": p["title"],
              "description": p["description"], "datePublished": p["date"], "dateModified": p["date"],
              "mainEntityOfPage": canonical, "inLanguage": "es",
              "author": {"@type": "Organization", "name": "OdooListo", "url": SITE},
              "publisher": {"@type": "Organization", "name": "OdooListo",
                            "logo": {"@type": "ImageObject", "url": f"{SITE}/logo.png"}}}
        out = ROOT / "blog" / p["slug"] / "index.html"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(page(f"{p['title']} | OdooListo", p["description"], canonical, body, scripts, ld, "article"),
                       encoding="utf-8")

    items = "\n".join(
        f'<a class="bl-item" href="/blog/{p["slug"]}/"><span class="bl-meta">{esc(p["date_label"])} · {esc(p["category"])} · {esc(p["readtime"])}</span>'
        f'<h2>{esc(p["title"])}</h2><p>{esc(p["description"])}</p></a>' for p in posts)
    listing = f"""<main class="bl-list">
<h1 style="font-family:var(--serif);color:var(--navy);font-size:clamp(1.8rem,4vw,2.6rem);margin-bottom:6px">Blog de OdooListo</h1>
<p style="color:var(--g4);margin-bottom:10px">Guías para pymes que quieren poner Odoo en marcha sin proyectos de meses: precios, comparativas, VeriFactu y casos por sector y país.</p>
{items}
</main>"""
    (ROOT / "blog" / "index.html").write_text(
        page("Blog de OdooListo · Odoo para pymes", "Guías prácticas para poner Odoo en marcha en tu pyme: precios, comparativas con Holded, Sage o Zoho, VeriFactu y Odoo por país.",
             f"{SITE}/blog/", listing, scripts), encoding="utf-8")

    today = datetime.date.today().isoformat()
    urls = [(f"{SITE}/", today, "1.0"), (f"{SITE}/blog/", today, "0.8")] + \
           [(f"{SITE}/blog/{p['slug']}/", p["date"], "0.7") for p in posts]
    sm = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + \
         "".join(f"  <url><loc>{u}</loc><lastmod>{d}</lastmod><priority>{pr}</priority></url>\n" for u, d, pr in urls) + "</urlset>\n"
    (ROOT / "sitemap.xml").write_text(sm, encoding="utf-8")

    # Mapa postN → slug para la portada (enlaces antiguos /#postN)
    (ROOT / "assets" / "blog-slugs.json").write_text(json.dumps(slugs, ensure_ascii=False), encoding="utf-8")
    print(f"{len(posts)} artículos · blog/index.html · sitemap.xml · assets/site.css")


if __name__ == "__main__":
    main()
