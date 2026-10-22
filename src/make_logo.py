#!/usr/bin/env python3
"""Logo de EDS Tattoo Studio y todos sus formatos.

El logo: "eds" en minúscula, dibujado como trazo de aguja de grosor parejo (monolínea), con la línea fina
violeta del esténcil debajo y "tattoo studio" en Josefin Sans convertida a trazos (no depende de la letra instalada).

Uso:  python3 src/make_logo.py
Deja:  marca/EDS-Tattoo-Studio-logo/  (kit completo + LEEME.txt) y marca/EDS-Tattoo-Studio-logo.zip
       src/brand/                    (íconos e imagen para compartir que usa la página)
"""
import io
import os
import shutil
import zipfile

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont
from PIL import Image
from playwright.sync_api import sync_playwright

SRC = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(SRC)
KIT = os.path.join(PROJ, "marca", "EDS-Tattoo-Studio-logo")
SITE_BRAND = os.path.join(SRC, "brand")

INK = "#000000"
PAPER = "#FCFCFE"
STENCIL = "#5B3FB3"
STENCIL_LIGHT = "#A897F2"
WHITE = "#FFFFFF"

STROKE = 3.6  # grosor del trazo de las letras (x-height = 36)

# ---------- geometría del monograma "eds" (x-height de y=2 a y=38) ----------
E = "M2 20H38A18 18 0 1 0 32.73 32.73"
D = "M84 20A18 18 0 1 1 48 20A18 18 0 1 1 84 20M84 -24V38"
S = "M110.79 6.5A9 9 0 1 0 103 20A9 9 0 1 1 95.21 33.5"
# la línea de aguja del sitio, escalada al ancho del monograma
NEEDLE = "M0 51.5C19.6 47.6 33.6 53.8 53.2 50.7S84 47.6 95.2 49.9S107.8 52.1 111.4 48.9"


def text_paths(text, font_file, size, x0, baseline, tracking=0.0):
    """Convierte un texto a trazos SVG con las curvas reales de la letra."""
    font = TTFont(font_file)
    gs = font.getGlyphSet()
    cmap = font.getBestCmap()
    upem = font["head"].unitsPerEm
    scale = size / upem
    x = 0.0
    out = []
    for ch in text:
        gname = cmap[ord(ch)]
        glyph = gs[gname]
        pen = SVGPathPen(gs)
        glyph.draw(TransformPen(pen, (scale, 0, 0, -scale, x0 + x, baseline)))
        cmd = pen.getCommands()
        if cmd:
            out.append(cmd)
        x += glyph.width * scale + tracking
    return " ".join(out), x - tracking


FONT_LIGHT = os.path.join(SRC, "fonts", "josefin-sans-latin-300-normal.woff2")


def monogram(letters, needle, needle_w=1.3):
    return (f'<path d="{E} {D} {S}" fill="none" stroke="{letters}" stroke-width="{STROKE}" '
            f'stroke-linecap="round" stroke-linejoin="round"/>'
            f'<path d="{NEEDLE}" fill="none" stroke="{needle}" stroke-width="{needle_w}" stroke-linecap="round"/>')


def stacked(letters, needle, text):
    tp, _ = text_paths("tattoo studio", FONT_LIGHT, 17.2, 0.6, 74, tracking=0.55)
    return monogram(letters, needle) + f'<path d="{tp}" fill="{text}"/>'


def horizontal(letters, needle, text):
    tp, _ = text_paths("tattoo studio", FONT_LIGHT, 27, 128, 38, tracking=0.4)
    return monogram(letters, needle) + f'<path d="{tp}" fill="{text}"/>'


def isotype_e(bg, fg, square=False):
    shape = (f'<rect width="48" height="48" fill="{bg}"/>' if square else f'<circle cx="24" cy="24" r="24" fill="{bg}"/>')
    return (shape + f'<path d="M14 24H34A10 10 0 1 0 31.07 31.07" fill="none" stroke="{fg}" stroke-width="3.2" '
            f'stroke-linecap="round" stroke-linejoin="round"/>')


VARIANTS = {
    "color": (INK, STENCIL, INK),
    "negro": (INK, INK, INK),
    "blanco": (WHITE, WHITE, WHITE),
    "color-fondo-oscuro": (WHITE, STENCIL_LIGHT, WHITE),
}


