/*
  Registro de consultas del formulario (src/site.js manda cada una acá con sendBeacon antes de abrir WhatsApp).
  Guarda la consulta con su código y el clic de Google, y avisa por correo al momento.
  Así no se pierde aunque la persona no toque "enviar" en su WhatsApp.

  Cloudflare Pages → Settings:
    Bindings → D1 database   DB           base "eds-consultas" (la tabla se crea sola)
    Variables and secrets    RESEND_KEY   clave de resend.com (secreto)
                             AVISO_A      correo donde llega el aviso
                             AVISO_DE     remitente (opcional; sin dominio verificado en Resend
                                          se usa onboarding@resend.dev, que solo manda al dueño de la cuenta)
  Si falta la base, igual avisa; si falta el correo, igual guarda.
*/

const SCHEMA = `CREATE TABLE IF NOT EXISTS consultas (
  ref TEXT PRIMARY KEY,
  created_at TEXT NOT NULL,
  received_at TEXT NOT NULL,
  lang TEXT, phone TEXT, idea TEXT, size TEXT, stay TEXT,
  visitor INTEGER, foreign_phone INTEGER,
  click_type TEXT, click_id TEXT, click_at TEXT,
  page TEXT, referrer TEXT, country TEXT, ip_hash TEXT
)`;

const ORIGINS = /^https:\/\/([a-z0-9-]+\.)?(edstattoostudio\.com|edstattoostudio\.pages\.dev)$|^http:\/\/(localhost|127\.0\.0\.1)(:\d+)?$/;
const MAX_BODY = 8192;
const MAX_POR_IP = 5; // consultas por IP cada 10 minutos; más que eso no se guarda ni avisa

const clip = (v, n) => String(v ?? "").slice(0, n);
const esc = (s) => String(s).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c]);

async function sha(text) {
  const d = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(text));
  return [...new Uint8Array(d)].slice(0, 12).map((b) => b.toString(16).padStart(2, "0")).join("");
}

function horaBA(iso) {
  try {
    return new Intl.DateTimeFormat("es-AR", { timeZone: "America/Argentina/Buenos_Aires", dateStyle: "short", timeStyle: "short" }).format(new Date(iso));
  } catch (e) { return iso; }
}

function limpiar(raw, received, country, ipHash) {
  const ref = clip(raw.ref, 20);
  const phone = clip(raw.phone, 20);
  if (!/^EDS-[2-9A-Z]{5}$/.test(ref) || !/^\+[1-9]\d{7,14}$/.test(phone)) return null;
  const clickType = ["gclid", "gbraid", "wbraid"].includes(raw.click_type) ? raw.click_type : "";
  return {
    ref,
    created_at: clip(raw.created_at, 40) || received,
    received_at: received,
    lang: clip(raw.lang, 5),
    phone,
    idea: clip(raw.idea, 1500),
    size: clip(raw.size, 60),
    stay: clip(raw.stay, 40),
    visitor: raw.visitor ? 1 : 0,
    foreign_phone: raw.foreign_phone ? 1 : 0,
    click_type: clickType,
    click_id: clickType ? clip(raw.click_id, 200) : "",
    click_at: clickType ? clip(raw.click_at, 40) : "",
    page: clip(raw.page, 400),
    referrer: clip(raw.referrer, 400),
    country: clip(country, 2),
    ip_hash: ipHash
  };
}

async function guardar(db, c) {
  await db.prepare(SCHEMA).run();
  const desde = new Date(Date.now() - 10 * 60 * 1000).toISOString();
  const { n } = await db.prepare("SELECT COUNT(*) AS n FROM consultas WHERE ip_hash = ? AND received_at > ?").bind(c.ip_hash, desde).first();
  if (n >= MAX_POR_IP) return "limite";
  const cols = Object.keys(c);
  const r = await db.prepare(`INSERT OR IGNORE INTO consultas (${cols.join(",")}) VALUES (${cols.map(() => "?").join(",")})`)
    .bind(...cols.map((k) => c[k])).run();
  return r.meta && r.meta.changes ? "nueva" : "repetida";
}

async function avisar(env, c) {
  if (!env.RESEND_KEY || !env.AVISO_A) return;
  const tipo = c.visitor ? "visitante" : "local";
  const waCliente = "https://wa.me/" + c.phone.replace(/\D/g, "") + "?text=" + encodeURIComponent("Hola! Te escribo de EDS Tattoo Studio por tu consulta " + c.ref + ".");
  const filas = [
    ["Código", c.ref],
    ["Tipo", tipo + (c.foreign_phone ? " (WhatsApp de afuera)" : "")],
    ["WhatsApp", c.phone],
    ["Idea", c.idea],
    ["Tamaño", c.size],
    ["Estadía", c.stay || "sin marcar"],
    ["Idioma de la página", c.lang],
    ["Clic de Google", c.click_type ? c.click_type + " (vino de un anuncio)" : "no"],
    ["País (Cloudflare)", c.country || "?"],
    ["Hora (Buenos Aires)", horaBA(c.received_at)]
  ];
  const html = `<p><a href="${esc(waCliente)}">Escribirle por WhatsApp</a></p><table cellpadding="4">` +
    filas.map(([k, v]) => `<tr><td><b>${esc(k)}</b></td><td>${esc(v).replace(/\n/g, "<br>")}</td></tr>`).join("") +
    `</table><p style="color:#666">Si ya escribió al WhatsApp del estudio, el mensaje trae este mismo código.</p>`;
  const text = filas.map(([k, v]) => k + ": " + v).join("\n") + "\n\nEscribirle: " + waCliente;
  const r = await fetch("https://api.resend.com/emails", {
    method: "POST",
    headers: { authorization: "Bearer " + env.RESEND_KEY, "content-type": "application/json" },
    body: JSON.stringify({
      from: env.AVISO_DE || "EDS consultas <onboarding@resend.dev>",
      to: env.AVISO_A.split(",").map((s) => s.trim()).filter(Boolean),
      subject: `Consulta ${c.ref}, ${tipo}: ${clip(c.idea, 60)}`,
      html,
      text
    })
  });
  if (!r.ok) console.error("aviso por correo falló", r.status, await r.text());
}

export async function onRequestPost({ request, env, waitUntil }) {
  const origin = request.headers.get("origin") || "";
  if (origin && !ORIGINS.test(origin)) return new Response(null, { status: 403 });

  const body = await request.text();
  if (body.length > MAX_BODY) return new Response(null, { status: 413 });
  let raw;
  try { raw = JSON.parse(body); } catch (e) { return new Response(null, { status: 400 }); }

  const received = new Date().toISOString();
  const ip = request.headers.get("cf-connecting-ip") || "";
  const c = limpiar(raw || {}, received, request.cf && request.cf.country, await sha(ip + "|eds"));
  if (!c) return new Response(null, { status: 400 });

  let estado = "sin-base";
  if (env.DB) {
    try { estado = await guardar(env.DB, c); } catch (e) { console.error("no se pudo guardar la consulta", e); }
  }
  if (estado !== "limite" && estado !== "repetida") waitUntil(avisar(env, c).catch((e) => console.error("aviso", e)));
  return new Response(null, { status: 204, headers: { "cache-control": "no-store" } });
}
