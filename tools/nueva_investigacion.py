#!/usr/bin/env python3
"""Añade una investigación a partir de un vídeo de YouTube y regenera la web.

Saca de YouTube (con yt-dlp) la fecha, la duración y la descripción, comprueba
qué miniatura existe, guarda la entrada en data/investigaciones.json y ejecuta
tools/build.py.

Ejemplos:
  python3 tools/nueva_investigacion.py Vm9UtqlORaI --titulo "El Pont del Diable de Martorell" --tipo Leyenda
  python3 tools/nueva_investigacion.py https://youtu.be/GzM0WQy0Ees \\
      --titulo "Torre Salvana — Método Estes" --slug torre-salvana-metodo-estes \\
      --tarjeta "Texto corto para las tarjetas" \\
      --parrafo "Primer párrafo de la ficha" --parrafo "Segundo párrafo"

Todos los textos se guardan como HTML (el script escapa "&", "<"…).
Si no pasas --tarjeta / --parrafo se rellenan con la descripción de YouTube
(limpia de enlaces y hashtags). Repásalos después en data/investigaciones.json
y vuelve a ejecutar tools/build.py.
"""
import argparse
import html
import json
import re
import shutil
import subprocess
import sys
import unicodedata
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / 'data' / 'investigaciones.json'


def video_id(arg):
    m = re.search(r'(?:v=|youtu\.be/|embed/|shorts/)([\w-]{11})', arg)
    if m:
        return m.group(1)
    if re.fullmatch(r'[\w-]{11}', arg):
        return arg
    sys.exit(f'No reconozco el ID de YouTube en: {arg}')


def yt_info(vid):
    exe = shutil.which('yt-dlp') or '/opt/homebrew/bin/yt-dlp'
    try:
        out = subprocess.run([exe, '--skip-download', '-J', '--', vid],
                             capture_output=True, text=True, check=True).stdout
    except (OSError, subprocess.CalledProcessError) as e:
        sys.exit(f'yt-dlp falló ({e}). Instálalo con: brew install yt-dlp')
    return json.loads(out)


def has_maxres(vid):
    req = urllib.request.Request(f'https://img.youtube.com/vi/{vid}/maxresdefault.jpg', method='HEAD')
    try:
        return urllib.request.urlopen(req, timeout=10).status == 200
    except urllib.error.URLError:
        return False


def slugify(text):
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode()
    return re.sub(r'[^a-z0-9]+', '-', text.lower()).strip('-')


def smart_quotes(text):
    """Comillas rectas → tipográficas, para que no rompan atributos HTML."""
    out, open_q = [], True
    for ch in text:
        if ch == '"':
            out.append('“' if open_q else '”')
            open_q = not open_q
        else:
            out.append(ch)
    return ''.join(out)


def as_html(text):
    return html.escape(smart_quotes(text.strip()), quote=False)


def clean_paragraphs(description):
    """Párrafos útiles de la descripción: sin enlaces, hashtags, separadores ni llamadas a suscribirse."""
    good = []
    for block in re.split(r'\n\s*\n', description):
        lines = []
        for line in block.splitlines():
            line = line.strip()
            if not line or re.search(r'https?://|www\.|\.com\b|@\w|#\w|━|suscr[ií]bete|tiktok|instagram', line, re.I):
                continue
            if not re.search(r'[a-záéíóúñ]{3}', line, re.I):     # solo emojis o símbolos
                continue
            lines.append(line)
        text = ' '.join(lines)
        if len(text) > 40:
            good.append(re.sub(r'\s+', ' ', text))
    return good


def truncate(text, limit):
    if len(text) <= limit:
        return text
    return text[:limit].rsplit(' ', 1)[0].rstrip(',.;:') + '…'


def main():
    ap = argparse.ArgumentParser(description='Añade una investigación desde YouTube.')
    ap.add_argument('video', help='ID o URL del vídeo de YouTube')
    ap.add_argument('--titulo', help='Título en la web (por defecto, el de YouTube)')
    ap.add_argument('--slug', help='Nombre del archivo, p. ej. torre-salvana (por defecto, a partir del título)')
    ap.add_argument('--tipo', default='Sitio visitado', help='Etiqueta: "Sitio visitado" (por defecto), "Leyenda"…')
    ap.add_argument('--tarjeta', help='Texto corto de la tarjeta (portada y videoteca)')
    ap.add_argument('--parrafo', action='append', help='Párrafo de "Sobre esta investigación" (repetible)')
    ap.add_argument('--seo-descripcion', help='Meta description (por defecto, la tarjeta recortada)')
    ap.add_argument('--keywords', help='Meta keywords separadas por comas')
    ap.add_argument('--sin-build', action='store_true', help='Solo guardar en el JSON, sin regenerar la web')
    args = ap.parse_args()

    vid = video_id(args.video)
    items = json.loads(DATA.read_text(encoding='utf-8'))
    if any(i['youtube_id'] == vid for i in items):
        sys.exit(f'El vídeo {vid} ya está en data/investigaciones.json')

    print(f'Consultando YouTube ({vid})…')
    info = yt_info(vid)
    titulo = as_html(args.titulo or info['title'])
    slug = args.slug or slugify(html.unescape(titulo))
    if any(i['slug'] == slug for i in items) or (ROOT / 'investigaciones' / f'{slug}.html').exists():
        sys.exit(f'Ya existe una investigación con slug "{slug}". Usa --slug para elegir otro.')

    desc_parrafos = clean_paragraphs(info.get('description') or '')
    parrafos = [as_html(p) for p in (args.parrafo or desc_parrafos[:2])]
    if not parrafos:
        sys.exit('La descripción de YouTube no tiene texto aprovechable: pasa al menos un --parrafo.')
    tarjeta = as_html(args.tarjeta) if args.tarjeta else as_html(truncate(html.unescape(parrafos[0]), 220))
    seo_desc = as_html(args.seo_descripcion) if args.seo_descripcion else as_html(truncate(html.unescape(tarjeta), 155))
    duracion = info['duration_string'] if ':' in info['duration_string'] else f"0:{int(info['duration_string']):02d}"
    d = info['upload_date']

    entry = {
        'slug': slug,
        'youtube_id': vid,
        'titulo': titulo,
        'tipo': args.tipo,
        'fecha': f'{d[:4]}-{d[4:6]}-{d[6:]}',
        'duracion': duracion,
        'miniatura': 'maxresdefault' if has_maxres(vid) else 'hqdefault',
        'tarjeta': tarjeta,
        'parrafos': parrafos,
        'seo': {
            'titulo': f'{titulo} — Investigación Paranormal | Enclave Paranormal',
            'descripcion': seo_desc,
            'keywords': as_html(args.keywords) if args.keywords else f'{titulo}, investigación paranormal, Enclave Paranormal',
            'og_type': 'website',
        },
    }
    items.append(entry)
    items.sort(key=lambda i: i['fecha'], reverse=True)
    DATA.write_text(json.dumps(items, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

    print(f'\nAñadida: {html.unescape(titulo)}  →  investigaciones/{slug}.html')
    print(f'  {entry["fecha"]} · {entry["duracion"]} · {entry["tipo"]} · miniatura {entry["miniatura"]}')
    if not args.parrafo:
        print('\n  Textos sacados de la descripción de YouTube. Revísalos en data/investigaciones.json.')
    if not args.sin_build:
        print()
        subprocess.run([sys.executable, str(ROOT / 'tools' / 'build.py')], check=True)


if __name__ == '__main__':
    main()