def main():
    shutil.rmtree(KIT, ignore_errors=True)
    for sub in ["vector", "png", "web", "redes", "imprenta"]:
        os.makedirs(os.path.join(KIT, sub), exist_ok=True)
    os.makedirs(SITE_BRAND, exist_ok=True)

    with sync_playwright() as p:
        b = p.chromium.launch()
        page = b.new_page()

        def fit(inner, pad):
            """Mide el dibujo real y arma un SVG con su caja exacta más el margen."""
            page.set_content(f'<svg xmlns="http://www.w3.org/2000/svg" id="s" width="2000" height="2000" viewBox="-200 -200 600 600"><g id="g">{inner}</g></svg>')
            bb = page.evaluate("() => { const r = document.getElementById('g').getBBox(); return [r.x, r.y, r.width, r.height]; }")
            x, y, w, h = bb
            sw = STROKE / 2
            x, y, w, h = x - sw - pad, y - sw - pad, w + 2 * sw + 2 * pad, h + 2 * sw + 2 * pad
            vb = "%.2f %.2f %.2f %.2f" % (x, y, w, h)
            return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb}" role="img" aria-label="EDS Tattoo Studio"><title>EDS Tattoo Studio</title>{inner}</svg>\n', w / h

        def render_png(svg, width, height=None, bg=None):
            ratio = svg_ratio(svg)
            height = height or round(width / ratio)
            sized = svg.replace("<svg ", '<svg width="%d" height="%d" ' % (width, height), 1)
            pg = b.new_page(viewport={"width": width, "height": height})
            background = bg or "transparent"
            pg.set_content(f'<html><body style="margin:0;background:{background}">{sized}</body></html>')
            png = pg.screenshot(type="png", omit_background=bg is None, clip={"x": 0, "y": 0, "width": width, "height": height})
            pg.close()
            return Image.open(io.BytesIO(png))

        def render_html(html_doc, width, height):
            pg = b.new_page(viewport={"width": width, "height": height})
            tmp = os.path.join(KIT, "_tmp.html")
            with open(tmp, "w", encoding="utf-8") as f:
                f.write(html_doc)
            pg.goto("file://" + tmp, wait_until="load")
            pg.evaluate("document.fonts.ready")
            pg.wait_for_timeout(300)
            png = pg.screenshot(type="png", clip={"x": 0, "y": 0, "width": width, "height": height})
            pg.close()
            os.remove(tmp)
            return Image.open(io.BytesIO(png))

        def svg_ratio(svg):
            vb = svg.split('viewBox="')[1].split('"')[0].split()
            return float(vb[2]) / float(vb[3])

        def pdf(svg, path, width_mm=80):
            ratio = svg_ratio(svg)
            h_mm = width_mm / ratio
            sized = svg.replace("<svg ", '<svg width="%.2fmm" height="%.2fmm" ' % (width_mm, h_mm), 1)
            pg = b.new_page()
            pg.set_content(f'<html><body style="margin:0">{sized}</body></html>')
            pg.pdf(path=path, width="%.2fmm" % width_mm, height="%.2fmm" % h_mm, print_background=True,
                   margin={"top": "0", "right": "0", "bottom": "0", "left": "0"})
            pg.close()

        # ----- vectores y PNG del logo -----
        svgs = {}
        for name, (letters, needle, text) in VARIANTS.items():
            for layout, fn, pad in [("apilado", stacked, 6), ("horizontal", horizontal, 5)]:
                svg, _ = fit(fn(letters, needle, text), pad)
                key = "eds-logo-%s-%s" % (layout, name)
                svgs[key] = svg
                with open(os.path.join(KIT, "vector", key + ".svg"), "w", encoding="utf-8") as f:
                    f.write(svg)
                for w in (1024, 2048):
                    render_png(svg, w).save(os.path.join(KIT, "png", "%s-%dpx.png" % (key, w)), optimize=True)
            if name in ("color", "negro"):
                pdf(svgs["eds-logo-apilado-%s" % name], os.path.join(KIT, "imprenta", "eds-logo-apilado-%s.pdf" % name))
                pdf(svgs["eds-logo-horizontal-%s" % name], os.path.join(KIT, "imprenta", "eds-logo-horizontal-%s.pdf" % name), width_mm=120)

        iso = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48">{isotype_e(INK, WHITE)}</svg>\n'
        iso_sq = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48">{isotype_e(INK, WHITE, square=True)}</svg>\n'
        with open(os.path.join(KIT, "vector", "eds-isotipo-e.svg"), "w", encoding="utf-8") as f:
            f.write(iso)
        render_png(iso, 1024, 1024).save(os.path.join(KIT, "png", "eds-isotipo-e-1024px.png"), optimize=True)

        # ----- web (favicon en múltiplos de 48 px, como pide Google) -----
        web = os.path.join(KIT, "web")
        with open(os.path.join(web, "favicon.svg"), "w", encoding="utf-8") as f:
            f.write(iso)
        f48 = render_png(iso, 48, 48)
        f48.save(os.path.join(web, "favicon.ico"), sizes=[(48, 48), (32, 32), (16, 16)])
        render_png(iso, 96, 96).save(os.path.join(web, "favicon-96.png"), optimize=True)
        render_png(iso_sq, 180, 180).save(os.path.join(web, "apple-touch-icon.png"), optimize=True)
        render_png(iso_sq, 192, 192).save(os.path.join(web, "icon-192.png"), optimize=True)
        render_png(iso_sq, 512, 512).save(os.path.join(web, "icon-512.png"), optimize=True)

        # logo cuadrado para Google (datos estructurados) y perfiles: monograma centrado, apto para recorte en círculo
        mono_dark = fit(monogram(WHITE, STENCIL_LIGHT, 1.6), 0)[0]
        vb = [float(v) for v in mono_dark.split('viewBox="')[1].split('"')[0].split()]
        side = vb[2] / 0.66  # el monograma ocupa el 66% del ancho: entra completo en el recorte en círculo
        cx, cy = vb[0] + vb[2] / 2, vb[1] + vb[3] / 2
        square_vb = "%.2f %.2f %.2f %.2f" % (cx - side / 2, cy - side / 2, side, side)
        inner_mono = monogram(WHITE, STENCIL_LIGHT, 1.6)
        profile_svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{square_vb}" role="img" aria-label="EDS Tattoo Studio">'
                       f'<rect x="{cx - side / 2:.2f}" y="{cy - side / 2:.2f}" width="{side:.2f}" height="{side:.2f}" fill="{INK}"/>{inner_mono}</svg>\n')
        with open(os.path.join(KIT, "vector", "eds-perfil-cuadrado.svg"), "w", encoding="utf-8") as f:
            f.write(profile_svg)
        render_png(profile_svg, 512, 512).convert("RGB").save(os.path.join(web, "logo-512.png"), optimize=True)

        # ----- redes y Google -----
        redes = os.path.join(KIT, "redes")
        render_png(profile_svg, 720, 720).convert("RGB").save(os.path.join(redes, "google-perfil-logo-720.png"), optimize=True)
        render_png(profile_svg, 1080, 1080).convert("RGB").save(os.path.join(redes, "instagram-facebook-perfil-1080.png"), optimize=True)
        render_png(profile_svg, 640, 640).convert("RGB").save(os.path.join(redes, "whatsapp-perfil-640.png"), optimize=True)

        fonts = os.path.join(SRC, "fonts")
        hero = os.path.join(SRC, "img", "sol-omoplato.webp")
        logo_c = svgs["eds-logo-apilado-color"]

        def cover_html(w, h, logo_w):
            return f"""<!doctype html><html><head><meta charset="utf-8"><style>
@font-face{{font-family:F;font-weight:400;src:url("file://{fonts}/figtree-latin-400-normal.woff2")}}
@font-face{{font-family:F;font-weight:600;src:url("file://{fonts}/figtree-latin-600-normal.woff2")}}
html,body{{margin:0;width:{w}px;height:{h}px;background:{PAPER};overflow:hidden}}
.wrap{{display:grid;grid-template-columns:{w // 2}px {w - w // 2}px;height:{h}px}}
.photo{{background:url("file://{hero}") center 60%/cover no-repeat}}
.text{{display:grid;align-content:center;justify-items:start;gap:{round(h * 0.05)}px;padding:0 {round(w * 0.06)}px}}
.text svg{{width:{logo_w}px;height:auto}}
p{{margin:0;font:400 {round(h * 0.047)}px/1.35 F,sans-serif;color:#5E5B6B}}
b{{font:600 {round(h * 0.04)}px/1.3 F,sans-serif;color:#000}}
</style></head><body><div class="wrap"><div class="photo"></div><div class="text">
{logo_c}<p>Fine line · Buenos Aires</p><b>San Martín 569, Microcentro</b>
</div></div></body></html>"""

        render_html(cover_html(1920, 1080, 560), 1920, 1080).convert("RGB").save(
            os.path.join(redes, "google-portada-1920x1080.jpg"), quality=88, optimize=True, progressive=True)
        og = render_html(cover_html(1200, 630, 350), 1200, 630).convert("RGB")
        og.save(os.path.join(web, "og-1200x630.jpg"), quality=86, optimize=True, progressive=True)

        b.close()

    # ----- lo que usa la página -----
    for n in ["favicon.svg", "favicon.ico", "favicon-96.png", "apple-touch-icon.png", "icon-192.png", "icon-512.png", "logo-512.png"]:
        shutil.copyfile(os.path.join(KIT, "web", n), os.path.join(SITE_BRAND, n))
    shutil.copyfile(os.path.join(KIT, "web", "og-1200x630.jpg"), os.path.join(SITE_BRAND, "og.jpg"))
    shutil.copyfile(os.path.join(KIT, "vector", "eds-logo-horizontal-color.svg"), os.path.join(SRC, "logo-horizontal.svg"))
    shutil.copyfile(os.path.join(KIT, "vector", "eds-logo-horizontal-color-fondo-oscuro.svg"), os.path.join(SRC, "logo-horizontal-oscuro.svg"))

    with open(os.path.join(KIT, "LEEME.txt"), "w", encoding="utf-8") as f:
        f.write(LEEME)

    zpath = os.path.join(PROJ, "marca", "EDS-Tattoo-Studio-logo.zip")
    if os.path.exists(zpath):
        os.remove(zpath)
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
        for root, _, files in os.walk(KIT):
            for n in sorted(files):
                full = os.path.join(root, n)
                z.write(full, os.path.join("EDS-Tattoo-Studio-logo", os.path.relpath(full, KIT)))
    count = sum(len(fs) for _, _, fs in os.walk(KIT))
    print("kit:", KIT, "|", count, "archivos | zip:", round(os.path.getsize(zpath) / 1024), "KB")


