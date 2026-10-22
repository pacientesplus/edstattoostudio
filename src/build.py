#!/usr/bin/env python3
"""Arma edstattoostudio.com en public/ (la carpeta que publica Cloudflare Pages).

Uso:  python3 src/build.py
Cada idioma tiene su propia dirección (/es/, /pt/, /en/, /de/) con el texto ya escrito en el HTML,
como pide Google para sitios en varios idiomas; la portada (/) elige idioma sin redirigir.
"""
import hashlib
import html
import json
import os
import shutil
from datetime import date

SRC = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(SRC)
OUT = os.path.join(PROJ, "public")

SITE = "https://edstattoostudio.com"
BRAND = "EDS Tattoo Studio"
PHONE_E164 = "+5491122510832"
PHONE_LABEL = "+54 9 11 2251-0832"
WA_URL = "https://wa.me/5491122510832"
STREET = "San Martín 569"
PLACE_ID = "ChIJSbT071_LvJURa8aGV8tGUIY"  # ficha de EDS Tattoo Studio en Google Maps
MAPS_DIRECTIONS = "https://www.google.com/maps/dir/?api=1&destination=EDS%20Tattoo%20Studio&destination_place_id=" + PLACE_ID
MAPS_REVIEWS = "https://www.google.com/maps/search/?api=1&query=EDS%20Tattoo%20Studio&query_place_id=" + PLACE_ID
TODAY = date.today().isoformat()

LANGS = ["es", "pt", "en", "de"]
HTML_LANG = {"es": "es-AR", "pt": "pt-BR", "en": "en", "de": "de"}
LOCALE = {"es": "es-AR", "pt": "pt-BR", "en": "en-US", "de": "de-DE"}
OG_LOCALE = {"es": "es_AR", "pt": "pt_BR", "en": "en_US", "de": "de_DE"}
API_LANG = {"es": "es", "pt": "pt-BR", "en": "en", "de": "de"}
PRIVACY_SLUG = {"es": "privacidad", "pt": "privacidade", "en": "privacy", "de": "datenschutz"}
LANG_NAME = {"es": "Español", "pt": "Português", "en": "English", "de": "Deutsch"}
LANG_LINE = {
    "es": "Tatuajes fine line en Buenos Aires",
    "pt": "Tatuagens fine line em Buenos Aires",
    "en": "Fine line tattoos in Buenos Aires",
    "de": "Fine-Line-Tattoos in Buenos Aires",
}
ALT_PREFIX = {"es": "Tatuaje: ", "pt": "Tatuagem: ", "en": "Tattoo: ", "de": "Tattoo: "}
HERO_SIZES = "(min-width: 900px) 540px, 100vw"
WEB_FONTS = ["montserrat-latin-400-normal.woff2", "montserrat-latin-500-normal.woff2", "montserrat-latin-600-normal.woff2",
             "OFL-Montserrat.txt"]


def header_logo():
    with open(os.path.join(SRC, "logo-horizontal.svg"), encoding="utf-8") as f:
        svg = f.read().strip()
    svg = (svg.replace('stroke="#000000"', 'stroke="currentColor"')
              .replace('fill="#000000"', 'fill="currentColor"')
              .replace('stroke="#5B3FB3"', 'style="stroke:var(--stencil)"'))
    return svg.replace("<svg ", '<svg class="logo" focusable="false" ', 1)


def hero_preload(assets):
    im = assets["img"][HERO["file"]]
    return (f'<link rel="preload" as="image" href="{im["url"]}" imagesrcset="{im["srcset"]}" '
            f'imagesizes="{HERO_SIZES}" fetchpriority="high">\n')

HERO = {"file": "sol-omoplato.webp", "pos": "50% 58%", "focus": "48% 56%",
        "cap": {"es": "Sol de Mayo, omóplato", "pt": "Sol argentino, omoplata", "en": "Argentine sun, shoulder blade", "de": "Argentinische Sonne, Schulterblatt"}}
WORKS = [
    {"file": "espalda-rama.webp", "pos": "50% 45%", "focus": "36% 32%", "cap": {"es": "Rama y frase, espalda", "pt": "Galho e frase, costas", "en": "Branch and script, back", "de": "Zweig und Schriftzug, Rücken"}},
    {"file": "corazon-linea.webp", "pos": "58% 52%", "focus": "60% 56%", "cap": {"es": "Corazón de una sola línea, antebrazo", "pt": "Coração de uma linha só, antebraço", "en": "Single-line heart, forearm", "de": "Herz aus einer einzigen Linie, Unterarm"}},
    {"file": "mariposas-sombra.webp", "pos": "50% 48%", "focus": "60% 42%", "cap": {"es": "Mariposas con sombra, antebrazo", "pt": "Borboletas com sombra, antebraço", "en": "Shaded butterflies, forearm", "de": "Schmetterlinge mit Schattierung, Unterarm"}},
    {"file": "sol-mano.webp", "pos": "50% 45%", "focus": "50% 48%", "cap": {"es": "Sol de Mayo, mano", "pt": "Sol argentino, mão", "en": "Argentine sun, hand", "de": "Argentinische Sonne, Hand"}},
    {"file": "ramo-color.webp", "pos": "50% 45%", "focus": "46% 48%", "cap": {"es": "Ramo de flores en color, brazo", "pt": "Buquê de flores colorido, braço", "en": "Color flower bouquet, arm", "de": "Farbiger Blumenstrauß, Arm"}},
    {"file": "frase-pierna.webp", "pos": "45% 50%", "focus": "44% 50%", "cap": {"es": "Frase, pierna", "pt": "Frase, perna", "en": "Script, leg", "de": "Schriftzug, Bein"}},
    {"file": "mariposa-violeta.webp", "pos": "50% 47%", "focus": "51% 46%", "cap": {"es": "Mariposa en violeta, antebrazo", "pt": "Borboleta lilás, antebraço", "en": "Purple butterfly, forearm", "de": "Lila Schmetterling, Unterarm"}},
    {"file": "ornamentos-dedos.webp", "pos": "50% 55%", "focus": "53% 52%", "cap": {"es": "Ornamentos, dedos", "pt": "Ornamentos, dedos", "en": "Ornaments, fingers", "de": "Ornamente, Finger"}},
    {"file": "nombre-corazon.webp", "pos": "50% 45%", "focus": "61% 56%", "cap": {"es": "Nombre con corazón, antebrazo", "pt": "Nome com coração, antebraço", "en": "Name with heart, forearm", "de": "Name mit Herz, Unterarm"}},
    {"file": "corazones-mano.webp", "pos": "50% 50%", "focus": "51% 49%", "cap": {"es": "Corazones, mano", "pt": "Corações, mão", "en": "Hearts, hand", "de": "Herzen, Hand"}},
    {"file": "nombres-cruz.webp", "pos": "55% 45%", "focus": "56% 48%", "cap": {"es": "Nombres con cruz, antebrazo", "pt": "Nomes com cruz, antebraço", "en": "Names with cross, forearm", "de": "Namen mit Kreuz, Unterarm"}},
    {"file": "nombre-rosa.webp", "pos": "50% 55%", "focus": "33% 58%", "cap": {"es": "Nombre y rosa en línea roja", "pt": "Nome e rosa em linha vermelha", "en": "Name and rose in red line", "de": "Name und Rose in roter Linie"}},
]

