/*
  Portada: edstattoostudio.com/ lleva directo a /es/, igual para todos (no se adivina el idioma).
  Se hace acá y no en _redirects para conservar seguro lo que viene después del "?"
  (el gclid de Google Ads: sin eso no se puede atribuir la consulta al anuncio).
*/
export function onRequest({ request }) {
  const url = new URL(request.url);
  return new Response(null, {
    status: 301,
    headers: { location: "/es/" + url.search, "cache-control": "public, max-age=3600" }
  });
}
