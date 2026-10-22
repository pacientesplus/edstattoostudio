# edstattoostudio.com

Página de EDS Tattoo Studio (San Martín 569, Microcentro, Buenos Aires) en castellano, portugués, inglés y alemán.

## Cómo está armada

- `src/` es lo que se edita: textos y fotos en `src/build.py`, estilos en `src/site.css`, comportamiento en `src/site.js`.
- `public/` es lo que se publica. Se genera con `python3 src/build.py` y no se edita a mano.
- Cloudflare Pages publica la carpeta `public/` tal cual, sin paso de compilación.

## Reglas que cumple (Google y estándares)

- Una dirección por idioma (`/es/`, `/pt/`, `/en/`, `/de/`) con el texto en el HTML, `hreflang` entre todas y la portada `/` como `x-default`. No se redirige por idioma del navegador.
- Título, descripción, canonical, Open Graph y datos estructurados (`TattooParlor`, `WebSite`) en cada página.
- `sitemap.xml` con las alternativas por idioma, `robots.txt`, página 404 sin indexar.
- Favicon en múltiplos de 48 px, ícono para celular e imagen para compartir (`src/make_brand.py`).
- Letras propias (sin depender de otros servidores), fotos WebP sin datos de ubicación, nombres con huella para caché larga.
- Encabezados de seguridad y caché en `_headers`.
- Política de privacidad en los cuatro idiomas (Ley 25.326 y requisitos de Google Ads para conversiones avanzadas).

## Lo que falta prender (en `src/site.js`, objeto `CONFIG`)

- `googleAdsId`, `visitorConversionLabel` y `localConversionLabel`: etiqueta de Google Ads y las dos conversiones ("Consulta visitante" y "Consulta local"). Es visitante si marcó "Estoy de visita" o si su WhatsApp no es +54. Cada una lleva su valor (`visitorValue`, `localValue`) para que Google priorice al visitante.
- `leadEndpoint`: dónde se guarda cada consulta (código, clic de Google, WhatsApp) para después subir a Google quién se tatuó y cuánto pagó.
- `googleMapsKey` y `placeId`: reseñas reales de Google en vivo.

## Cambiar fotos o textos

1. Poner la foto en `src/img/` (WebP, sin datos de ubicación) y sumarla a `WORKS` en `src/build.py`.
2. `python3 src/build.py`
3. Subir el cambio al repositorio; Cloudflare publica solo.

## Acceso privado a Meta (`functions/api/meta/`)

- `/api/meta/vXX.X/<ruta de Graph>` con `Authorization: Bearer <EDS_KEY>`. Usa por adentro el token del usuario del sistema `edstattoo` (portfolio eduardoink, app "eds tattoo studio"). Solo del estudio: nada de odontología.
- Secretos en Cloudflare Pages → Settings → Variables and secrets: `META_TOKEN` y `EDS_KEY`. Para cortar el acceso, cambiar `EDS_KEY`.
- Freno en el código: bloquea `DELETE` y cambiar el estado a pausado, archivado o borrado. Eso lo hace Eduardo o se hace con su OK.
- El token nunca vuelve en las respuestas (se borra de los enlaces de paginación).