T = {
    "es": {
        "meta.title": "Tatuajes fine line en Buenos Aires | EDS Tattoo Studio",
        "meta.desc": "Tatuajes fine line en Microcentro, Buenos Aires. 5,0 en Google con más de 230 reseñas. Contame tu idea y te respondo por WhatsApp.",
        "og.alt": "Tatuaje fine line del Sol de Mayo en el omóplato",
        "skip": "Ir al formulario",
        "nav.lang": "Idioma",
        "hero.h1": "Tatuajes fine line en el centro de Buenos Aires",
        "hero.lead": "Soy Eduardo. Me especializo en línea fina y tatúo en mi estudio de San Martín 569, en Microcentro.",
        "hero.proof": "5,0 en Google, con más de 230 reseñas",
        "hero.proofLink": "Leer reseñas",
        "hero.cta": "Contame tu idea",
        "work.h2": "Trabajos",
        "work.lead": "En cada foto, el círculo muestra la línea de cerca.",
        "reviews.h2": "Reseñas",
        "reviews.lead": "5,0 de 5 en Google, con más de 230 reseñas.",
        "reviews.live": "{r} de 5 en Google, con {n} reseñas.",
        "reviews.order": "Google las ordena por relevancia.",
        "reviews.translated": "Traducida por Google",
        "reviews.onMaps": "Ver en Google Maps",
        "reviews.starsLabel": "{n} de 5 estrellas",
        "reviews.link": "Leer todas en Google",
        "steps.h2": "Cómo es",
        "steps.1": "Me contás tu idea en el formulario: qué te querés hacer, el tamaño y si vivís acá o estás de visita.",
        "steps.2": "Se abre WhatsApp con todo ya escrito. Lo mandás y, si tenés una foto de referencia, la sumás ahí.",
        "steps.3": "Te respondo por WhatsApp y vemos diseño, precio y día.",
        "form.h2": "Contame tu idea",
        "form.lead": "Son cuatro datos y se abre WhatsApp con tu mensaje listo.",
        "f.idea": "Corta descripción de lo que te querés hacer",
        "f.idea.ph": "Ej.: una rama de olivo con hojas chiquitas",
        "f.zone": "Zona del cuerpo",
        "f.size": "Tamaño aproximado",
        "f.stay": "¿Vivís en Buenos Aires o estás de visita?",
        "f.leave": "¿Qué día te vas?",
        "f.name": "Tu nombre",
        "f.phone": "Tu WhatsApp, con código de país",
        "f.phone.ph": "+54 9 11 1234 5678",
        "f.privacy": "Tu número se usa para responderte y, cifrado, para medir qué anuncios traen consultas.",
        "f.privacyLink": "Política de privacidad",
        "f.submit": "Mandar por WhatsApp",
        "f.submitNote": "Se abre WhatsApp con tu mensaje ya escrito.",
        "err.idea": "Contame qué te querés tatuar.",
        "err.zone": "Elegí una zona.",
        "err.size": "Elegí un tamaño.",
        "err.stay": "Decime si vivís acá o estás de visita.",
        "err.phone": "Poné tu WhatsApp con el código de país, por ejemplo +54 9 11 1234 5678.",
        "done.title": "Tu mensaje está listo",
        "done.text": "Si WhatsApp no se abrió, tocá el botón y mandalo desde ahí.",
        "done.code": "Código de tu consulta",
        "done.open": "Abrir WhatsApp",
        "done.copy": "Copiar mensaje",
        "done.copied": "Mensaje copiado",
        "place.h2": "Dónde estoy",
        "place.addr": "San Martín 569, Microcentro, Buenos Aires",
        "place.link": "Cómo llegar",
        "sticky": "Contame tu idea",
        "foot.privacy": "Privacidad",
        "msg.hello": "Hola Eduardo, te escribo desde la web.",
        "msg.idea": "Idea", "msg.zone": "Zona", "msg.size": "Tamaño",
        "msg.local": "Vivo en Buenos Aires.", "msg.travel": "Estoy de visita.", "msg.leave": "Me voy el",
        "msg.name": "Nombre", "msg.code": "Código",
        "zones": ["Muñeca", "Antebrazo", "Brazo", "Mano o dedos", "Clavícula", "Costillas", "Espalda", "Tobillo", "Otra"],
        "sizes": ["Mini, hasta 5 cm", "Chico, de 5 a 10 cm", "Mediano, de 10 a 15 cm", "Grande, más de 15 cm", "No sé todavía"],
        "stay": ["Vivo acá", "Estoy de visita"],
    },
    "pt": {
        "meta.title": "Tatuagem fine line em Buenos Aires | EDS Tattoo Studio",
        "meta.desc": "Tatuagens fine line no Microcentro de Buenos Aires. Nota 5,0 no Google com mais de 230 avaliações. Me conta sua ideia pelo WhatsApp.",
        "og.alt": "Tatuagem fine line do sol argentino na omoplata",
        "skip": "Ir para o formulário",
        "nav.lang": "Idioma",
        "hero.h1": "Tatuagens fine line no centro de Buenos Aires",
        "hero.lead": "Eu sou o Eduardo, especialista em fine line. Tatuo no meu estúdio na San Martín 569, no Microcentro.",
        "hero.proof": "Nota 5,0 no Google, com mais de 230 avaliações",
        "hero.proofLink": "Ler avaliações",
        "hero.cta": "Me conta sua ideia",
        "work.h2": "Trabalhos",
        "work.lead": "Em cada foto, o círculo mostra a linha de perto.",
        "reviews.h2": "Avaliações",
        "reviews.lead": "Nota 5,0 de 5 no Google, com mais de 230 avaliações.",
        "reviews.live": "Nota {r} de 5 no Google, com {n} avaliações.",
        "reviews.order": "O Google ordena por relevância.",
        "reviews.translated": "Traduzida pelo Google",
        "reviews.onMaps": "Ver no Google Maps",
        "reviews.starsLabel": "{n} de 5 estrelas",
        "reviews.link": "Ler todas no Google",
        "steps.h2": "Como funciona",
        "steps.1": "Você me conta sua ideia no formulário: o que quer fazer, o tamanho e se mora aqui ou está de visita.",
        "steps.2": "O WhatsApp abre com tudo já escrito. Você envia e, se tiver uma foto de referência, manda junto.",
        "steps.3": "Eu respondo pelo WhatsApp e combinamos desenho, preço e dia.",
        "form.h2": "Me conta sua ideia",
        "form.lead": "São quatro dados e o WhatsApp abre com sua mensagem pronta.",
        "f.idea": "Breve descrição do que você quer fazer",
        "f.idea.ph": "Ex.: um raminho de oliveira com folhas pequenas",
        "f.zone": "Local do corpo",
        "f.size": "Tamanho aproximado",
        "f.stay": "Você mora em Buenos Aires ou está de visita?",
        "f.leave": "Que dia você vai embora?",
        "f.name": "Seu nome",
        "f.phone": "Seu WhatsApp, com código do país",
        "f.phone.ph": "+55 11 91234 5678",
        "f.privacy": "Seu número é usado para te responder e, criptografado, para medir quais anúncios trazem contatos.",
        "f.privacyLink": "Política de privacidade",
        "f.submit": "Enviar pelo WhatsApp",
        "f.submitNote": "O WhatsApp abre com sua mensagem já escrita.",
        "err.idea": "Me conta o que você quer tatuar.",
        "err.zone": "Escolha um local.",
        "err.size": "Escolha um tamanho.",
        "err.stay": "Me diga se você mora aqui ou está de visita.",
        "err.phone": "Coloque seu WhatsApp com o código do país, por exemplo +55 11 91234 5678.",
        "done.title": "Sua mensagem está pronta",
        "done.text": "Se o WhatsApp não abriu, toque no botão e envie por lá.",
        "done.code": "Código do seu contato",
        "done.open": "Abrir WhatsApp",
        "done.copy": "Copiar mensagem",
        "done.copied": "Mensagem copiada",
        "place.h2": "Onde fica",
        "place.addr": "San Martín 569, Microcentro, Buenos Aires",
        "place.link": "Como chegar",
        "sticky": "Me conta sua ideia",
        "foot.privacy": "Privacidade",
        "msg.hello": "Oi Eduardo, estou escrevendo pelo site.",
        "msg.idea": "Ideia", "msg.zone": "Local", "msg.size": "Tamanho",
        "msg.local": "Moro em Buenos Aires.", "msg.travel": "Estou de visita.", "msg.leave": "Vou embora em",
        "msg.name": "Nome", "msg.code": "Código",
        "zones": ["Pulso", "Antebraço", "Braço", "Mão ou dedos", "Clavícula", "Costelas", "Costas", "Tornozelo", "Outro"],
        "sizes": ["Mini, até 5 cm", "Pequeno, de 5 a 10 cm", "Médio, de 10 a 15 cm", "Grande, mais de 15 cm", "Ainda não sei"],
        "stay": ["Moro aqui", "Estou de visita"],
    },
    "en": {
        "meta.title": "Fine line tattoos in Buenos Aires | EDS Tattoo Studio",
        "meta.desc": "Fine line tattoos in downtown Buenos Aires. Rated 5.0 on Google from more than 230 reviews. Tell me your idea and I'll reply on WhatsApp.",
        "og.alt": "Fine line tattoo of the Argentine sun on a shoulder blade",
        "skip": "Skip to the form",
        "nav.lang": "Language",
        "hero.h1": "Fine line tattoos in downtown Buenos Aires",
        "hero.lead": "I'm Eduardo. I specialize in fine line and tattoo at my studio at San Martín 569, in Microcentro.",
        "hero.proof": "Rated 5.0 on Google from more than 230 reviews",
        "hero.proofLink": "Read reviews",
        "hero.cta": "Tell me your idea",
        "work.h2": "Work",
        "work.lead": "In each photo, the circle shows the line up close.",
        "reviews.h2": "Reviews",
        "reviews.lead": "Rated 5.0 out of 5 on Google from more than 230 reviews.",
        "reviews.live": "Rated {r} out of 5 on Google from {n} reviews.",
        "reviews.order": "Google sorts them by relevance.",
        "reviews.translated": "Translated by Google",
        "reviews.onMaps": "View on Google Maps",
        "reviews.starsLabel": "{n} out of 5 stars",
        "reviews.link": "Read them all on Google",
        "steps.h2": "How it works",
        "steps.1": "Tell me your idea in the form: what you want, the size, and whether you live here or are visiting.",
        "steps.2": "WhatsApp opens with everything already written. Send it, and add a reference photo there if you have one.",
        "steps.3": "I reply on WhatsApp and we settle the design, price and day.",
        "form.h2": "Tell me your idea",
        "form.lead": "Four quick answers and WhatsApp opens with your message ready.",
        "f.idea": "Short description of what you want",
        "f.idea.ph": "E.g. an olive branch with tiny leaves",
        "f.zone": "Placement",
        "f.size": "Approximate size",
        "f.stay": "Do you live in Buenos Aires or are you visiting?",
        "f.leave": "What day do you leave?",
        "f.name": "Your name",
        "f.phone": "Your WhatsApp, with country code",
        "f.phone.ph": "+1 212 555 0123",
        "f.privacy": "Your number is used to reply to you and, encrypted, to measure which ads bring inquiries.",
        "f.privacyLink": "Privacy policy",
        "f.submit": "Send via WhatsApp",
        "f.submitNote": "WhatsApp opens with your message already written.",
        "err.idea": "Tell me what you'd like to get.",
        "err.zone": "Pick a placement.",
        "err.size": "Pick a size.",
        "err.stay": "Tell me if you live here or are visiting.",
        "err.phone": "Add your WhatsApp with the country code, for example +1 212 555 0123.",
        "done.title": "Your message is ready",
        "done.text": "If WhatsApp didn't open, tap the button and send it from there.",
        "done.code": "Your inquiry code",
        "done.open": "Open WhatsApp",
        "done.copy": "Copy message",
        "done.copied": "Message copied",
        "place.h2": "Where to find me",
        "place.addr": "San Martín 569, Microcentro, Buenos Aires",
        "place.link": "Get directions",
        "sticky": "Tell me your idea",
        "foot.privacy": "Privacy",
        "msg.hello": "Hi Eduardo, I'm writing from your website.",
        "msg.idea": "Idea", "msg.zone": "Placement", "msg.size": "Size",
        "msg.local": "I live in Buenos Aires.", "msg.travel": "I'm visiting.", "msg.leave": "I leave on",
        "msg.name": "Name", "msg.code": "Code",
        "zones": ["Wrist", "Forearm", "Upper arm", "Hand or fingers", "Collarbone", "Ribs", "Back", "Ankle", "Other"],
        "sizes": ["Mini, up to 5 cm (2 in)", "Small, 5 to 10 cm (2 to 4 in)", "Medium, 10 to 15 cm (4 to 6 in)", "Large, over 15 cm (6 in)", "Not sure yet"],
        "stay": ["I live here", "I'm visiting"],
    },
    "de": {
        "meta.title": "Fine-Line-Tattoos in Buenos Aires | EDS Tattoo Studio",
        "meta.desc": "Fine-Line-Tattoos im Microcentro von Buenos Aires. 5,0 bei Google mit mehr als 230 Bewertungen. Erzähl mir deine Idee per WhatsApp.",
        "og.alt": "Fine-Line-Tattoo der argentinischen Sonne auf dem Schulterblatt",
        "skip": "Zum Formular springen",
        "nav.lang": "Sprache",
        "hero.h1": "Fine-Line-Tattoos im Zentrum von Buenos Aires",
        "hero.lead": "Ich bin Eduardo, spezialisiert auf Fine Line. Ich tätowiere in meinem Studio in der San Martín 569 im Microcentro.",
        "hero.proof": "5,0 bei Google mit mehr als 230 Bewertungen",
        "hero.proofLink": "Bewertungen lesen",
        "hero.cta": "Erzähl mir deine Idee",
        "work.h2": "Arbeiten",
        "work.lead": "Auf jedem Foto zeigt der Kreis die Linie aus der Nähe.",
        "reviews.h2": "Bewertungen",
        "reviews.lead": "5,0 von 5 bei Google mit mehr als 230 Bewertungen.",
        "reviews.live": "{r} von 5 bei Google mit {n} Bewertungen.",
        "reviews.order": "Google sortiert sie nach Relevanz.",
        "reviews.translated": "Von Google übersetzt",
        "reviews.onMaps": "Auf Google Maps ansehen",
        "reviews.starsLabel": "{n} von 5 Sternen",
        "reviews.link": "Alle auf Google lesen",
        "steps.h2": "So läuft es ab",
        "steps.1": "Du erzählst mir deine Idee im Formular: was du dir machen lassen willst, die Größe und ob du hier wohnst oder zu Besuch bist.",
        "steps.2": "WhatsApp öffnet sich mit allem schon ausgefüllt. Du schickst es ab und hängst dort ein Referenzbild an, wenn du eins hast.",
        "steps.3": "Ich antworte dir auf WhatsApp und wir klären Motiv, Preis und Termin.",
        "form.h2": "Erzähl mir deine Idee",
        "form.lead": "Vier Angaben, und WhatsApp öffnet sich mit deiner fertigen Nachricht.",
        "f.idea": "Kurze Beschreibung, was du dir machen lassen willst",
        "f.idea.ph": "Z. B. ein Olivenzweig mit kleinen Blättern",
        "f.zone": "Körperstelle",
        "f.size": "Ungefähre Größe",
        "f.stay": "Wohnst du in Buenos Aires oder bist du zu Besuch?",
        "f.leave": "Wann reist du ab?",
        "f.name": "Dein Name",
        "f.phone": "Deine WhatsApp-Nummer mit Ländervorwahl",
        "f.phone.ph": "+49 151 23456789",
        "f.privacy": "Deine Nummer wird genutzt, um dir zu antworten, und verschlüsselt, um zu messen, welche Anzeigen Anfragen bringen.",
        "f.privacyLink": "Datenschutzerklärung",
        "f.submit": "Per WhatsApp senden",
        "f.submitNote": "WhatsApp öffnet sich mit deiner Nachricht, schon fertig geschrieben.",
        "err.idea": "Erzähl mir, was du dir tätowieren lassen möchtest.",
        "err.zone": "Wähle eine Körperstelle.",
        "err.size": "Wähle eine Größe.",
        "err.stay": "Sag mir, ob du hier wohnst oder zu Besuch bist.",
        "err.phone": "Gib deine WhatsApp-Nummer mit Ländervorwahl ein, zum Beispiel +49 151 23456789.",
        "done.title": "Deine Nachricht ist fertig",
        "done.text": "Falls sich WhatsApp nicht geöffnet hat, tippe auf den Button und sende sie von dort.",
        "done.code": "Code deiner Anfrage",
        "done.open": "WhatsApp öffnen",
        "done.copy": "Nachricht kopieren",
        "done.copied": "Nachricht kopiert",
        "place.h2": "So findest du mich",
        "place.addr": "San Martín 569, Microcentro, Buenos Aires",
        "place.link": "Route anzeigen",
        "sticky": "Erzähl mir deine Idee",
        "foot.privacy": "Datenschutz",
        "msg.hello": "Hallo Eduardo, ich schreibe dir über deine Website.",
        "msg.idea": "Idee", "msg.zone": "Körperstelle", "msg.size": "Größe",
        "msg.local": "Ich wohne in Buenos Aires.", "msg.travel": "Ich bin zu Besuch.", "msg.leave": "Ich reise ab am",
        "msg.name": "Name", "msg.code": "Code",
        "zones": ["Handgelenk", "Unterarm", "Oberarm", "Hand oder Finger", "Schlüsselbein", "Rippen", "Rücken", "Knöchel", "Andere"],
        "sizes": ["Mini, bis 5 cm", "Klein, 5 bis 10 cm", "Mittel, 10 bis 15 cm", "Groß, über 15 cm", "Weiß ich noch nicht"],
        "stay": ["Ich wohne hier", "Ich bin zu Besuch"],
    },
}

