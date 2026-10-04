#!/usr/bin/env python3
"""Sube a PythonAnywhere los archivos de la web que difieren de producción.

Compara cada archivo de la web (los que sigue git, sin tools/, data/ ni README)
con su copia en /home/agfcsoad/sitios-paranormales/ y sube solo los distintos.

El token de la API se lee de la variable de entorno PA_TOKEN o del archivo
tools/.pa_token (ignorado por git; nunca lo subas al repo, que es público).

Uso:
  python3 tools/desplegar.py            # sube lo que haya cambiado
  python3 tools/desplegar.py --simular  # solo muestra qué subiría
"""
import argparse
import os
import subprocess
import sys
import urllib.error
import urllib.request
import uuid
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
USER = 'agfcsoad'
REMOTE_DIR = f'/home/{USER}/sitios-paranormales'
API = f'https://www.pythonanywhere.com/api/v0/user/{USER}/files/path{REMOTE_DIR}/'
EXCLUDE_PREFIXES = ('tools/', 'data/', '.')
EXCLUDE_FILES = {'README.md'}


def token():
    tok = os.environ.get('PA_TOKEN')
    f = ROOT / 'tools' / '.pa_token'
    if not tok and f.exists():
        tok = f.read_text().strip()
    if not tok:
        sys.exit('Falta el token: exporta PA_TOKEN o guárdalo en tools/.pa_token')
    return tok


def site_files():
    out = subprocess.run(['git', 'ls-files'], cwd=ROOT, capture_output=True, text=True, check=True).stdout
    return [p for p in out.splitlines()
            if not p.startswith(EXCLUDE_PREFIXES) and p not in EXCLUDE_FILES]


def remote_bytes(path, tok):
    req = urllib.request.Request(API + path, headers={'Authorization': f'Token {tok}'})
    try:
        return urllib.request.urlopen(req, timeout=30).read()
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None
        raise


def upload(path, tok):
    boundary = uuid.uuid4().hex
    body = (f'--{boundary}\r\nContent-Disposition: form-data; name="content"; filename="{Path(path).name}"\r\n'
            f'Content-Type: application/octet-stream\r\n\r\n').encode() + (ROOT / path).read_bytes() \
        + f'\r\n--{boundary}--\r\n'.encode()
    req = urllib.request.Request(API + path, data=body, method='POST', headers={
        'Authorization': f'Token {tok}', 'Content-Type': f'multipart/form-data; boundary={boundary}'})
    return urllib.request.urlopen(req, timeout=60).status


def main():
    ap = argparse.ArgumentParser(description='Despliega la web en PythonAnywhere.')
    ap.add_argument('--simular', action='store_true', help='No sube nada, solo lista las diferencias')
    args = ap.parse_args()

    dirty = subprocess.run(['git', 'status', '--porcelain', '--untracked-files=no'], cwd=ROOT,
                           capture_output=True, text=True).stdout.strip()
    if dirty:
        print('Aviso: hay cambios sin commit; se subirá lo que hay en disco.\n')

    tok = token()
    files = site_files()
    print(f'Comparando {len(files)} archivos con producción…')
    with ThreadPoolExecutor(max_workers=8) as pool:
        remote = dict(zip(files, pool.map(lambda p: remote_bytes(p, tok), files)))
    pending = [p for p in files if remote[p] != (ROOT / p).read_bytes()]

    if not pending:
        print('Producción ya está al día.')
        return
    for p in pending:
        estado = 'nuevo' if remote[p] is None else 'modificado'
        if args.simular:
            print(f'  {estado:10} {p}')
        else:
            code = upload(p, tok)
            print(f'  {estado:10} {p}  → {code}')
    if not args.simular:
        print(f'\n{len(pending)} archivo(s) subido(s). Comprueba https://www.enclaveparanormal.com/')


if __name__ == '__main__':
    main()
