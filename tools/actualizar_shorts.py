#!/usr/bin/env python3
"""Descarga la lista de Shorts del canal y regenera la página de vídeos cortos.

Guarda id, título (sin hashtags) y visitas de cada Short en data/shorts.json,
en el orden del canal (más reciente primero), y ejecuta tools/build.py.

Uso:  python3 tools/actualizar_shorts.py
"""
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / 'data' / 'shorts.json'
CHANNEL_SHORTS = 'https://www.youtube.com/channel/UC5ooPVBZplLiqx4PbtVxVrw/shorts'


def clean_title(title):
    t = re.sub(r'#\S*', '', title)
    t = re.sub(r'\s+', ' ', t).strip(' -|·,')
    if t and not re.search(r'[a-záéíóúñ]', t):           # todo en mayúsculas → frase normal
        t = t[0] + t[1:].lower()
    return t or 'Grabación sin título'


def main():
    exe = shutil.which('yt-dlp') or '/opt/homebrew/bin/yt-dlp'
    print('Consultando los Shorts del canal…')
    try:
        out = subprocess.run([exe, '--flat-playlist', '-J', CHANNEL_SHORTS],
                             capture_output=True, text=True, check=True).stdout
    except (OSError, subprocess.CalledProcessError) as e:
        sys.exit(f'yt-dlp falló ({e}). Instálalo con: brew install yt-dlp')
    entries = json.loads(out).get('entries') or []
    shorts = [{'id': e['id'], 'titulo': clean_title(e.get('title') or ''), 'vistas': e.get('view_count') or 0}
              for e in entries if e.get('id')]
    if not shorts:
        sys.exit('YouTube no devolvió ningún Short; no toco data/shorts.json.')

    before = {s['id'] for s in json.loads(DATA.read_text(encoding='utf-8'))} if DATA.exists() else set()
    DATA.write_text(json.dumps(shorts, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
    nuevos = [s for s in shorts if s['id'] not in before]
    print(f'{len(shorts)} Shorts guardados ({len(nuevos)} nuevos).\n')
    subprocess.run([sys.executable, str(ROOT / 'tools' / 'build.py')], check=True)


if __name__ == '__main__':
    main()