RUNTIME_KEYS = [k for k in T["es"] if k.startswith(("err.", "msg.", "done.", "reviews."))]

PRIVACY = {
    "es": {
        "title": "Política de privacidad",
        "updated": "Actualizada el 22 de octubre de 2026",
        "body": [
            ("Quién es el responsable", ["EDS Tattoo Studio, San Martín 569, Microcentro, Ciudad Autónoma de Buenos Aires, Argentina. WhatsApp: " + PHONE_LABEL + "."]),
            ("Qué datos se piden y para qué", ["Cuando usás el formulario se piden una corta descripción de lo que te querés hacer, el tamaño aproximado, si vivís en Buenos Aires o estás de visita, y tu número de WhatsApp. Se usan para responderte y coordinar el tatuaje. Darlos es voluntario; sin el número de WhatsApp no te podemos responder."]),
            ("Medición de anuncios", ["Si llegaste por un anuncio de Google, la página guarda en tu navegador el identificador de ese clic durante 90 días. Cuando la medición de Google Ads está activa, al mandar el formulario tu número de WhatsApp se envía a Google cifrado, en un formato que no permite leerlo, para medir qué anuncios traen consultas. Si después te tatuás, podemos informarle a Google ese resultado y su monto, asociado al mismo número cifrado."]),
            ("Con quién se comparten", [
                ["Google, para medir las visitas (Google Analytics), medir los anuncios (Google Ads) y mostrar en esta página las reseñas públicas de Google Maps. Para mostrarlas, tu navegador se conecta con Google.",
                 "WhatsApp (Meta), cuando mandás el mensaje desde tu teléfono.",
                 "Cloudflare, que aloja esta página."],
                "Estos proveedores pueden tratar datos fuera de Argentina."]),
            ("Cuánto tiempo se guardan", ["Mientras sean necesarios para responderte, coordinar el tatuaje y medir los anuncios. Podés pedir que los borremos cuando quieras."]),
            ("Tus derechos", ["Podés pedir acceso, corrección, actualización o eliminación de tus datos escribiendo al WhatsApp de arriba. Tenés derecho a acceder a ellos en forma gratuita cada seis meses, salvo que acredites un interés legítimo para hacerlo antes (artículo 14, inciso 3, de la Ley 25.326). La Agencia de Acceso a la Información Pública, como órgano de control de la Ley 25.326, atiende las denuncias y reclamos de quienes vean afectados sus derechos por incumplimiento de las normas de protección de datos personales."]),
            ("Cookies", ["La página usa Google Analytics, para saber cuántas personas la visitan, y Google Ads, para saber qué anuncios traen consultas. Las dos herramientas usan cookies de Google. Si estás en Europa, el Reino Unido o Suiza, no se activan hasta que las aceptes en el aviso. Estés donde estés, podés aceptarlas o rechazarlas y cambiar tu elección cuando quieras desde el enlace «Cookies» al pie de cada página. La página guarda en tu navegador tu elección y el identificador del clic de Google.", "Cómo usa Google la información de los sitios que usan sus servicios: https://policies.google.com/technologies/partner-sites"]),
        ],
    },
    "pt": {
        "title": "Política de privacidade",
        "updated": "Atualizada em 22 de outubro de 2026",
        "body": [
            ("Quem é o responsável", ["EDS Tattoo Studio, San Martín 569, Microcentro, Cidade Autônoma de Buenos Aires, Argentina. WhatsApp: " + PHONE_LABEL + "."]),
            ("Quais dados pedimos e para quê", ["Quando você usa o formulário, pedimos uma breve descrição do que você quer fazer, o tamanho aproximado, se mora em Buenos Aires ou está de visita, e seu número de WhatsApp. Usamos esses dados para te responder e combinar a tatuagem. Informá-los é voluntário; sem o número de WhatsApp não conseguimos te responder."]),
            ("Medição de anúncios", ["Se você chegou por um anúncio do Google, a página guarda no seu navegador o identificador desse clique por 90 dias. Quando a medição do Google Ads está ativa, ao enviar o formulário seu número de WhatsApp é enviado ao Google criptografado, num formato que não permite lê-lo, para medir quais anúncios trazem contatos. Se depois você fizer a tatuagem, podemos informar ao Google esse resultado e o valor, associados ao mesmo número criptografado."]),
            ("Com quem compartilhamos", [
                ["Google, para medir as visitas (Google Analytics), medir os anúncios (Google Ads) e mostrar nesta página as avaliações públicas do Google Maps. Para mostrá-las, seu navegador se conecta ao Google.",
                 "WhatsApp (Meta), quando você envia a mensagem pelo seu celular.",
                 "Cloudflare, que hospeda esta página."],
                "Esses fornecedores podem tratar dados fora da Argentina."]),
            ("Por quanto tempo guardamos", ["Enquanto forem necessários para te responder, combinar a tatuagem e medir os anúncios. Você pode pedir que os apaguemos quando quiser."]),
            ("Seus direitos", ["Você pode pedir acesso, correção, atualização ou exclusão dos seus dados pelo WhatsApp acima. Você tem direito de acessá-los gratuitamente a cada seis meses, salvo se comprovar um interesse legítimo para fazê-lo antes (artigo 14, inciso 3, da Lei 25.326 da Argentina). A Agencia de Acceso a la Información Pública, como órgão de controle da Lei 25.326, recebe denúncias e reclamações de quem tiver seus direitos afetados pelo descumprimento das normas de proteção de dados pessoais."]),
            ("Cookies", ["A página usa o Google Analytics, para saber quantas pessoas a visitam, e o Google Ads, para saber quais anúncios trazem contatos. As duas ferramentas usam cookies do Google. Se você está na Europa, no Reino Unido ou na Suíça, elas só são ativadas depois que você as aceitar no aviso. Esteja onde estiver, você pode aceitá-las ou recusá-las e mudar sua escolha quando quiser pelo link «Cookies» no rodapé de cada página. A página guarda no seu navegador a sua escolha e o identificador do clique do Google.", "Como o Google usa as informações de sites que usam seus serviços: https://policies.google.com/technologies/partner-sites"]),
        ],
    },
    "en": {
        "title": "Privacy policy",
        "updated": "Updated October 22, 2026",
        "body": [
            ("Who is responsible", ["EDS Tattoo Studio, San Martín 569, Microcentro, City of Buenos Aires, Argentina. WhatsApp: " + PHONE_LABEL + "."]),
            ("What we ask for and why", ["When you use the form we ask for a short description of what you want, the approximate size, whether you live in Buenos Aires or are visiting, and your WhatsApp number. We use them to reply to you and arrange your tattoo. Giving them is voluntary; without your WhatsApp number we can't reply."]),
            ("Ad measurement", ["If you arrived through a Google ad, the page stores that click's identifier in your browser for 90 days. When Google Ads measurement is on, sending the form passes your WhatsApp number to Google in encrypted form, which can't be read, to measure which ads bring inquiries. If you later get tattooed, we may report that result and its amount to Google, linked to the same encrypted number."]),
            ("Who we share it with", [
                ["Google, to measure visits (Google Analytics), measure ads (Google Ads) and show public Google Maps reviews on this page. To show them, your browser connects to Google.",
                 "WhatsApp (Meta), when you send the message from your phone.",
                 "Cloudflare, which hosts this page."],
                "These providers may process data outside Argentina."]),
            ("How long we keep it", ["As long as it's needed to reply to you, arrange your tattoo and measure the ads. You can ask us to delete it at any time."]),
            ("Your rights", ["You can ask to access, correct, update or delete your data by writing to the WhatsApp above. You have the right to access it free of charge every six months, unless you show a legitimate interest in doing so sooner (Article 14, section 3, of Argentina's Law 25,326). The Agencia de Acceso a la Información Pública, as the authority in charge of Law 25,326, handles complaints from anyone whose rights are affected by a breach of the personal data protection rules."]),
            ("Cookies", ["The page uses Google Analytics, to know how many people visit it, and Google Ads, to know which ads bring inquiries. Both use Google cookies. If you are in Europe, the United Kingdom or Switzerland, they stay off until you accept them in the notice. Wherever you are, you can accept or reject them and change your choice at any time with the “Cookies” link at the bottom of every page. The page stores your choice and the Google click identifier in your browser.", "How Google uses information from sites that use its services: https://policies.google.com/technologies/partner-sites"]),
        ],
    },
    "de": {
        "title": "Datenschutzerklärung",
        "updated": "Aktualisiert am 22. Oktober 2026",
        "body": [
            ("Verantwortlich", ["EDS Tattoo Studio, San Martín 569, Microcentro, Stadt Buenos Aires, Argentinien. WhatsApp: " + PHONE_LABEL + "."]),
            ("Welche Daten wir abfragen und wofür", ["Wenn du das Formular nutzt, fragen wir nach einer kurzen Beschreibung deines Wunschtattoos, der ungefähren Größe, ob du in Buenos Aires wohnst oder zu Besuch bist, und deiner WhatsApp-Nummer. Wir nutzen diese Daten, um dir zu antworten und dein Tattoo zu planen. Die Angaben sind freiwillig; ohne WhatsApp-Nummer können wir dir nicht antworten."]),
            ("Messung von Anzeigen", ["Wenn du über eine Google-Anzeige gekommen bist, speichert die Seite die Kennung dieses Klicks 90 Tage lang in deinem Browser. Wenn die Google-Ads-Messung aktiv ist, wird deine WhatsApp-Nummer beim Absenden des Formulars verschlüsselt an Google übermittelt, in einer Form, die sich nicht lesen lässt, um zu messen, welche Anzeigen Anfragen bringen. Wenn du dich danach tätowieren lässt, können wir Google dieses Ergebnis und den Betrag melden, verknüpft mit derselben verschlüsselten Nummer."]),
            ("Mit wem wir Daten teilen", [
                ["Google, um Besuche (Google Analytics) und Anzeigen (Google Ads) zu messen und auf dieser Seite öffentliche Google-Maps-Bewertungen anzuzeigen. Dafür verbindet sich dein Browser mit Google.",
                 "WhatsApp (Meta), wenn du die Nachricht von deinem Handy sendest.",
                 "Cloudflare, das diese Seite hostet."],
                "Diese Anbieter können Daten außerhalb Argentiniens verarbeiten."]),
            ("Wie lange wir Daten speichern", ["So lange, wie es nötig ist, um dir zu antworten, dein Tattoo zu planen und die Anzeigen zu messen. Du kannst jederzeit verlangen, dass wir sie löschen."]),
            ("Deine Rechte", ["Du kannst über das WhatsApp oben Auskunft, Berichtigung, Aktualisierung oder Löschung deiner Daten verlangen. Du hast das Recht, alle sechs Monate kostenlos Auskunft zu erhalten, sofern du kein berechtigtes Interesse an einer früheren Auskunft nachweist (Artikel 14, Absatz 3 des argentinischen Gesetzes 25.326). Die Agencia de Acceso a la Información Pública ist als Aufsichtsbehörde für das Gesetz 25.326 für Beschwerden zuständig, wenn Rechte durch Verstöße gegen den Datenschutz verletzt werden."]),
            ("Cookies", ["Die Seite nutzt Google Analytics, um zu wissen, wie viele Menschen sie besuchen, und Google Ads, um zu wissen, welche Anzeigen Anfragen bringen. Beide verwenden Cookies von Google. Wenn du in Europa, im Vereinigten Königreich oder in der Schweiz bist, bleiben sie aus, bis du sie im Hinweis akzeptierst. Egal wo du bist, kannst du sie annehmen oder ablehnen und deine Wahl jederzeit über den Link „Cookies“ unten auf jeder Seite ändern. Die Seite speichert deine Wahl und die Google-Klickkennung in deinem Browser.", "Wie Google Informationen von Websites nutzt, die seine Dienste verwenden: https://policies.google.com/technologies/partner-sites"]),
        ],
    },
}

