/*
  Lista de consultas guardadas (para revisar y para subir a Google Ads quién se tatuó).
  Uso:  GET /api/consultas            → JSON, las últimas 500
        GET /api/consultas?formato=csv
        Header  Authorization: Bearer <EDS_KEY>   (la misma llave del acceso a Meta)
*/

const COLS = ["ref", "received_at", "lang", "phone", "idea", "size", "stay", "visitor", "foreign_phone",
  "click_type", "click_id", "click_at", "page", "referrer", "country"];

function sameKey(a, b) {
  if (!a || !b || a.length !== b.length) return false;
  let r = 0;
  for (let i = 0; i < a.length; i++) r |= a.charCodeAt(i) ^ b.charCodeAt(i);
  return r === 0;
}

const csvCell = (v) => {
  const s = String(v ?? "");
  return /[",\n\r]/.test(s) ? '"' + s.replace(/"/g, '""') + '"' : s;
};

export async function onRequestGet({ request, env }) {
  const head = { "cache-control": "no-store", "x-robots-tag": "noindex" };
  const key = (request.headers.get("authorization") || "").replace(/^Bearer\s+/i, "");
  if (!sameKey(key, env.EDS_KEY || "")) return new Response("sin permiso", { status: 401, headers: head });
  if (!env.DB) return new Response("falta la base DB", { status: 503, headers: head });

  let rows = [];
  try {
    ({ results: rows } = await env.DB.prepare(`SELECT ${COLS.join(",")} FROM consultas ORDER BY received_at DESC LIMIT 500`).all());
  } catch (e) {
    if (!/no such table/i.test(String(e))) throw e; // todavía no llegó ninguna consulta
  }

  if (new URL(request.url).searchParams.get("formato") === "csv") {
    const csv = [COLS.join(","), ...rows.map((r) => COLS.map((c) => csvCell(r[c])).join(","))].join("\n") + "\n";
    return new Response(csv, { headers: { ...head, "content-type": "text/csv; charset=utf-8", "content-disposition": 'attachment; filename="consultas.csv"' } });
  }
  return new Response(JSON.stringify(rows, null, 1), { headers: { ...head, "content-type": "application/json; charset=utf-8" } });
}
