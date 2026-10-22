/*
  Acceso privado a Meta (Graph / Marketing API) para EDS Tattoo Studio.
  Solo del estudio: usa el token del usuario del sistema "edstattoo" (portfolio eduardoink).
  Nada de odontología pasa por acá.

  Uso:  /api/meta/v23.0/<ruta de Graph>?<parámetros>
        Header  Authorization: Bearer <EDS_KEY>
        Header  X-Graph-Host: video   (opcional, para subir videos a graph-video.facebook.com)

  Secretos en Cloudflare Pages (Settings → Variables and secrets):
    META_TOKEN  token del usuario del sistema edstattoo
    EDS_KEY     llave para usar este acceso (se cambia ahí para cortar el acceso)

  Freno (regla de Eduardo): nada que borre o pause sin su OK.
    - Bloqueado: método DELETE.
    - Bloqueado: cambiar el status de algo que ya existe (POST a /vXX/<id>) a PAUSED, ARCHIVED o DELETED.
      Crear cosas nuevas en pausa (POST a /act_.../campaigns, /adsets, /ads) sí se puede.
  Todo lo demás pasa (leer, crear, editar, subir, publicar, responder).
*/

const HOSTS = { graph: "https://graph.facebook.com", video: "https://graph-video.facebook.com" };
const BLOCKED_STATUS = /^(PAUSED|ARCHIVED|DELETED)$/i;

function json(status, obj) {
  return new Response(JSON.stringify(obj), {
    status,
    headers: { "content-type": "application/json; charset=utf-8", "cache-control": "no-store", "x-robots-tag": "noindex" }
  });
}

function sameKey(a, b) {
  if (!a || !b || a.length !== b.length) return false;
  let r = 0;
  for (let i = 0; i < a.length; i++) r |= a.charCodeAt(i) ^ b.charCodeAt(i);
  return r === 0;
}

function blockedStatus(get) {
  for (const k of ["status", "effective_status", "configured_status"]) {
    const v = get(k);
    if (v != null && BLOCKED_STATUS.test(String(v).replace(/["\[\]\s]/g, ""))) return true;
  }
  return false;
}

export async function onRequest({ request, env, params }) {
  if (!env.META_TOKEN || !env.EDS_KEY) return json(503, { error: "Falta META_TOKEN o EDS_KEY en Cloudflare" });

  const auth = request.headers.get("authorization") || "";
  const key = auth.startsWith("Bearer ") ? auth.slice(7).trim() : "";
  if (!sameKey(key, env.EDS_KEY)) return json(401, { error: "No autorizado" });

  const path = (params.path || []).join("/");
  if (!/^v\d+\.\d+\/[\w.\/-]+$/.test(path)) return json(400, { error: "Ruta inválida: /api/meta/vXX.X/<ruta de Graph>" });

  const method = request.method.toUpperCase();
  if (method === "DELETE") return json(403, { error: "Freno: borrar necesita el OK de Eduardo" });
  if (!["GET", "POST"].includes(method)) return json(405, { error: "Solo GET y POST" });

  // Solo frena cambios sobre algo existente; crear en pausa es lo seguro y se permite.
  const isUpdate = /^v\d+\.\d+\/\d+\/?$/.test(path);
  const inUrl = new URL(request.url);
  const host = HOSTS[(request.headers.get("x-graph-host") || "graph").toLowerCase()] || HOSTS.graph;
  const target = new URL(host + "/" + path);
  inUrl.searchParams.forEach((v, k) => { if (k !== "access_token") target.searchParams.append(k, v); });
  if (isUpdate && blockedStatus((k) => target.searchParams.get(k))) return json(403, { error: "Freno: pausar, archivar o borrar necesita el OK de Eduardo" });

  const init = { method, headers: {} };
  if (method === "POST") {
    const ct = request.headers.get("content-type") || "";
    if (ct.includes("multipart/form-data")) {
      const fd = await request.formData();
      if (isUpdate && blockedStatus((k) => fd.get(k))) return json(403, { error: "Freno: pausar, archivar o borrar necesita el OK de Eduardo" });
      fd.delete("access_token");
      fd.append("access_token", env.META_TOKEN);
      init.body = fd;
    } else if (ct.includes("application/json")) {
      const body = await request.json().catch(() => null);
      if (!body || typeof body !== "object") return json(400, { error: "JSON inválido" });
      if (isUpdate && blockedStatus((k) => body[k])) return json(403, { error: "Freno: pausar, archivar o borrar necesita el OK de Eduardo" });
      delete body.access_token;
      body.access_token = env.META_TOKEN;
      init.headers["content-type"] = "application/json";
      init.body = JSON.stringify(body);
    } else {
      const form = new URLSearchParams(await request.text());
      if (isUpdate && blockedStatus((k) => form.get(k))) return json(403, { error: "Freno: pausar, archivar o borrar necesita el OK de Eduardo" });
      form.delete("access_token");
      form.append("access_token", env.META_TOKEN);
      init.headers["content-type"] = "application/x-www-form-urlencoded";
      init.body = form.toString();
    }
  } else {
    target.searchParams.set("access_token", env.META_TOKEN);
  }

  const res = await fetch(target.toString(), init);
  // Los enlaces de paginación de Meta traen el token: se borra antes de devolver.
  const text = (await res.text()).split(env.META_TOKEN).join("REDACTED").split(encodeURIComponent(env.META_TOKEN)).join("REDACTED");
  return new Response(text, {
    status: res.status,
    headers: { "content-type": res.headers.get("content-type") || "application/json", "cache-control": "no-store", "x-robots-tag": "noindex" }
  });
}
