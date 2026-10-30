(() => {
  "use strict";

  /* Datos del estudio. Lo que dice FALTA se completa cuando se prenda esa parte. */
  const CONFIG = {
    whatsapp: "5491122510832",   // +54 9 11 2251-0832 (el 9 es como WhatsApp arma los números de Argentina)
    analyticsId: "G-VS2YKG1P8B", // Google Analytics 4 (propiedad EDS Tattoo Studio)
    googleAdsId: "AW-11475190614",  // cuenta de Google Ads eduardo INK (147-493-6431)
    visitorConversionLabel: "K9xpCL3Xp6UdENaG5t8q",  // "Consulta visitante"
    localConversionLabel: "yAlwCMDXp6UdENaG5t8q",    // "Consulta local"
    visitorValue: 3,             // valor de una consulta de visitante (vale más: es el cliente que más interesa)
    localValue: 1,               // valor de una consulta local
    conversionCurrency: "USD",   // moneda de esos valores (son pesos relativos, no plata real)
    leadEndpoint: "/api/consulta", // guarda cada consulta y avisa por correo (functions/api/consulta.js)
    googleMapsKey: "",           // FALTA: clave de Google Maps Platform, restringida a edstattoostudio.com
    placeId: "ChIJSbT071_LvJURa8aGV8tGUIY",                 // ID del estudio en Google Maps; sin él se busca una vez por nombre y dirección
    placeQuery: "EDS Tattoo, San Martín 569, Buenos Aires"
  };
  const MAPS_FALLBACK = "https://www.google.com/maps/search/?api=1&query=EDS%20Tattoo%20Studio&query_place_id=ChIJSbT071_LvJURa8aGV8tGUIY";

  const $ = (id) => document.getElementById(id);
  const el = (tag, cls) => { const n = document.createElement(tag); if (cls) n.className = cls; return n; };
  const store = {
    get(k) { try { return localStorage.getItem(k); } catch (e) { return null; } },
    set(k, v) { try { localStorage.setItem(k, v); } catch (e) { /* sin almacenamiento */ } }
  };
  const reducedMotion = () => { try { return matchMedia("(prefers-reduced-motion: reduce)").matches; } catch (e) { return false; } };

  /* Lupas: usan la misma foto ya descargada, así no se baja nada de más.
     La de arriba muestra primero la versión chica y, cuando terminó de cargar la página, pasa a la grande. */
  document.querySelectorAll("[data-loupe]").forEach((box) => {
    const img = box.querySelector("img");
    const loupe = box.querySelector(".loupe");
    if (!img || !loupe) return;
    const set = (u) => { loupe.style.backgroundImage = 'url("' + u + '")'; };
    const fromImg = () => set(img.currentSrc || img.src);
    if (img.complete && img.naturalWidth) fromImg(); else img.addEventListener("load", fromImg, { once: true });
    const full = img.dataset.full;
    if (full) {
      const upgrade = () => { const pre = new Image(); pre.onload = () => set(full); pre.src = full; };
      if (document.readyState === "complete") upgrade(); else window.addEventListener("load", upgrade, { once: true });
    }
  });

  /* Guardar el clic del anuncio de Google (gclid, gbraid o wbraid) por 90 días, en cualquier página */
  /* Consentimiento (modo de consentimiento v2 de Google).
     En el Espacio Económico Europeo, el Reino Unido y Suiza todo arranca denegado hasta que la persona acepta
     (Google aplica esa región por su cuenta según la ubicación). El aviso se muestra a quien tiene el teléfono
     en hora de Europa; cualquiera puede cambiar su elección desde "Cookies" al pie. */
  const CONSENT_REGIONS = ["AT","BE","BG","HR","CY","CZ","DK","EE","FI","FR","DE","GR","HU","IS","IE","IT","LV","LI","LT",
    "LU","MT","NL","NO","PL","PT","RO","SK","SI","ES","SE","GB","CH"];
  const inEuropeTime = (() => {
    try {
      const tz = Intl.DateTimeFormat().resolvedOptions().timeZone || "";
      return /^Europe\//.test(tz) || /^Atlantic\/(Canary|Madeira|Azores|Reykjavik|Faroe)$/.test(tz);
    } catch (e) { return false; }
  })();
  const consentChoice = () => { const v = store.get("eds_consent"); return v === "granted" || v === "denied" ? v : null; };
  const consentOk = () => { const c = consentChoice(); return c ? c === "granted" : !inEuropeTime; };

  /* Clic del anuncio de Google (gclid, gbraid o wbraid): se guarda 90 días solo si hay consentimiento */
  let pendingClick = null;
  (function captureClick() {
    let params;
    try { params = new URLSearchParams(location.search); } catch (e) { return; }
    for (const key of ["gclid", "gbraid", "wbraid"]) {
      const id = params.get(key);
      if (id) {
        pendingClick = { type: key, id, ts: Date.now() };
        if (consentOk()) store.set("eds_click", JSON.stringify(pendingClick));
        return;
      }
    }
  })();
  function readClick() {
    const raw = store.get("eds_click");
    if (!raw) return pendingClick;
    try {
      const c = JSON.parse(raw);
      return Date.now() - c.ts > 90 * 864e5 ? null : c;
    } catch (e) { return pendingClick; }
  }

  /* Etiqueta de Google (Analytics + Ads), sin Tag Manager */
  /* Las etiquetas de Google solo corren en el dominio real: en las vistas previas (*.pages.dev) o en la PC
     una prueba del formulario no tiene que contar como consulta en Google Ads ni como visita en Analytics */
  const liveHost = /(^|\.)edstattoostudio\.com$/.test(location.hostname);
  const tagIds = liveHost ? [CONFIG.analyticsId, CONFIG.googleAdsId].filter(Boolean) : [];
  const consentState = (on) => {
    const v = on ? "granted" : "denied";
    return { ad_storage: v, ad_user_data: v, ad_personalization: v, analytics_storage: v };
  };
  (function loadGtag() {
    if (!tagIds.length) return;
    window.dataLayer = window.dataLayer || [];
    window.gtag = function () { window.dataLayer.push(arguments); };
    const g = window.gtag;
    g("consent", "default", Object.assign(consentState(false), { region: CONSENT_REGIONS, wait_for_update: 500 }));
    g("consent", "default", consentState(true));
    const c = consentChoice();
    if (c) g("consent", "update", consentState(c === "granted"));
    g("set", "url_passthrough", true);
    g("set", "ads_data_redaction", true);
    g("js", new Date());
    tagIds.forEach((id) => g("config", id));
    const s = document.createElement("script");
    s.async = true;
    s.src = "https://www.googletagmanager.com/gtag/js?id=" + encodeURIComponent(tagIds[0]);
    document.head.appendChild(s);
  })();

  /* Aviso de cookies */
  const CONSENT_TEXT = {
    es: { msg: "Uso cookies de Google Analytics y Google Ads para saber cuánta gente visita la página y qué anuncios traen consultas.", more: "Más información", yes: "Aceptar", no: "Rechazar", label: "Cookies", path: "/es/privacidad/" },
    pt: { msg: "Uso cookies do Google Analytics e do Google Ads para saber quantas pessoas visitam a página e quais anúncios trazem contatos.", more: "Saiba mais", yes: "Aceitar", no: "Recusar", label: "Cookies", path: "/pt/privacidade/" },
    en: { msg: "I use Google Analytics and Google Ads cookies to know how many people visit this page and which ads bring inquiries.", more: "Learn more", yes: "Accept", no: "Reject", label: "Cookies", path: "/en/privacy/" },
    de: { msg: "Ich nutze Cookies von Google Analytics und Google Ads, um zu wissen, wie viele Menschen die Seite besuchen und welche Anzeigen Anfragen bringen.", more: "Mehr erfahren", yes: "Akzeptieren", no: "Ablehnen", label: "Cookies", path: "/de/datenschutz/" }
  };
  function setConsent(on) {
    store.set("eds_consent", on ? "granted" : "denied");
    if (typeof window.gtag === "function") window.gtag("consent", "update", consentState(on));
    if (on && pendingClick) store.set("eds_click", JSON.stringify(pendingClick));
    if (!on) { try { localStorage.removeItem("eds_click"); } catch (e) { /* sin almacenamiento */ } }
  }
  function showConsent() {
    if (!tagIds.length) return;
    const old = document.querySelector(".consent");
    if (old) { old.querySelector("button").focus(); return; }
    const lang = (document.documentElement.lang || "en").slice(0, 2).toLowerCase();
    const L = CONSENT_TEXT[lang] || CONSENT_TEXT.en;
    const box = el("div", "consent");
    box.setAttribute("role", "region");
    box.setAttribute("aria-label", L.label);
    const p = el("p");
    p.textContent = L.msg + " ";
    const a = el("a");
    a.href = L.path;
    a.textContent = L.more;
    p.appendChild(a);
    const row = el("div", "consent-actions");
    const no = el("button", "btn btn-line");
    no.type = "button";
    no.textContent = L.no;
    const yes = el("button", "btn");
    yes.type = "button";
    yes.textContent = L.yes;
    const close = (on) => { setConsent(on); box.remove(); };
    no.addEventListener("click", () => close(false));
    yes.addEventListener("click", () => close(true));
    row.append(no, yes);
    box.append(p, row);
    document.body.appendChild(box);
  }
  if (tagIds.length && inEuropeTime && !consentChoice()) showConsent();
  document.querySelectorAll("[data-cookie-settings]").forEach((b) => {
    if (!tagIds.length) { b.hidden = true; return; }
    b.addEventListener("click", showConsent);
  });

  /* Lo que sigue es solo para las páginas de cada idioma */
  const cfgEl = $("eds-page");
  if (!cfgEl) return;
  const P = JSON.parse(cfgEl.textContent);
  const t = (key) => P.t[key] || "";

  function makeRef() {
    const abc = "23456789ABCDEFGHJKMNPQRSTUVWXYZ";
    const buf = new Uint32Array(5);
    try { crypto.getRandomValues(buf); } catch (e) { for (let i = 0; i < 5; i++) buf[i] = Math.floor(Math.random() * 1e9); }
    let r = "";
    for (let i = 0; i < 5; i++) r += abc[buf[i] % abc.length];
    return "EDS-" + r;
  }

  /* Número en formato internacional (+ y código de país), que es como lo pide Google */
  function normPhone(v) {
    let s = String(v || "").trim().replace(/[\s\-().]/g, "");
    if (s.startsWith("00")) s = "+" + s.slice(2);
    return /^\+[1-9]\d{7,14}$/.test(s) ? s : null;
  }

  function fmtDate(iso) {
    try {
      return new Intl.DateTimeFormat(P.locale, { day: "numeric", month: "long" }).format(new Date(iso + "T12:00:00"));
    } catch (e) { return iso; }
  }

  function checkedIdx(name) {
    const n = document.querySelector('input[name="' + name + '"]:checked');
    return n ? Number(n.value) : -1;
  }

  /* Errores del formulario */
  const FIELD_INPUT = { idea: "f-idea", phone: "f-phone" };
  function showError(field, key) {
    const n = $("err-" + field);
    n.textContent = t(key);
    n.hidden = false;
    if (FIELD_INPUT[field]) $(FIELD_INPUT[field]).setAttribute("aria-invalid", "true");
  }
  function clearError(field) {
    const n = $("err-" + field);
    if (n) n.hidden = true;
    if (FIELD_INPUT[field]) $(FIELD_INPUT[field]).removeAttribute("aria-invalid");
  }
  function focusField(field) {
    if (FIELD_INPUT[field]) { $(FIELD_INPUT[field]).focus(); return; }
    const first = document.querySelector('input[name="' + field + '"]');
    if (first) first.focus();
  }

  function showDone(text, url, ref) {
    $("done-code").textContent = ref;
    $("done-msg").textContent = text;
    $("done-open").href = url;
    const done = $("done");
    done.hidden = false;
    done.scrollIntoView({ behavior: reducedMotion() ? "auto" : "smooth", block: "nearest" });
  }

  function onSubmit(e) {
    e.preventDefault();
    ["idea", "size", "stay", "phone"].forEach(clearError);

    const idea = $("f-idea").value.trim();
    const sizeI = checkedIdx("size");
    const stayI = checkedIdx("stay");
    const phone = normPhone($("f-phone").value);

    const errs = [];
    if (!idea) errs.push(["idea", "err.idea"]);
    if (sizeI < 0) errs.push(["size", "err.size"]);
    if (stayI < 0) errs.push(["stay", "err.stay"]);
    if (!phone) errs.push(["phone", "err.phone"]);
    if (errs.length) {
      errs.forEach(([f, k]) => showError(f, k));
      focusField(errs[0][0]);
      return;
    }

    const ref = makeRef();
    const lines = [
      t("msg.hello"),
      "",
      t("msg.idea") + ": " + idea,
      t("msg.size") + ": " + P.sizes[sizeI]
    ];
    if (stayI === 0) lines.push(t("msg.local"));
    if (stayI === 1) lines.push(t("msg.travel"));
    lines.push(t("msg.code") + ": " + ref);
    const text = lines.join("\n");
    const waUrl = "https://wa.me/" + CONFIG.whatsapp + "?text=" + encodeURIComponent(text);

    /* Visitante: lo que marcó en el formulario o, como segunda prueba, un número que no es de Argentina */
    const foreignPhone = !phone.startsWith("+54");
    const visitor = stayI === 1 || foreignPhone;

    /* Google Ads: una conversión distinta para visitante y para local, con su valor.
       El WhatsApp viaja cifrado por la etiqueta (conversiones avanzadas para clientes potenciales). */
    const label = visitor ? CONFIG.visitorConversionLabel : CONFIG.localConversionLabel;
    if (typeof window.gtag === "function" && CONFIG.googleAdsId && label) {
      window.gtag("set", "user_data", { phone_number: phone });
      window.gtag("event", "conversion", {
        send_to: CONFIG.googleAdsId + "/" + label,
        value: visitor ? CONFIG.visitorValue : CONFIG.localValue,
        currency: CONFIG.conversionCurrency,
        transaction_id: ref
      });
      /* Analytics: la misma consulta como evento clave */
      if (CONFIG.analyticsId) window.gtag("event", "generate_lead", {
        send_to: CONFIG.analyticsId,
        value: visitor ? CONFIG.visitorValue : CONFIG.localValue,
        currency: CONFIG.conversionCurrency,
        lead_source: visitor ? "visitante" : "local"
      });
    }

    /* Registro de la consulta: con esto después se sube a Google quién se tatuó y cuánto pagó */
    const click = readClick();
    const lead = {
      ref,
      created_at: new Date().toISOString(),
      lang: P.lang,
      phone,
      idea,
      size: P.sizesEs[sizeI],
      stay: stayI === 1 ? "de visita" : stayI === 0 ? "vive en Buenos Aires" : "",
      foreign_phone: foreignPhone,
      visitor,
      click_type: click ? click.type : "",
      click_id: click ? click.id : "",
      click_at: click ? new Date(click.ts).toISOString() : "",
      page: location.href,
      referrer: document.referrer
    };
    if (CONFIG.leadEndpoint && navigator.sendBeacon) {
      try { navigator.sendBeacon(CONFIG.leadEndpoint, new Blob([JSON.stringify(lead)], { type: "text/plain;charset=UTF-8" })); } catch (err) { /* sin conexión al registro */ }
    }

    showDone(text, waUrl, ref);
    if (window.top === window.self) setTimeout(() => { location.href = waUrl; }, 450);
  }

  /* Reseñas reales de Google (Maps JavaScript API, clase Place). Se piden en vivo, sin guardarlas. */
  let lastPlace = null;
  let reviewsRequested = false;
  let mapsReady = null;

  function renderSummary() {
    if (!lastPlace || !lastPlace.rating || !lastPlace.userRatingCount) return;
    const r = new Intl.NumberFormat(P.locale, { minimumFractionDigits: 1, maximumFractionDigits: 1 }).format(lastPlace.rating);
    const n = new Intl.NumberFormat(P.locale).format(lastPlace.userRatingCount);
    $("reviews-summary").textContent = t("reviews.live").replace("{r}", r).replace("{n}", n);
  }

  function loadMaps() {
    if (mapsReady) return mapsReady;
    mapsReady = new Promise((resolve, reject) => {
      window.__edsMapsReady = () => resolve();
      const s = document.createElement("script");
      s.async = true;
      s.src = "https://maps.googleapis.com/maps/api/js?key=" + encodeURIComponent(CONFIG.googleMapsKey) +
        "&v=weekly&loading=async&language=" + encodeURIComponent(P.apiLang) + "&callback=__edsMapsReady";
      s.onerror = () => reject(new Error("maps"));
      document.head.appendChild(s);
    });
    return mapsReady;
  }

  function reviewItem(r) {
    const li = el("li", "review");
    const head = el("div", "review-head");
    const a = r.authorAttribution || {};
    if (a.photoURI) {
      const img = el("img", "avatar");
      img.src = a.photoURI; img.alt = ""; img.width = 36; img.height = 36;
      img.loading = "lazy"; img.referrerPolicy = "no-referrer";
      head.append(img);
    } else {
      const ini = el("span", "avatar");
      ini.textContent = (a.displayName || "G").trim().charAt(0).toUpperCase();
      head.append(ini);
    }
    const who = el("div", "who");
    const name = el(a.uri ? "a" : "span", "author");
    name.textContent = a.displayName || "Google";
    if (a.uri) { name.href = a.uri; name.target = "_blank"; name.rel = "noopener"; }
    const meta = el("div", "meta");
    const stars = el("span", "stars");
    stars.textContent = "★".repeat(Math.max(0, Math.min(5, Math.round(r.rating || 0))));
    stars.setAttribute("aria-label", t("reviews.starsLabel").replace("{n}", String(r.rating || "")));
    const when = el("span");
    when.textContent = r.relativePublishTimeDescription || "";
    meta.append(stars, when);
    who.append(name, meta);
    head.append(who);
    const text = el("p", "review-text");
    text.textContent = String(r.text || "").trim();
    const foot = el("p", "review-foot");
    if (r.originalText && r.textLanguageCode && r.originalTextLanguageCode && r.textLanguageCode !== r.originalTextLanguageCode) {
      const tr = el("span"); tr.textContent = t("reviews.translated"); foot.append(tr);
    }
    const link = el("a");
    link.href = r.googleMapsURI || (lastPlace && lastPlace.googleMapsURI) || MAPS_FALLBACK;
    link.target = "_blank"; link.rel = "noopener"; link.textContent = t("reviews.onMaps");
    foot.append(link);
    li.append(head, text, foot);
    return li;
  }

  async function fetchReviews() {
    await loadMaps();
    const { Place } = await google.maps.importLibrary("places");
    let id = CONFIG.placeId || store.get("eds_place_id");
    if (!id) {
      const res = await Place.searchByText({ textQuery: CONFIG.placeQuery, fields: ["id"], maxResultCount: 1 });
      id = res && res.places && res.places[0] && res.places[0].id;
      if (!id) return;
      store.set("eds_place_id", id);
      console.info("ID de EDS Tattoo en Google Maps:", id);
    }
    const place = new Place({ id, requestedLanguage: P.apiLang });
    await place.fetchFields({ fields: ["rating", "userRatingCount", "reviews", "googleMapsURI"] });
    lastPlace = place;
    renderSummary();
    if (place.googleMapsURI) $("reviews-link").href = place.googleMapsURI;
    const reviews = (place.reviews || []).slice(0, 5);
    if (!reviews.length) return;
    $("reviews-list").replaceChildren(...reviews.map(reviewItem));
    $("gm-box").hidden = false;
  }

  function initReviews() {
    if (!CONFIG.googleMapsKey || !$("resenas")) return;
    const go = () => {
      if (reviewsRequested) return;
      reviewsRequested = true;
      fetchReviews().catch(() => { /* queda el enlace a Google */ });
    };
    if (!("IntersectionObserver" in window)) { go(); return; }
    const io = new IntersectionObserver((entries) => {
      if (entries.some((en) => en.isIntersecting)) { io.disconnect(); go(); }
    }, { rootMargin: "800px 0px" });
    io.observe($("resenas"));
  }

  function initCopy() {
    const btn = $("done-copy");
    btn.addEventListener("click", () => {
      const text = $("done-msg").textContent;
      const ok = () => { btn.textContent = t("done.copied"); setTimeout(() => { btn.textContent = t("done.copy"); }, 2000); };
      const selectText = () => {
        const r = document.createRange();
        r.selectNodeContents($("done-msg"));
        const sel = window.getSelection();
        sel.removeAllRanges(); sel.addRange(r);
      };
      try { navigator.clipboard.writeText(text).then(ok, selectText); } catch (err) { selectText(); }
    });
  }

  /* Botón fijo del celular: entra desde abajo cuando el botón de arriba ya no se ve y se va
     cuando aparece el formulario (mismo camino de ida y de vuelta) */
  function initSticky() {
    const sticky = $("sticky");
    if (!sticky || !("IntersectionObserver" in window)) return;
    sticky.hidden = false;
    let heroVisible = true, formVisible = false;
    const io = new IntersectionObserver((entries) => {
      entries.forEach((en) => {
        if (en.target.id === "hero-cta") heroVisible = en.isIntersecting;
        if (en.target.id === "idea") formVisible = en.isIntersecting;
      });
      const on = !heroVisible && !formVisible;
      sticky.classList.toggle("on", on);
      sticky.inert = !on;
    });
    io.observe($("hero-cta"));
    io.observe($("idea"));
  }

  /* Carrusel de trabajos como un tren: corre solo, despacio y sin fin (hay una segunda vuelta igual
     y al terminar la primera se salta al mismo punto de la otra, sin que se note).
     Se frena mientras la persona lo toca, lo arrastra, pasa el mouse o usa las flechas, y vuelve a
     andar a los pocos segundos. Quien pidió menos movimiento en su teléfono lo ve quieto, con imán. */
  function initCarousel() {
    const track = $("track");
    if (!track) return;
    const slides = [...track.querySelectorAll(".slide:not(.clone)")];
    const n = slides.length;
    const now = $("car-now"), fill = $("car-fill");
    const btns = document.querySelectorAll("[data-dir][aria-controls='track']");
    const train = !reducedMotion() && n > 1;
    if (train) track.classList.add("train");
    const firstClone = track.querySelector(".slide.clone");
    // largo exacto de una vuelta (de la primera foto a su copia); el paso de una foto sale de ahí
    const lap = () => (train && firstClone ? firstClone.offsetLeft - slides[0].offsetLeft : track.scrollWidth);
    const step = () => (train ? lap() / n : (slides[1] ? slides[1].offsetLeft - slides[0].offsetLeft : track.clientWidth));

    let pos = 0, lastSet = -1, ticking = false;
    const update = () => {
      ticking = false;
      const x = track.scrollLeft;
      if (train) {
        // vuelta sin fin: pasada la primera vuelta (o antes del principio) se salta a la copia
        const L = lap();
        if (x >= L) { track.scrollLeft = x - L; pos = track.scrollLeft; lastSet = pos; }
      }
      const xs = train ? track.scrollLeft % lap() : track.scrollLeft;
      const i = ((Math.round(xs / step()) % n) + n) % n;
      now.textContent = String(i + 1);
      const max = train ? lap() : Math.max(1, track.scrollWidth - track.clientWidth);
      fill.style.transform = "scaleX(" + Math.max(0.08, Math.min(1, xs / max)).toFixed(4) + ")";
    };

    // marcha: velocidad suave, más lenta en el celular
    const SPEED = matchMedia("(max-width: 640px)").matches ? 26 : 38; // px por segundo
    let running = train, hover = false, visible = true, resumeAt = 0, prev = 0;
    const holdFor = (ms) => { resumeAt = performance.now() + ms; };
    const loop = (tm) => {
      const dt = prev ? Math.min(64, tm - prev) / 1000 : 0;
      prev = tm;
      if (running && !hover && visible && !document.hidden && tm >= resumeAt) {
        if (Math.abs(track.scrollLeft - lastSet) > 2) pos = track.scrollLeft; // la persona lo movió
        pos += SPEED * dt;
        const L = lap();
        if (pos >= L) pos -= L;
        track.scrollLeft = pos;
        lastSet = track.scrollLeft;
      }
      requestAnimationFrame(loop);
    };

    track.addEventListener("scroll", () => {
      if (Math.abs(track.scrollLeft - lastSet) > 2) holdFor(3500); // lo está moviendo la persona
      if (!ticking) { ticking = true; requestAnimationFrame(update); }
    }, { passive: true });
    window.addEventListener("resize", update, { passive: true });

    if (train) {
      track.addEventListener("pointerenter", (e) => { if (e.pointerType === "mouse") hover = true; });
      track.addEventListener("pointerleave", (e) => { if (e.pointerType === "mouse") { hover = false; holdFor(600); } });
      ["pointerdown", "wheel", "keydown", "focusin"].forEach((ev) =>
        track.addEventListener(ev, () => holdFor(4000), { passive: true }));
      if ("IntersectionObserver" in window) {
        new IntersectionObserver((es) => { visible = es[0].isIntersecting; }).observe(track);
      }
      holdFor(1200); // arranca después de que se vio la primera foto
      requestAnimationFrame(loop);
    }

    // flechas y aviso: una foto por toque, siempre alineada; en el tren no hay principio ni fin
    btns.forEach((btn) => btn.addEventListener("click", () => {
      const dir = Number(btn.dataset.dir);
      holdFor(5000);
      const s = step();
      let x = track.scrollLeft;
      if (train && dir < 0 && x < s) { x += lap(); track.scrollLeft = x; }
      const target = (Math.round(x / s) + dir) * s;
      track.scrollTo({ left: Math.max(0, target), behavior: reducedMotion() ? "auto" : "smooth" });
      lastSet = -1;
    }));
    update();
  }

  /* Secciones que aparecen al bajar. Solo se esconden las que todavía no se ven,
     así nada de lo que ya está en pantalla parpadea al cargar */
  function initReveal() {
    if (!("IntersectionObserver" in window)) return;
    const blocks = [...document.querySelectorAll("main .block")]
      .filter((el) => el.getBoundingClientRect().top > window.innerHeight);
    if (!blocks.length) return;
    const io = new IntersectionObserver((entries) => {
      entries.forEach((en) => {
        if (en.isIntersecting) { en.target.classList.add("in"); io.unobserve(en.target); }
      });
    }, { rootMargin: "0px 0px -12% 0px" });
    blocks.forEach((el) => { el.classList.add("reveal"); io.observe(el); });
  }

  /* Botón de mandar: neutro hasta que están los cuatro datos, verde WhatsApp cuando ya se puede.
     Sigue siempre activo: si falta algo y lo tocan, se marcan los errores como antes */
  function initReady() {
    const btn = $("f-submit");
    if (!btn) return;
    const check = () => {
      const ok = $("f-idea").value.trim() !== "" && checkedIdx("size") >= 0 &&
        checkedIdx("stay") >= 0 && !!normPhone($("f-phone").value);
      btn.classList.toggle("ready", ok);
    };
    form.addEventListener("input", check);
    form.addEventListener("change", check);
    check();
  }

  /* Arranque */
  const form = $("lead-form");
  form.addEventListener("submit", onSubmit);
  form.addEventListener("change", (e) => {
    const n = e.target.name;
    if (n === "size" || n === "stay") clearError(n);
  });
  form.addEventListener("input", (e) => {
    const n = e.target.name;
    if (n === "idea" || n === "phone") clearError(n);
  });
  initCopy();
  initReady();
  initSticky();
  initCarousel();
  initReveal();
  initReviews();
})();
