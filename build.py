#!/usr/bin/env python3
"""Genera docs/datos.js (lo que lee la web) y folios.html (lo que se imprime).

    python3 build.py --base https://usuario.github.io/halloween-qr

Cada QR apunta a  <base>/j.html?q=<acertijo>&o=<opción>.
El orden de las opciones sale de una semilla fija: reimprimir un folio no lo cambia.
"""
import argparse
import json
import random
import sys
from html import escape
from pathlib import Path

RAIZ = Path(__file__).parent
sys.path.insert(0, str(RAIZ / "vendor"))
import segno  # noqa: E402

PROB_SUSTO_ACIERTO = 0.25   # probabilidad de susto aunque la respuesta sea correcta

SUSTOS = [
    # Calavera
    '<svg viewBox="0 0 400 400" xmlns="http://www.w3.org/2000/svg"><rect width="400" height="400" fill="#000"/>'
    '<defs><radialGradient id="g1" cx="50%" cy="45%" r="55%"><stop offset="0" stop-color="#f4eeda"/><stop offset="1" stop-color="#6b6454"/></radialGradient></defs>'
    '<path d="M200 25C108 25 55 92 55 170c0 50 20 82 52 102v48c0 16 10 26 26 26h134c16 0 26-10 26-26v-48c32-20 52-52 52-102C345 92 292 25 200 25z" fill="url(#g1)"/>'
    '<ellipse cx="138" cy="175" rx="44" ry="56" fill="#000"/><ellipse cx="262" cy="175" rx="44" ry="56" fill="#000"/>'
    '<circle cx="140" cy="186" r="8" fill="#e8141e"/><circle cx="260" cy="186" r="8" fill="#e8141e"/>'
    '<path d="M200 212l-20 50h40z" fill="#000"/>'
    '<path d="M122 296h156v44H122z" fill="#000"/>'
    '<path d="M146 296v44M173 296v44M200 296v44M227 296v44M254 296v44" stroke="#ece6d2" stroke-width="11"/></svg>',
    # Rostro desencajado
    '<svg viewBox="0 0 400 400" xmlns="http://www.w3.org/2000/svg"><defs>'
    '<radialGradient id="g2" cx="50%" cy="50%" r="70%"><stop offset="0" stop-color="#5a0508"/><stop offset="1" stop-color="#000"/></radialGradient></defs>'
    '<rect width="400" height="400" fill="url(#g2)"/>'
    '<ellipse cx="200" cy="205" rx="122" ry="180" fill="#cdd4c0"/>'
    '<ellipse cx="148" cy="165" rx="40" ry="58" fill="#000" transform="rotate(-14 148 165)"/>'
    '<ellipse cx="252" cy="165" rx="40" ry="58" fill="#000" transform="rotate(14 252 165)"/>'
    '<circle cx="151" cy="172" r="7" fill="#ff2a2a"/><circle cx="249" cy="172" r="7" fill="#ff2a2a"/>'
    '<path d="M122 262Q200 284 278 262Q292 372 200 388Q108 372 122 262z" fill="#000"/>'
    '<polygon points="130,267 150,308 170,274 190,316 210,278 230,316 250,274 270,308 280,267" fill="#eee"/>'
    '<polygon points="150,372 168,338 188,380 212,380 232,338 250,372" fill="#eee"/></svg>',
    # Ojos en la oscuridad y sonrisa
    '<svg viewBox="0 0 400 400" xmlns="http://www.w3.org/2000/svg"><defs>'
    '<radialGradient id="g3" cx="50%" cy="50%" r="50%"><stop offset="0" stop-color="#fff7a8"/><stop offset=".5" stop-color="#ffb400"/><stop offset="1" stop-color="#ff6a00" stop-opacity="0"/></radialGradient></defs>'
    '<rect width="400" height="400" fill="#000"/>'
    '<ellipse cx="130" cy="150" rx="62" ry="40" fill="url(#g3)" transform="rotate(18 130 150)"/>'
    '<ellipse cx="270" cy="150" rx="62" ry="40" fill="url(#g3)" transform="rotate(-18 270 150)"/>'
    '<ellipse cx="136" cy="152" rx="7" ry="26" fill="#000" transform="rotate(18 136 152)"/>'
    '<ellipse cx="264" cy="152" rx="7" ry="26" fill="#000" transform="rotate(-18 264 152)"/>'
    '<path d="M38 238Q200 420 362 238Q200 322 38 238z" fill="#f2efe4"/>'
    '<path d="M80 252v52M110 266v62M140 276v68M170 281v72M200 283v74M230 281v72M260 276v68M290 266v62M320 252v52" stroke="#000" stroke-width="5"/></svg>',
]


