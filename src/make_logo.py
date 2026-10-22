#!/usr/bin/env python3
"""Logo de EDS Tattoo Studio (opción 2, elegida el 22/10/2026) y todos sus formatos.

"EDS" en Bodoni Moda, una línea fina debajo y "TATTOO STUDIO" en Josefin Sans, en una sola tinta.
Las letras están convertidas a trazos: los archivos se ven igual en cualquier lado, sin la letra instalada.

Uso:  python3 src/make_logo.py
Deja:  marca/EDS-Tattoo-Studio-logo/  (kit completo + LEEME.txt) y marca/EDS-Tattoo-Studio-logo.zip
       src/brand/ y src/logo-horizontal.svg  (lo que usa la página)
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
FONTS = os.path.join(SRC, "fonts")
BODONI = os.path.join(FONTS, "bodoni-moda-latin-500-normal.woff2")
BODONI_BOLD = os.path.join(FONTS, "bodoni-moda-latin-700-normal.woff2")
JOSEFIN = os.path.join(FONTS, "josefin-sans-latin-400-normal.woff2")

INK = "#000000"
WHITE = "#FFFFFF"
PAPER = "#FCFCFE"


def text_paths(text, font_file, size, x0, baseline, tracking=0.0):
    """Convierte un texto a trazos SVG con las curvas reales de la letra. Devuelve (trazos, ancho)."""
    font = TTFont(font_file)
    gs = font.getGlyphSet()
    cmap = font.getBestCmap()
    scale = size / font["head"].unitsPerEm
    x = 0.0
    out = []
    for ch in text:
        glyph = gs[cmap[ord(ch)]]
        pen = SVGPathPen(gs)
        glyph.draw(TransformPen(pen, (scale, 0, 0, -scale, x0 + x, baseline)))
        if pen.getCommands():
            out.append(pen.getCommands())
        x += glyph.width * scale + tracking
    return " ".join(out), x - tracking


def cap_height(font_file, size):
    f = TTFont(font_file)
    return f["OS/2"].sCapHeight / f["head"].unitsPerEm * size


def stacked(color, tagline=True):
    eds, w1 = text_paths("EDS", BODONI, 100, 0, 100, tracking=7)
    parts = [f'<path d="{eds}" fill="{color}"/>', f'<rect x="0" y="120" width="{w1:.2f}" height="1.3" fill="{color}"/>']
    if tagline:
        ts = 14.5
        _, w2 = text_paths("TATTOO STUDIO", JOSEFIN, ts, 0, 0, tracking=ts * 0.34)
        tag, _ = text_paths("TATTOO STUDIO", JOSEFIN, ts, (w1 - w2) / 2, 129 + cap_height(JOSEFIN, ts), tracking=ts * 0.34)
        parts.append(f'<path d="{tag}" fill="{color}"/>')
    return "".join(parts)


def horizontal(color):
    eds, w1 = text_paths("EDS", BODONI, 100, 0, 100, tracking=7)
    cap = cap_height(BODONI, 100)
    ts = 24
    tcap = cap_height(JOSEFIN, ts)
    gap = 14
    top = 100 - cap / 2 - (tcap * 2 + gap) / 2
    x = w1 + 24
    l1, _ = text_paths("TATTOO", JOSEFIN, ts, x + 24, top + tcap, tracking=ts * 0.3)
    l2, _ = text_paths("STUDIO", JOSEFIN, ts, x + 24, top + tcap * 2 + gap, tracking=ts * 0.3)
    return (f'<path d="{eds}" fill="{color}"/>'
            f'<rect x="{x:.2f}" y="{100 - cap:.2f}" width="1.3" height="{cap:.2f}" fill="{color}"/>'
            f'<path d="{l1} {l2}" fill="{color}"/>')


def letter_e(bg, fg, square=False, size=30):
    e, w = text_paths("E", BODONI_BOLD, size, 0, 0)
    cap = cap_height(BODONI_BOLD, size)
    shape = f'<rect width="48" height="48" fill="{bg}"/>' if square else f'<circle cx="24" cy="24" r="24" fill="{bg}"/>'
    return shape + f'<g transform="translate({24 - w / 2:.2f} {24 + cap / 2:.2f})"><path d="{e}" fill="{fg}"/></g>'


VARIANTS = {"negro": INK, "blanco": WHITE}


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
            page.set_content(f'<svg xmlns="http://www.w3.org/2000/svg" width="2000" height="2000" viewBox="-200 -200 800 800"><g id="g">{inner}</g></svg>')
            x, y, w, h = page.evaluate("() => { const r = document.getElementById('g').getBBox(); return [r.x, r.y, r.width, r.height]; }")
            vb = "%.2f %.2f %.2f %.2f" % (x - pad, y - pad, w + 2 * pad, h + 2 * pad)
            return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb}" role="img" aria-label="EDS Tattoo Studio">'
                    f'<title>EDS Tattoo Studio</title>{inner}</svg>\n')

        def ratio(svg):
            vb = svg.split('viewBox="')[1].split('"')[0].split()
            return float(vb[2]) / float(vb[3])

        def png(svg, width, height=None):
            height = height or round(width / ratio(svg))
            sized = svg.replace("<svg ", '<svg width="%d" height="%d" ' % (width, height), 1)
            pg = b.new_page(viewport={"width": width, "height": height})
            pg.set_content(f'<html><body style="margin:0;background:transparent">{sized}</body></html>')
            shot = pg.screenshot(type="png", omit_background=True, clip={"x": 0, "y": 0, "width": width, "height": height})
            pg.close()
            return Image.open(io.BytesIO(shot))

        def pdf(svg, path, width_mm):
            h_mm = width_mm / ratio(svg)
            sized = svg.replace("<svg ", '<svg width="%.2fmm" height="%.2fmm" ' % (width_mm, h_mm), 1)
            pg = b.new_page()
            pg.set_content(f'<html><body style="margin:0">{sized}</body></html>')
            pg.pdf(path=path, width="%.2fmm" % width_mm, height="%.2fmm" % h_mm, print_background=True,
                   margin={"top": "0", "right": "0", "bottom": "0", "left": "0"})
            pg.close()

        def shot_html(doc, w, h):
            tmp = os.path.join(KIT, "_tmp.html")
            with open(tmp, "w", encoding="utf-8") as f:
                f.write(doc)
            pg = b.new_page(viewport={"width": w, "height": h})
            pg.goto("file://" + tmp, wait_until="load")
            pg.evaluate("document.fonts.ready")
            pg.wait_for_timeout(300)
            data = pg.screenshot(type="png", clip={"x": 0, "y": 0, "width": w, "height": h})
            pg.close()
            os.remove(tmp)
            return Image.open(io.BytesIO(data)).convert("RGB")

        def save_svg(name, svg):
            with open(os.path.join(KIT, "vector", name + ".svg"), "w", encoding="utf-8") as f:
                f.write(svg)

        # ----- logo en sus tres armados y dos tintas -----
        svgs = {}
        for tinta, color in VARIANTS.items():
            for layout, inner, pad in [("apilado", stacked(color), 10), ("horizontal", horizontal(color), 8),
                                       ("monograma", stacked(color, tagline=False), 8)]:
                name = "eds-logo-%s-%s" % (layout, tinta)
                svgs[name] = fit(inner, pad)
                save_svg(name, svgs[name])
                for w in (1024, 2048):
                    png(svgs[name], w).save(os.path.join(KIT, "png", "%s-%dpx.png" % (name, w)), optimize=True)
        pdf(svgs["eds-logo-apilado-negro"], os.path.join(KIT, "imprenta", "eds-logo-apilado-negro.pdf"), 80)
        pdf(svgs["eds-logo-horizontal-negro"], os.path.join(KIT, "imprenta", "eds-logo-horizontal-negro.pdf"), 120)
        pdf(svgs["eds-logo-monograma-negro"], os.path.join(KIT, "imprenta", "eds-logo-monograma-negro.pdf"), 60)

        iso = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48" role="img" aria-label="EDS Tattoo Studio">{letter_e(INK, WHITE)}</svg>\n'
        iso_sq = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48">{letter_e(INK, WHITE, square=True, size=28)}</svg>\n'
        save_svg("eds-isotipo-e", iso)
        png(iso, 1024, 1024).save(os.path.join(KIT, "png", "eds-isotipo-e-1024px.png"), optimize=True)

        # ----- foto de perfil: fondo negro y "EDS" con su línea, apto para recorte en círculo -----
        mono = svgs["eds-logo-monograma-blanco"]
        x, y, w, h = [float(v) for v in mono.split('viewBox="')[1].split('"')[0].split()]
        side = w / 0.62
        cx, cy = x + w / 2, y + h / 2
        inner = mono.split("</title>", 1)[1].rsplit("</svg>", 1)[0]
        ox, oy = cx - side / 2, cy - side / 2
        profile = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{ox:.2f} {oy:.2f} {side:.2f} {side:.2f}" role="img" aria-label="EDS Tattoo Studio">'
                   f'<rect x="{ox:.2f}" y="{oy:.2f}" width="{side:.2f}" height="{side:.2f}" fill="{INK}"/>{inner}</svg>\n')
        save_svg("eds-perfil-cuadrado", profile)

        # ----- web (favicon en múltiplos de 48 px, como pide Google) -----
        web = os.path.join(KIT, "web")
        with open(os.path.join(web, "favicon.svg"), "w", encoding="utf-8") as f:
            f.write(iso)
        png(iso, 48, 48).save(os.path.join(web, "favicon.ico"), sizes=[(48, 48), (32, 32), (16, 16)])
        png(iso, 96, 96).save(os.path.join(web, "favicon-96.png"), optimize=True)
        png(iso_sq, 180, 180).save(os.path.join(web, "apple-touch-icon.png"), optimize=True)
        png(iso_sq, 192, 192).save(os.path.join(web, "icon-192.png"), optimize=True)
        png(iso_sq, 512, 512).save(os.path.join(web, "icon-512.png"), optimize=True)
        png(profile, 512, 512).convert("RGB").save(os.path.join(web, "logo-512.png"), optimize=True)

        # ----- redes y Google -----
        redes = os.path.join(KIT, "redes")
        png(profile, 720, 720).convert("RGB").save(os.path.join(redes, "google-perfil-logo-720.png"), optimize=True)
        png(profile, 1080, 1080).convert("RGB").save(os.path.join(redes, "instagram-facebook-perfil-1080.png"), optimize=True)
        png(profile, 640, 640).convert("RGB").save(os.path.join(redes, "whatsapp-perfil-640.png"), optimize=True)

        hero = os.path.join(SRC, "img", "sol-omoplato.webp")
        logo = svgs["eds-logo-apilado-negro"]

        def cover(w, h, logo_w):
            return f"""<!doctype html><html><head><meta charset="utf-8"><style>
