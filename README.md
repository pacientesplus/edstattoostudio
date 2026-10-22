# edstattoostudio.com

Página de EDS Tattoo Studio (San Martín 569, Microcentro, Buenos Aires) en castellano, portugués, inglés y alemán.

## Cómo está armada

- `src/` es lo que se edita: textos y fotos en `src/build.py`, estilos en `src/site.css`, comportamiento en `src/site.js`.
- `public/` es lo que se publica. Se genera con `python3 src/build.py` y no se edita a mano.
- Cloudflare Pages publica la carpeta `public/` tal cual, sin paso de compilación.

## Reglas que cumple (Google y estándares)

- Una dirección por idioma (`/es/`, `/pt/`, `/en/`, `/de/`) con el texto en el HTML y `hreflang` entre todas. La portada `/` redirige con 301 a `/es/` igual para todos (`functions/index.js`, conserva el `?gclid=`), y `x-default` apunta a `/es/`. No se adivina el idioma por el navegador. Arriba de cada página, la barra de idiomas con los nombres completos: Español · English · Português · Deutsch.
- Título, descripción, canonical, Open Graph y datos estructurados (`TattooParlor`, `WebSite`) en cada página.
- `sitemap.xml` con las alternativas por idioma, `robots.txt`, página 404 sin indexar.
- Favicon en múltiplos de 48 px, ícono para celular e imagen para compartir (`src/make_brand.py`).
- Letras propias (sin depender de otros servidores), fotos WebP sin datos de ubicación, nombres con huella para caché larga.
- Encabezados de seguridad y caché en `_headers`.
- Política de privacidad en los cuatro idiomas (Ley 25.326 y requisitos de Google Ads para conversiones avanzadas).

## Lo que falta prender (en `src/site.js`, objeto `CONFIG`)

- `googleAdsId`, `visitorConversionLabel` y `localConversionLabel`: etiqueta de Google Ads y las dos conversiones ("Consulta visitante" y "Consulta local"). Es visitante si marcó "Estoy de visita" o si su WhatsApp no es +54. Cada una lleva su valor (`visitorValue`, `localValue`) para que Google priorice al visitante.
- `googleMapsKey` y `placeId`: reseñas reales de Google en vivo.

## Registro de consultas (`functions/api/consulta.js`)

Cada vez que alguien completa el formulario, antes de abrir WhatsApp la página manda la consulta a `/api/consulta`. Se guarda con su código (`EDS-XXXXX`), el WhatsApp, la idea, el tamaño y el clic de Google (gclid, gbraid o wbraid), y llega un correo al momento con un botón para escribirle. Así no se pierde aunque la persona no toque "enviar" en su WhatsApp.

Para prenderlo, en Cloudflare Pages (proyecto del estudio):
1. **Base:** Storage & Databases → D1 → Create → nombre `eds-consultas`. Después, en el proyecto de Pages → Settings → Bindings → Add → D1 database: nombre de variable `DB`, base `eds-consultas`. La tabla se crea sola con la primera consulta.
2. **Correo:** crear cuenta en resend.com con el correo donde querés recibir los avisos, y crear una API key. En Pages → Settings → Variables and secrets: `RESEND_KEY` (tipo secreto) con esa clave y `AVISO_A` con tu correo. Mientras no se verifique el dominio en Resend, el aviso sale de `onboarding@resend.dev` y solo puede llegar al correo de la cuenta de Resend (alcanza, porque el aviso es para vos). Si más adelante se verifica `edstattoostudio.com` en Resend, poner `AVISO_DE` = `EDS consultas <consultas@edstattoostudio.com>`.
3. Volver a publicar (Deployments → Retry deployment) para que tome los cambios.

Ver lo guardado: `GET /api/consultas` (JSON) o `/api/consultas?formato=csv`, con `Authorization: Bearer <EDS_KEY>`.
Freno contra abuso: solo acepta envíos desde la web, valida código y teléfono, y más de 5 consultas por IP en 10 minutos no se guardan ni avisan.

## Cambiar fotos o textos

1. Poner la foto en `src/img/` (WebP, sin datos de ubicación) y sumarla a `WORKS` en `src/build.py`.
2. `python3 src/build.py`
3. Subir el cambio al repositorio; Cloudflare publica solo.

## Acceso privado a Meta (`functions/api/meta/`)

- `/api/meta/vXX.X/<ruta de Graph>` con `Authorization: Bearer <EDS_KEY>`. Usa por adentro el token del usuario del sistema `edstattoo` (portfolio eduardoink, app "eds tattoo studio"). Solo del estudio: nada de odontología.
- Secretos en Cloudflare Pages → Settings → Variables and secrets: `META_TOKEN` y `EDS_KEY`. Para cortar el acceso, cambiar `EDS_KEY`.
- Freno en el código: bloquea `DELETE` y cambiar el estado a pausado, archivado o borrado. Eso lo hace Eduardo o se hace con su OK.
- El token nunca vuelve en las respuestas (se borra de los enlaces de paginación).