def preparar(origen):
    acertijos = []
    for i, a in enumerate(origen, start=1):
        opciones = [a["correcta"]] + a["falsas"]
        random.Random(i).shuffle(opciones)
        acertijos.append({
            "id": i,
            "texto": a["texto"],
            "opciones": opciones,
            "correcta": opciones.index(a["correcta"]),
            "premio": a["premio"],
        })
    return acertijos


def escribir_datos(acertijos):
    web = [{k: a[k] for k in ("id", "opciones", "correcta", "premio")} for a in acertijos]
    js = "/* Generado por build.py; no editar a mano. */\n"
    js += "var PROB_SUSTO_ACIERTO = %s;\n" % PROB_SUSTO_ACIERTO
    js += "var ACERTIJOS = %s;\n" % json.dumps(web, ensure_ascii=False, indent=1)
    js += "var SUSTOS = %s;\n" % json.dumps(SUSTOS)
    (RAIZ / "docs" / "datos.js").write_text(js, encoding="utf-8")


CSS = """
@page { size: A4; margin: 0 }
* { box-sizing: border-box; margin: 0 }
body { font-family: Georgia, "Times New Roman", serif; color: #111; background: #fff }
.folio { width: 210mm; height: 297mm; padding: 14mm 16mm; page-break-after: always; display: flex; flex-direction: column }
.marco { flex: 1; border: 2.2mm double #d9600b; border-radius: 6mm; padding: 10mm 10mm 7mm; display: flex; flex-direction: column }
.cab { text-align: center; color: #d9600b; letter-spacing: .3em; font-size: 15pt; text-transform: uppercase }
.num { text-align: center; font-size: 46pt; line-height: 1; margin: 2mm 0 7mm }
.texto { text-align: center; font-size: 20pt; line-height: 1.4; font-style: italic; margin: 0 4mm 9mm }
.opciones { display: grid; grid-template-columns: 1fr 1fr; gap: 8mm 6mm; flex: 1; align-content: center }
.op { text-align: center }
.op svg { width: 52mm; height: 52mm; display: block; margin: 0 auto 2.5mm }
.op b { display: inline-block; width: 8mm; height: 8mm; line-height: 8mm; border-radius: 50%; background: #111; color: #fff; font-size: 13pt; margin-right: 2mm }
.op span { font-size: 17pt }
.pie { text-align: center; font-size: 10pt; color: #666; margin-top: 6mm }
@media screen { body { background: #888 } .folio { margin: 8mm auto; background: #fff } }
"""


def escribir_folios(acertijos, base):
    base = base.rstrip("/")
    paginas = []
    for a in acertijos:
        ops = []
        for i, texto in enumerate(a["opciones"]):
            url = "%s/j.html?q=%d&o=%d" % (base, a["id"], i)
            q = segno.make(url, error="m")
            ancho, alto = q.symbol_size(scale=4, border=2)
            qr = q.svg_inline(scale=4, border=2).replace("<svg ", '<svg viewBox="0 0 %d %d" ' % (ancho, alto), 1)
            ops.append('<div class="op">%s<b>%s</b><span>%s</span></div>' % (qr, "ABCD"[i], escape(texto)))
        paginas.append(
            '<section class="folio"><div class="marco">'
            '<div class="cab">Acertijo</div><div class="num">%d</div>'
            '<p class="texto">%s</p><div class="opciones">%s</div>'
            '<p class="pie">Escanea la opción que creas correcta. Ojo: este juego tiene sustos y sonidos fuertes.</p>'
            '</div></section>' % (a["id"], escape(a["texto"]), "".join(ops)))
    html = ('<!doctype html><html lang="es"><meta charset="utf-8"><title>Folios</title><style>%s</style><body>%s</body></html>'
            % (CSS, "".join(paginas)))
    (RAIZ / "folios.html").write_text(html, encoding="utf-8")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--base", default="http://localhost:8000",
                   help="dirección pública de la carpeta docs/ (sin barra final)")
    args = p.parse_args()
    acertijos = preparar(json.loads((RAIZ / "acertijos.json").read_text(encoding="utf-8")))
    escribir_datos(acertijos)
    escribir_folios(acertijos, args.base)
    print("%d acertijos. QR -> %s/j.html" % (len(acertijos), args.base.rstrip("/")))


if __name__ == "__main__":
    main()
