#!/usr/bin/env python3
"""Genera los íconos (favicon en múltiplos de 48 px, como pide Google) y la imagen para compartir (1200x630).
Uso: python3 src/make_brand.py  -> deja todo en src/brand/
Si llega el logo oficial del estudio, se reemplaza FAVICON_SVG por el logo y se vuelve a correr."""
import io
import os
from PIL import Image
from playwright.sync_api import sync_playwright

SRC = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(SRC, "brand")
os.makedirs(OUT, exist_ok=True)

# Una "e" de una sola línea, como un trazo de aguja, blanca sobre círculo de tinta.
FAVICON_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48">
<circle cx="24" cy="24" r="24" fill="#000"/>
<path d="M14 24H34A10 10 0 1 0 31.07 31.07" fill="none" stroke="#fff" stroke-width="3.2" stroke-linecap="round" stroke-linejoin="round"/>
</svg>
"""
# Versión para íconos de pantalla de inicio: fondo cuadrado (los sistemas recortan a su forma).
TILE_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48">
<rect width="48" height="48" fill="#000"/>
<path d="M14 24H34A10 10 0 1 0 31.07 31.07" fill="none" stroke="#fff" stroke-width="3.2" stroke-linecap="round" stroke-linejoin="round"/>
</svg>
"""

with open(os.path.join(OUT, "favicon.svg"), "w", encoding="utf-8") as f:
    f.write(FAVICON_SVG)

fonts = os.path.join(SRC, "fonts")
hero = os.path.join(SRC, "img", "sol-omoplato.webp")
OG_HTML = f"""<!doctype html><html><head><meta charset="utf-8"><style>
@font-face{{font-family:J;font-weight:300;src:url("file://{fonts}/josefin-sans-latin-300-normal.woff2")}}
@font-face{{font-family:F;font-weight:400;src:url("file://{fonts}/figtree-latin-400-normal.woff2")}}
@font-face{{font-family:F;font-weight:600;src:url("file://{fonts}/figtree-latin-600-normal.woff2")}}
html,body{{margin:0;width:1200px;height:630px;background:#FCFCFE;overflow:hidden}}
.wrap{{display:grid;grid-template-columns:600px 600px;height:630px}}
.photo{{background:url("file://{hero}") center 60%/cover no-repeat}}
.text{{display:grid;align-content:center;gap:22px;padding:0 64px}}
h1{{margin:0;font:300 76px/1.02 J,sans-serif;color:#000;letter-spacing:-1px}}
p{{margin:0;font:400 30px/1.3 F,sans-serif;color:#5E5B6B}}
b{{font:600 26px/1.3 F,sans-serif;color:#000}}
svg{{width:380px;height:26px;overflow:visible}}
</style></head><body><div class="wrap"><div class="photo"></div><div class="text">
<h1>EDS Tattoo Studio</h1>
<svg viewBox="0 0 400 28" preserveAspectRatio="none"><path d="M2 18 C 70 4, 120 26, 190 15 S 300 4, 340 12 S 385 20, 398 9" fill="none" stroke="#5B3FB3" stroke-width="3" stroke-linecap="round"/></svg>
<p>Fine line tattoos<br>Buenos Aires</p>
<b>San Martín 569, Microcentro</b>
</div></div></body></html>"""

with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": 1200, "height": 630})
    tmp = os.path.join(OUT, "_og.html")   # desde un archivo, para que carguen la foto y las letras locales
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(OG_HTML)
    pg.goto("file://" + tmp, wait_until="load")
    pg.evaluate("document.fonts.ready")
    pg.wait_for_timeout(400)
    os.remove(tmp)
    Image.open(io.BytesIO(pg.screenshot(type="png"))).convert("RGB").save(os.path.join(OUT, "og.jpg"), quality=86, optimize=True, progressive=True)

    def raster(svg, size):
        sized = svg.replace("<svg ", '<svg width="%d" height="%d" ' % (size, size), 1)
        page = b.new_page(viewport={"width": size, "height": size})
        page.set_content('<html><body style="margin:0;background:transparent">' + sized + "</body></html>")
        png = page.screenshot(type="png", omit_background=True, clip={"x": 0, "y": 0, "width": size, "height": size})
        page.close()
        return Image.open(io.BytesIO(png)).convert("RGBA")

    fav48 = raster(FAVICON_SVG, 48)
    fav96 = raster(FAVICON_SVG, 96)
    fav96.save(os.path.join(OUT, "favicon-96.png"))
    fav48.save(os.path.join(OUT, "favicon.ico"), sizes=[(48, 48), (32, 32), (16, 16)])
    raster(TILE_SVG, 180).save(os.path.join(OUT, "apple-touch-icon.png"))
    raster(TILE_SVG, 192).save(os.path.join(OUT, "icon-192.png"))
    raster(TILE_SVG, 512).save(os.path.join(OUT, "icon-512.png"))
    b.close()

for n in sorted(os.listdir(OUT)):
    print(n, os.path.getsize(os.path.join(OUT, n)), "bytes")