@font-face{{font-family:F;font-weight:400;src:url("file://{FONTS}/montserrat-latin-400-normal.woff2")}}
@font-face{{font-family:F;font-weight:600;src:url("file://{FONTS}/montserrat-latin-600-normal.woff2")}}
html,body{{margin:0;width:{w}px;height:{h}px;background:{PAPER};overflow:hidden}}
.wrap{{display:grid;grid-template-columns:{w // 2}px {w - w // 2}px;height:{h}px}}
.photo{{background:url("file://{hero}") center 60%/cover no-repeat}}
.text{{display:grid;align-content:center;justify-items:center;gap:{round(h * 0.055)}px;padding:0 {round(w * 0.05)}px;text-align:center}}
.text svg{{width:{logo_w}px;height:auto}}
p{{margin:0;font:400 {round(h * 0.045)}px/1.35 F,sans-serif;color:#5E5B6B}}
b{{font:600 {round(h * 0.038)}px/1.3 F,sans-serif;color:#000}}
</style></head><body><div class="wrap"><div class="photo"></div><div class="text">
{logo}<p>Fine line · Buenos Aires</p><b>San Martín 569, Microcentro</b>
</div></div></body></html>"""

        shot_html(cover(1920, 1080, 600), 1920, 1080).save(os.path.join(redes, "google-portada-1920x1080.jpg"), quality=88, optimize=True, progressive=True)
        shot_html(cover(1200, 630, 360), 1200, 630).save(os.path.join(web, "og-1200x630.jpg"), quality=86, optimize=True, progressive=True)
        b.close()

    # ----- lo que usa la página -----
    for n in ["favicon.svg", "favicon.ico", "favicon-96.png", "apple-touch-icon.png", "icon-192.png", "icon-512.png", "logo-512.png"]:
        shutil.copyfile(os.path.join(KIT, "web", n), os.path.join(SITE_BRAND, n))
    shutil.copyfile(os.path.join(KIT, "web", "og-1200x630.jpg"), os.path.join(SITE_BRAND, "og.jpg"))
    shutil.copyfile(os.path.join(KIT, "vector", "eds-logo-horizontal-negro.svg"), os.path.join(SRC, "logo-horizontal.svg"))
    for old in ["logo-horizontal-oscuro.svg"]:
        if os.path.exists(os.path.join(SRC, old)):
            os.remove(os.path.join(SRC, old))

    with open(os.path.join(KIT, "LEEME.txt"), "w", encoding="utf-8") as f:
        f.write(LEEME)
    for n in ["OFL-BodoniModa.txt", "OFL-JosefinSans.txt"]:
        shutil.copyfile(os.path.join(FONTS, n), os.path.join(KIT, n))

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
- Imprenta (cartel, tarjetas, stickers, sello): imprenta/*.pdf o vector/*.svg. Son vectores: se agrandan sin perder calidad.
- Cualquier otro uso: png/ (fondo transparente, 1024 y 2048 px de ancho).

ARMADOS
- apilado: "EDS", la línea y "TATTOO STUDIO" abajo. Es el principal.
- horizontal: "EDS" y "TATTOO STUDIO" al costado, para espacios bajos y anchos (encabezado de la página, carteles largos).
- monograma: "EDS" con la línea, sin texto chico, para tamaños donde "TATTOO STUDIO" no se leería.
- isotipo-e: la "E" sola en círculo, para tamaños muy chicos (favicon).

TINTAS
- negro: sobre fondos claros. blanco: sobre fondos oscuros o fotos.
- Color: solo negro #000000 (o blanco #FFFFFF). Una sola tinta: sirve para vinilo, sello, grabado y bordado.

LETRAS
- "EDS": Bodoni Moda. "TATTOO STUDIO": Josefin Sans. Las dos con licencia libre SIL OFL (textos de licencia incluidos)
  y ya convertidas a trazos en los archivos.
"""

if __name__ == "__main__":
    main()