LEEME = """EDS Tattoo Studio - logo y formatos

QUÉ USAR DÓNDE
- Página web: carpeta web/ (es lo que usa edstattoostudio.com).
  favicon.ico, favicon.svg y favicon-96.png: el ícono de la pestaña y de los resultados de Google (múltiplos de 48 px).
  apple-touch-icon.png (180), icon-192.png, icon-512.png: ícono al guardar la página en el celular.
  logo-512.png: el logo que se declara a Google en los datos del negocio.
  og-1200x630.jpg: la imagen que aparece al compartir el link por WhatsApp, Facebook, etc.
- Ficha de Google (Business Profile): redes/google-perfil-logo-720.png como logo (Google recomienda 720 x 720)
  y redes/google-portada-1920x1080.jpg como portada.
- Instagram y Facebook (foto de perfil): redes/instagram-facebook-perfil-1080.png.
- WhatsApp Business (foto de perfil): redes/whatsapp-perfil-640.png.
  Las fotos de perfil están pensadas para el recorte en círculo: el logo queda adentro.
- Imprenta (cartel, tarjetas, stickers): imprenta/*.pdf o vector/*.svg. Son vectores: se agrandan sin perder calidad.
- Cualquier otro uso: png/ (fondo transparente, 1024 y 2048 px de ancho).

VERSIONES
- color: letras negras y línea violeta, para fondos claros.
- color-fondo-oscuro: letras blancas y línea violeta clara, para fondos oscuros.
- negro / blanco: una sola tinta (sellos, grabados, vinilo de un color).
- apilado: "eds" arriba y "tattoo studio" abajo. horizontal: todo en una línea.
- isotipo-e: la "e" sola en círculo, para tamaños muy chicos.

COLORES
- Tinta: #000000
- Violeta esténcil: #5B3FB3 (sobre oscuro: #A897F2)
- Papel: #FCFCFE

LETRA
- "tattoo studio": Josefin Sans Light (licencia libre SIL OFL), ya convertida a trazos en los archivos.
- Textos de la página: Figtree.
"""

if __name__ == "__main__":
    main()
