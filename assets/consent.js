/* Consentimiento de cookies · OdooListo
 * Consent Mode v2: todo denegado por defecto (lo fija el bloque del <head>).
 * Este script pinta el banner, guarda la elección y, si se acepta:
 *   - actualiza el consentimiento de Google (GA4 + Ads)
 *   - carga Microsoft Clarity
 *   - avisa a window.olOnConsent (para píxeles futuros, p. ej. Meta)
 * Elección guardada en localStorage 'ol_consent' = 'all' | 'none'.
 */
(function () {
  var KEY = 'ol_consent';
  var LOCAL = /^(localhost|127\.0\.0\.1)$/.test(location.hostname);

  function get() { try { return localStorage.getItem(KEY); } catch (e) { return null; } }
  function set(v) { try { localStorage.setItem(KEY, v); } catch (e) {} }

  function loadClarity() {
    if (LOCAL || window.__olClarity) return;
    window.__olClarity = true;
    (function (c, l, a, r, i, t, y) {
      c[a] = c[a] || function () { (c[a].q = c[a].q || []).push(arguments); };
      t = l.createElement(r); t.async = 1; t.src = 'https://www.clarity.ms/tag/' + i;
      y = l.getElementsByTagName(r)[0]; y.parentNode.insertBefore(t, y);
    })(window, document, 'clarity', 'script', 'xenf784cuk');
  }

  // Píxel de Meta (conjunto de datos «OdooListo web»): solo con consentimiento
  var META_PIXEL = '1653138256227151';
  function loadMeta() {
    if (LOCAL || window.fbq) return;
    !function (f, b, e, v, n, t, s) {
      if (f.fbq) return; n = f.fbq = function () { n.callMethod ? n.callMethod.apply(n, arguments) : n.queue.push(arguments); };
      if (!f._fbq) f._fbq = n; n.push = n; n.loaded = !0; n.version = '2.0'; n.queue = [];
      t = b.createElement(e); t.async = !0; t.src = v; s = b.getElementsByTagName(e)[0]; s.parentNode.insertBefore(t, s);
    }(window, document, 'script', 'https://connect.facebook.net/en_US/fbevents.js');
    fbq('init', META_PIXEL);
    fbq('track', 'PageView');
  }

  // Microsoft Ads UET (etiqueta «OdooListo web»): solo con consentimiento
  var UET_ID = '187280237';
  function loadUet() {
    if (LOCAL || window.__olUet) return;
    window.__olUet = true;
    (function (w, d, t, r, u) {
      var f, n, i; w[u] = w[u] || [];
      f = function () { var o = { ti: UET_ID, enableAutoSpaTracking: true }; o.q = w[u]; w[u] = new UET(o); w[u].push('pageLoad'); };
      n = d.createElement(t); n.src = r; n.async = 1;
      n.onload = n.onreadystatechange = function () { var s = this.readyState; s && s !== 'loaded' && s !== 'complete' || (f(), n.onload = n.onreadystatechange = null); };
      i = d.getElementsByTagName(t)[0]; i.parentNode.insertBefore(n, i);
    })(window, document, 'script', '//bat.bing.com/bat.js', 'uetq');
  }

  function grant() {
    loadMeta(); loadUet();
    if (typeof gtag === 'function') {
      gtag('consent', 'update', {
        ad_storage: 'granted', ad_user_data: 'granted',
        ad_personalization: 'granted', analytics_storage: 'granted'
      });
    }
    loadClarity();
    if (typeof window.olOnConsent === 'function') { try { window.olOnConsent(); } catch (e) {} }
  }

  function deny() {
    if (typeof gtag === 'function') {
      gtag('consent', 'update', {
        ad_storage: 'denied', ad_user_data: 'denied',
        ad_personalization: 'denied', analytics_storage: 'denied'
      });
    }
  }

  var css = '#olcb{position:fixed;left:16px;right:16px;bottom:16px;z-index:9999;max-width:760px;margin:0 auto;' +
    'background:#1C0F5E;color:#fff;border-radius:14px;padding:16px 18px;box-shadow:0 10px 40px rgba(0,0,0,.25);' +
    'font:500 14px/1.5 Nunito,system-ui,sans-serif;display:flex;gap:14px;align-items:center;flex-wrap:wrap}' +
    '#olcb p{margin:0;flex:1;min-width:220px;color:rgba(255,255,255,.85)}' +
    '#olcb a{color:#4DD9D6;text-decoration:underline}' +
    '#olcb .b{display:flex;gap:8px;flex-shrink:0}' +
    '#olcb button{font:700 14px Nunito,system-ui,sans-serif;border-radius:8px;padding:9px 18px;cursor:pointer}' +
    '#olcb .r{background:transparent;color:#fff;border:1px solid rgba(255,255,255,.45)}' +
    '#olcb .a{background:#00A09D;color:#fff;border:1px solid #00A09D}';

  function banner() {
    if (document.getElementById('olcb')) return;
    var en = (document.documentElement.getAttribute('lang') || '').indexOf('en') === 0 ||
      (function () { try { return localStorage.getItem('odoolisto_lang') === 'en'; } catch (e) { return false; } })();
    var st = document.createElement('style'); st.textContent = css; document.head.appendChild(st);
    var d = document.createElement('div'); d.id = 'olcb'; d.setAttribute('role', 'dialog');
    d.setAttribute('aria-label', en ? 'Cookies' : 'Cookies');
    d.innerHTML = en
      ? '<p>We use analytics and advertising cookies (Google, Meta, Microsoft) only if you accept them. <a href="/#cookies">Cookie policy</a>.</p>' +
        '<div class="b"><button class="r" type="button">Reject</button><button class="a" type="button">Accept</button></div>'
      : '<p>Usamos cookies de análisis y publicidad (Google, Meta, Microsoft) solo si las aceptas. <a href="/#cookies">Política de cookies</a>.</p>' +
        '<div class="b"><button class="r" type="button">Rechazar</button><button class="a" type="button">Aceptar</button></div>';
    d.querySelector('.r').onclick = function () { set('none'); deny(); d.remove(); };
    d.querySelector('.a').onclick = function () { set('all'); grant(); d.remove(); };
    document.body.appendChild(d);
  }

  // Reenvía a Meta los eventos de conversión que la web ya manda a GA4 (solo si el píxel está cargado)
  var MAP = { generate_lead: 'Lead', begin_checkout: 'InitiateCheckout', purchase: 'Purchase', formulario_contacto: 'Contact' };
  var UMAP = { generate_lead: 'sign_up', begin_checkout: 'begin_checkout', purchase: 'purchase', formulario_contacto: 'contact' };
  window.dataLayer = window.dataLayer || [];
  var push = window.dataLayer.push;
  window.dataLayer.push = function () {
    var a = arguments[0];
    try {
      if (a && a[0] === 'event' && MAP[a[1]] && typeof window.fbq === 'function') {
        var p = a[2] || {}, d = {};
        if (p.value) { d.value = p.value; d.currency = p.currency || 'EUR'; }
        window.fbq('track', MAP[a[1]], d, p.transaction_id ? { eventID: p.transaction_id } : undefined);
      }
      if (a && a[0] === 'event' && MAP[a[1]] && window.__olUet) {
        var q = a[2] || {}; window.uetq = window.uetq || [];
        window.uetq.push('event', UMAP[a[1]], q.value ? { revenue_value: q.value, currency: q.currency || 'EUR' } : {});
      }
    } catch (e) {}
    return push.apply(window.dataLayer, arguments);
  };

  // Reabrir el banner (enlace «Cambiar mis preferencias de cookies»)
  window.olConsentOpen = function () { banner(); };

  var c = get();
  if (c === 'all') {
    loadClarity(); loadMeta(); loadUet();
    // Eventos lanzados antes de cargar este script (p. ej. purchase en /gracias)
    try {
      window.dataLayer.forEach(function (a) {
        if (a && a[0] === 'event' && MAP[a[1]] && typeof window.fbq === 'function') {
          var p = a[2] || {}, d = {};
          if (p.value) { d.value = p.value; d.currency = p.currency || 'EUR'; }
          window.fbq('track', MAP[a[1]], d, p.transaction_id ? { eventID: p.transaction_id } : undefined);
        }
        if (a && a[0] === 'event' && MAP[a[1]] && window.__olUet) {
          var q = a[2] || {}; window.uetq = window.uetq || [];
          window.uetq.push('event', UMAP[a[1]], q.value ? { revenue_value: q.value, currency: q.currency || 'EUR' } : {});
        }
      });
    } catch (e) {}
  }
  else if (c !== 'none') {
    if (document.body) banner(); else document.addEventListener('DOMContentLoaded', banner);
  }
})();