NOT_FOUND = {
    "es": ("Esta página no existe.", "Ir al inicio"),
    "pt": ("Esta página não existe.", "Ir para o início"),
    "en": ("This page doesn't exist.", "Go to the home page"),
    "de": ("Diese Seite gibt es nicht.", "Zur Startseite"),
}

esc = html.escape


def h8(path):
    with open(path, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()[:8]


def write(rel, text):
    path = os.path.join(OUT, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


# ---------- assets ----------
def build_assets():
    shutil.rmtree(OUT, ignore_errors=True)
    os.makedirs(OUT)
    a = {}
    for kind, name, ext in [("css", "site", "css"), ("js", "site", "js")]:
        src = os.path.join(SRC, "%s.%s" % (name, ext))
        rel = "assets/%s/%s.%s.%s" % (kind, name, h8(src), ext)
        os.makedirs(os.path.join(OUT, os.path.dirname(rel)), exist_ok=True)
        shutil.copyfile(src, os.path.join(OUT, rel))
        a[kind] = "/" + rel
    os.makedirs(os.path.join(OUT, "assets/fonts"))
    for n in WEB_FONTS:
        shutil.copyfile(os.path.join(SRC, "fonts", n), os.path.join(OUT, "assets/fonts", n))
    os.makedirs(os.path.join(OUT, "assets/img"))
    from PIL import Image
    a["img"] = {}
    for n in sorted(os.listdir(os.path.join(SRC, "img"))):
        src = os.path.join(SRC, "img", n)
        base, ext = os.path.splitext(n)
        rel = "assets/img/%s.%s%s" % (base, h8(src), ext)
        shutil.copyfile(src, os.path.join(OUT, rel))
        w, h = Image.open(src).size
        a["img"][n] = {"url": "/" + rel, "w": w, "h": h}
        if n == HERO["file"]:
            # versión chica para el celular: la foto de arriba es lo primero que mide Google (LCP)
            small = Image.open(src).convert("RGB")
            small = small.resize((720, round(h * 720 / w)), Image.LANCZOS)
            tmp = os.path.join(OUT, "assets/img/_tmp.webp")
            small.save(tmp, "WEBP", quality=78, method=6)
            rel_s = "assets/img/%s-720.%s%s" % (base, h8(tmp), ext)
            os.replace(tmp, os.path.join(OUT, rel_s))
            a["img"][n]["srcset"] = "/%s 720w, /%s %dw" % (rel_s, rel, w)
    brand = os.path.join(SRC, "brand")
    for n in os.listdir(brand):
        shutil.copyfile(os.path.join(brand, n), os.path.join(OUT, n))
    return a


# ---------- shared pieces ----------
def head(lang_attr, title, desc, path, alternates, assets, og_locale, og_alt, extra=""):
    canonical = SITE + path
    alt_links = "".join('<link rel="alternate" hreflang="%s" href="%s">\n' % (hl, SITE + p) for hl, p in alternates)
    return f"""<!doctype html>
<html lang="{lang_attr}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="format-detection" content="address=no">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<link rel="canonical" href="{canonical}">
{alt_links}<meta name="theme-color" content="#FCFCFE" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#000000" media="(prefers-color-scheme: dark)">
<link rel="icon" href="/favicon.ico" sizes="48x48">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="manifest" href="/site.webmanifest">
<meta property="og:type" content="website">
<meta property="og:site_name" content="{BRAND}">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{SITE}/og.jpg">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="{esc(og_alt)}">
<meta property="og:locale" content="{og_locale}">
<meta name="twitter:card" content="summary_large_image">
<link rel="preload" href="/assets/fonts/montserrat-latin-600-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="/assets/fonts/montserrat-latin-400-normal.woff2" as="font" type="font/woff2" crossorigin>
{extra}<link rel="stylesheet" href="{assets['css']}">
<script src="{assets['js']}" defer></script>
</head>
"""


# same hours as the Google Business Profile (oct 2026)
OPENING_HOURS = [
    {"@type": "OpeningHoursSpecification", "dayOfWeek": "Monday", "opens": "10:00:00", "closes": "20:30:00"},
    {"@type": "OpeningHoursSpecification", "dayOfWeek": "Tuesday", "opens": "10:00:00", "closes": "21:00:00"},
    {"@type": "OpeningHoursSpecification",
     "dayOfWeek": ["Wednesday", "Thursday", "Friday", "Saturday", "Sunday"], "opens": "10:00:00", "closes": "20:00:00"},
]


def ld_json(path_url, lang=None):
    graph = [
        {"@type": "WebSite", "@id": SITE + "/#website", "url": SITE + "/", "name": BRAND,
         "inLanguage": ["es", "pt", "en", "de"]},
        {"@type": "TattooParlor", "@id": SITE + "/#studio", "name": BRAND, "url": SITE + "/",
         "image": SITE + "/og.jpg", "logo": SITE + "/logo-512.png", "telephone": PHONE_E164,
         "address": {"@type": "PostalAddress", "streetAddress": STREET, "postalCode": "C1004AAK",
                     "addressLocality": "Buenos Aires", "addressRegion": "Ciudad Autónoma de Buenos Aires",
                     "addressCountry": "AR"},
         "openingHoursSpecification": OPENING_HOURS,
         "sameAs": ["https://instagram.com/eduardoink", "https://www.youtube.com/@EduardoGomezR"]},
    ]
    if lang:
        graph.append({"@type": "WebPage", "@id": SITE + path_url + "#page", "url": SITE + path_url,
                      "name": T[lang]["meta.title"], "inLanguage": HTML_LANG[lang],
                      "isPartOf": {"@id": SITE + "/#website"}, "about": {"@id": SITE + "/#studio"}})
    data = {"@context": "https://schema.org", "@graph": graph}
    return '<script type="application/ld+json">' + json.dumps(data, ensure_ascii=False).replace("</", "<\\/") + "</script>\n"


def langs_nav(lang, paths):
    t = T[lang]
    items = []
    for l in LANGS:
        cur = ' aria-current="page"' if l == lang else ""
        items.append(f'<a href="{paths[l]}" hreflang="{l}" lang="{HTML_LANG[l]}"{cur}>{l.upper()}</a>')
    return f'<nav class="langs" aria-label="{esc(t["nav.lang"])}">' + "".join(items) + "</nav>"


def top(lang, paths, home):
    return f"""<header class="top">
<a class="mark" href="{home}">{header_logo()}</a>
{langs_nav(lang, paths)}
</header>
"""


def foot(lang):
    t = T[lang]
    others = "".join(f'<a href="/{l}/" hreflang="{l}" lang="{HTML_LANG[l]}">{LANG_NAME[l]}</a>' for l in LANGS)
    return f"""<footer class="foot">
<span>{BRAND}</span>
<a href="{esc(MAPS_REVIEWS)}" target="_blank" rel="noopener">{esc(t["place.addr"])}</a>
<a href="{WA_URL}" target="_blank" rel="noopener">WhatsApp {PHONE_LABEL}</a>
<nav aria-label="{esc(t["nav.lang"])}"><a href="/{lang}/{PRIVACY_SLUG[lang]}/">{esc(t["foot.privacy"])}</a><button type="button" class="linkish" data-cookie-settings>Cookies</button>{others}</nav>
</footer>
"""


def chips(name, items):
    out = []
    for i, label in enumerate(items):
        out.append(f'<input class="chip-input" type="radio" name="{name}" id="{name}-{i}" value="{i}"><label class="chip" for="{name}-{i}">{esc(label)}</label>')
    return "".join(out)


def photo(item, lang, assets, cls, eager=False):
    im = assets["img"][item["file"]]
    alt = ALT_PREFIX[lang] + item["cap"][lang]
    load = 'fetchpriority="high" decoding="async"' if eager else 'loading="lazy" decoding="async"'
    if im.get("srcset"):
        load += f' srcset="{im["srcset"]}" sizes="{HERO_SIZES}" data-full="{im["url"]}"'
    return (f'<img src="{im["url"]}" width="{im["w"]}" height="{im["h"]}" alt="{esc(alt)}" {load} style="object-position:{item["pos"]}">'
            f'<span class="loupe" aria-hidden="true" style="background-position:{item["focus"]}"></span>')


# ---------- pages ----------
def home_page(lang, assets):
    t = T[lang]
    path = "/%s/" % lang
    paths = {l: "/%s/" % l for l in LANGS}
    alternates = [(l, "/%s/" % l) for l in LANGS] + [("x-default", "/")]
    extra = hero_preload(assets) + ld_json(path, lang)
    works = "\n".join(
        f'<figure class="work"><div class="work-photo" data-loupe>{photo(w, lang, assets, "work")}</div><figcaption>{esc(w["cap"][lang])}</figcaption></figure>'
        for w in WORKS)
    runtime = {"lang": lang, "locale": LOCALE[lang], "apiLang": API_LANG[lang],
               "t": {k: t[k] for k in RUNTIME_KEYS},
               "sizes": t["sizes"], "sizesEs": T["es"]["sizes"]}
    runtime_json = json.dumps(runtime, ensure_ascii=False).replace("</", "<\\/")
    body = f"""<body>
<a class="skip" href="#idea">{esc(t["skip"])}</a>
<div class="band"><div class="wrap">
{top(lang, paths, path)}
<section class="hero" aria-labelledby="h-hero">
<figure class="hero-photo" data-loupe>{photo(HERO, lang, assets, "hero", eager=True)}</figure>
<div class="hero-text">
<h1 id="h-hero">{esc(t["hero.h1"])}</h1>
<p class="lead">{esc(t["hero.lead"])}</p>
<p class="proof"><span class="stars" aria-hidden="true">★★★★★</span><span>{esc(t["hero.proof"])}</span><a href="#resenas">{esc(t["hero.proofLink"])}</a></p>
<a class="btn" id="hero-cta" href="#idea">{esc(t["hero.cta"])}</a>
</div>
</section>
</div></div>
<main id="inicio" class="wrap">

<section class="block" id="trabajos" aria-labelledby="h-work">
<div class="block-head"><h2 id="h-work">{esc(t["work.h2"])}</h2><p class="sub">{esc(t["work.lead"])}</p></div>
<div class="works">
{works}
</div>
</section>

<section class="block" id="resenas" aria-labelledby="h-reviews">
<div class="block-head"><h2 id="h-reviews">{esc(t["reviews.h2"])}</h2><p class="big" id="reviews-summary">{esc(t["reviews.lead"])}</p></div>
<div class="gm-box" id="gm-box" hidden>
<ol class="reviews" id="reviews-list"></ol>
<div class="gm-foot"><span>{esc(t["reviews.order"])}</span><span class="gm-attr" translate="no">Google Maps</span></div>
</div>
<div class="links"><a id="reviews-link" href="{esc(MAPS_REVIEWS)}" target="_blank" rel="noopener">{esc(t["reviews.link"])}</a></div>
</section>

<section class="block" id="como" aria-labelledby="h-steps">
<div class="block-head"><h2 id="h-steps">{esc(t["steps.h2"])}</h2></div>
<ol class="steps">
<li><p>{esc(t["steps.1"])}</p></li>
<li><p>{esc(t["steps.2"])}</p></li>
<li><p>{esc(t["steps.3"])}</p></li>
</ol>
</section>

<section class="block" id="idea" aria-labelledby="h-form">
<div class="block-head"><h2 id="h-form">{esc(t["form.h2"])}</h2><p class="sub">{esc(t["form.lead"])}</p></div>
<div class="form-card">
<form class="form" id="lead-form" novalidate>
<div class="field">
<label class="label" for="f-idea">{esc(t["f.idea"])}</label>
<textarea class="input" id="f-idea" name="idea" rows="2" maxlength="300" placeholder="{esc(t["f.idea.ph"])}" aria-describedby="err-idea"></textarea>
<p class="error" id="err-idea" hidden></p>
</div>
<fieldset aria-describedby="err-size"><legend>{esc(t["f.size"])}</legend><div class="chips">{chips("size", t["sizes"])}</div><p class="error" id="err-size" hidden></p></fieldset>
<fieldset aria-describedby="err-stay"><legend>{esc(t["f.stay"])}</legend><div class="chips">{chips("stay", t["stay"])}</div><p class="error" id="err-stay" hidden></p></fieldset>
<div class="field">
<label class="label" for="f-phone">{esc(t["f.phone"])}</label>
<input class="input" id="f-phone" name="phone" type="tel" inputmode="tel" autocomplete="tel" placeholder="{esc(t["f.phone.ph"])}" aria-describedby="err-phone">
<p class="error" id="err-phone" hidden></p>
</div>
<div class="submit-row">
<button class="btn" type="submit" id="f-submit">{esc(t["f.submit"])}</button>
<p class="hint">{esc(t["f.submitNote"])}</p>
<p class="hint">{esc(t["f.privacy"])} <a href="/{lang}/{PRIVACY_SLUG[lang]}/">{esc(t["f.privacyLink"])}</a></p>
</div>
</form>
<div class="done" id="done" hidden aria-live="polite">
<h3>{esc(t["done.title"])}</h3>
<p>{esc(t["done.text"])}</p>
<p class="hint">{esc(t["done.code"])}: <span class="code" id="done-code"></span></p>
<pre class="msg" id="done-msg"></pre>
<div class="done-actions">
<a class="btn" id="done-open" href="{WA_URL}" target="_blank" rel="noopener">{esc(t["done.open"])}</a>
<button type="button" class="btn btn-line" id="done-copy">{esc(t["done.copy"])}</button>
</div>
</div>
</div>
</section>

<section class="block" id="donde" aria-labelledby="h-place">
<div class="block-head"><h2 id="h-place">{esc(t["place.h2"])}</h2></div>
<p class="big"><a href="{esc(MAPS_REVIEWS)}" target="_blank" rel="noopener">{esc(t["place.addr"])}</a></p>
<div class="links"><a href="{esc(MAPS_DIRECTIONS)}" target="_blank" rel="noopener">{esc(t["place.link"])}</a></div>
</section>
</main>
<div class="wrap">{foot(lang)}</div>
<div class="sticky" id="sticky" hidden><a class="btn" href="#idea">{esc(t["sticky"])}</a></div>
<script id="eds-page" type="application/json">{runtime_json}</script>
</body>
</html>
"""
    return head(HTML_LANG[lang], t["meta.title"], t["meta.desc"], path, alternates, assets, OG_LOCALE[lang], t["og.alt"], extra) + body


def chooser_page(assets):
    extra = hero_preload(assets) + ld_json("/")
    alternates = [(l, "/%s/" % l) for l in LANGS] + [("x-default", "/")]
    items = "\n".join(
        f'<li><a href="/{l}/" hreflang="{l}" lang="{HTML_LANG[l]}" data-lang="{l}"><span class="lang-name">{LANG_NAME[l]}</span><span class="lang-line">{esc(LANG_LINE[l])}</span></a></li>'
        for l in LANGS)
    title = "EDS Tattoo Studio | Fine line tattoos in Buenos Aires"
    desc = "Fine line tattoos in downtown Buenos Aires. Tatuajes fine line en Microcentro. Tatuagens fine line em Buenos Aires. Fine-Line-Tattoos in Buenos Aires."
    body = f"""<body>
<div class="band band-full"><div class="wrap">
<header class="top"><a class="mark" href="/">{header_logo()}</a></header>
<main>
<section class="choose" aria-labelledby="h-choose">
<figure class="hero-photo" data-loupe>{photo(HERO, "en", assets, "hero", eager=True)}</figure>
<div class="choose-head">
<h1 id="h-choose">{BRAND}</h1>
<p class="sub">San Martín 569, Microcentro, Buenos Aires</p>
<ul class="choose-list">
{items}
</ul>
</div>
</section>
</main>
<footer class="foot">
<span>{BRAND}</span>
<a href="{WA_URL}" target="_blank" rel="noopener">WhatsApp {PHONE_LABEL}</a>
<nav aria-label="Privacy"><a href="/en/privacy/">Privacy</a><button type="button" class="linkish" data-cookie-settings>Cookies</button></nav>
</footer>
</div></div>
</body>
</html>
"""
    return head("en", title, desc, "/", alternates, assets, "en_US", T["en"]["og.alt"], extra) + body


def privacy_page(lang, assets):
    t = T[lang]
    p = PRIVACY[lang]
    path = "/%s/%s/" % (lang, PRIVACY_SLUG[lang])
    paths = {l: "/%s/%s/" % (l, PRIVACY_SLUG[l]) for l in LANGS}
    alternates = [(l, paths[l]) for l in LANGS] + [("x-default", paths["en"])]
    parts = []
    for heading, blocks in p["body"]:
        parts.append(f"<h2>{esc(heading)}</h2>")
        for b in blocks:
            if isinstance(b, list):
                parts.append("<ul>" + "".join(f"<li>{esc(x)}</li>" for x in b) + "</ul>")
            else:
                parts.append(f"<p>{esc(b)}</p>")
    body = f"""<body>
<div class="wrap">
{top(lang, paths, "/%s/" % lang)}
<main class="prose">
<h1>{esc(p["title"])}</h1>
<p class="sub">{esc(p["updated"])}</p>
{"".join(parts)}
</main>
{foot(lang)}</div>
</body>
</html>
"""
    return head(HTML_LANG[lang], p["title"] + " | " + BRAND, p["title"] + ", " + BRAND + ".", path, alternates, assets, OG_LOCALE[lang], t["og.alt"]) + body


def not_found_page(assets):
    lines = "\n".join(
        f'<p lang="{HTML_LANG[l]}">{esc(NOT_FOUND[l][0])} <a href="/{l}/" hreflang="{l}">{esc(NOT_FOUND[l][1])}</a></p>'
        for l in LANGS)
    page = head("en", "404 | " + BRAND, "Page not found.", "/404.html", [], assets, "en_US", T["en"]["og.alt"],
                '<meta name="robots" content="noindex">\n')
    return page + f"""<body>
<div class="wrap">
<header class="top"><a class="mark" href="/">{header_logo()}</a></header>
<main class="prose">
<h1>404</h1>
{lines}
</main>
</div>
</body>
</html>
"""


# ---------- site files ----------
def sitemap():
    groups = [{l: "/%s/" % l for l in LANGS}, {l: "/%s/%s/" % (l, PRIVACY_SLUG[l]) for l in LANGS}]
    defaults = ["/", groups[1]["en"]]
    out = ['<?xml version="1.0" encoding="UTF-8"?>',
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">']
    for g, xdef in zip(groups, defaults):
        locs = list(g.values()) + ([xdef] if xdef not in g.values() else [])
        for loc in locs:
            out.append("  <url>")
            out.append("    <loc>%s%s</loc>" % (SITE, loc))
            out.append("    <lastmod>%s</lastmod>" % TODAY)
            for l in LANGS:
                out.append('    <xhtml:link rel="alternate" hreflang="%s" href="%s%s"/>' % (l, SITE, g[l]))
            out.append('    <xhtml:link rel="alternate" hreflang="x-default" href="%s%s"/>' % (SITE, xdef))
            out.append("  </url>")
    out.append("</urlset>\n")
    return "\n".join(out)


HEADERS = """/*
  Strict-Transport-Security: max-age=31536000; includeSubDomains
  X-Content-Type-Options: nosniff
  Referrer-Policy: strict-origin-when-cross-origin
  Permissions-Policy: camera=(), microphone=(), geolocation=(), payment=(), usb=()
  X-Frame-Options: SAMEORIGIN

/assets/*
  Cache-Control: public, max-age=31536000, immutable
"""

REDIRECTS = """/privacy /en/privacy/ 301
/privacidad /es/privacidad/ 301
/privacidade /pt/privacidade/ 301
/datenschutz /de/datenschutz/ 301
"""

ROBOTS = """User-agent: *
Allow: /

Sitemap: %s/sitemap.xml
""" % SITE

MANIFEST = json.dumps({
    "name": BRAND, "short_name": "EDS Tattoo", "start_url": "/", "display": "browser",
    "background_color": "#FCFCFE", "theme_color": "#000000",
    "icons": [{"src": "/icon-192.png", "sizes": "192x192", "type": "image/png"},
              {"src": "/icon-512.png", "sizes": "512x512", "type": "image/png"}],
}, ensure_ascii=False, indent=2) + "\n"


def main():
    assets = build_assets()
    write("index.html", chooser_page(assets))
    for l in LANGS:
        write("%s/index.html" % l, home_page(l, assets))
        write("%s/%s/index.html" % (l, PRIVACY_SLUG[l]), privacy_page(l, assets))
    write("404.html", not_found_page(assets))
    write("sitemap.xml", sitemap())
    write("robots.txt", ROBOTS)
    write("_headers", HEADERS)
    write("_redirects", REDIRECTS)
    write("site.webmanifest", MANIFEST)
    total = 0
    for root, _, files in os.walk(OUT):
        for f in files:
            total += os.path.getsize(os.path.join(root, f))
    print("listo:", OUT, "(%.1f MB)" % (total / 1048576))


if __name__ == "__main__":
    main()
