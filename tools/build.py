#!/usr/bin/env python3
"""Regenera las partes automáticas de la web a partir de data/investigaciones.json.

Qué genera:
  - index.html                 → bloques <!-- auto:portada-* -->
  - investigaciones/index.html → bloques <!-- auto:videoteca-* -->
  - investigaciones/<slug>.html → la página completa de cada investigación
  - videos/index.html          → bloques <!-- auto:videos-* --> (desde data/shorts.json)
  - sitemap.xml                → añade las URLs de investigaciones que falten

Lo que queda fuera de los marcadores <!-- auto:... --> se puede editar a mano.
Los textos del JSON (tarjeta, párrafos) son HTML: escribe &amp; para un "&" suelto.

Uso:  python3 tools/build.py
"""
import html as htmllib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / 'data' / 'investigaciones.json'
SHORTS = ROOT / 'data' / 'shorts.json'
SHORTS_INICIALES = 24   # cámaras que se pintan en el HTML; el resto las añade js/videos.js
SITE = 'https://enclaveparanormal.com'
LOGO = ('https://yt3.googleusercontent.com/QkF6NLkCisTSMB9xesJVk0rK1WkPb946Tt2teUr1M8O4Ch'
        'shPeTQmF3qxEk9lDnYr8vkLKXUaA=s200-c-k-c0x00ffffff-no-rj')
CHANNEL = 'https://www.youtube.com/channel/UC5ooPVBZplLiqx4PbtVxVrw'
MESES = 'ENE FEB MAR ABR MAY JUN JUL AGO SEP OCT NOV DIC'.split()


# ---------- utilidades ----------

def load():
    items = json.loads(DATA.read_text(encoding='utf-8'))
    items.sort(key=lambda i: i['fecha'], reverse=True)
    for n, it in enumerate(items):
        it['num'] = len(items) - n
    return items


def vhsdate(fecha):
    y, m, d = fecha.split('-')
    return f'{MESES[int(m) - 1]}.{d} {y}'


def seconds(dur):
    total = 0
    for part in dur.split(':'):
        total = total * 60 + int(part)
    return total


def iso_duration(dur):
    s = seconds(dur)
    h, m, sec = s // 3600, (s // 60) % 60, s % 60
    return f'PT{h}H{m}M{sec}S' if h else f'PT{m}M{sec}S'


def thumb(it, quality=None):
    return f"https://img.youtube.com/vi/{it['youtube_id']}/{quality or it['miniatura']}.jpg"


def hero_bg(it):
    """Fondo con la mejor miniatura y, si es maxres, hqdefault de reserva."""
    urls = [thumb(it)] + ([thumb(it, 'hqdefault')] if it['miniatura'] == 'maxresdefault' else [])
    return ','.join(f"url('{u}')" for u in urls)


def tag_slug(tipo):
    return tipo.lower().replace(' ', '-')


def replace_block(html, name, content):
    pattern = re.compile(rf'(<!-- auto:{name} -->\n).*?(<!-- /auto:{name} -->\n)', re.S)
    if not pattern.search(html):
        sys.exit(f'Falta el marcador auto:{name}')
    return pattern.sub(lambda m: m.group(1) + content + m.group(2), html, count=1)


def write_if_changed(path, text, changed):
    if not path.exists() or path.read_text(encoding='utf-8') != text:
        path.write_text(text, encoding='utf-8')
        changed.append(str(path.relative_to(ROOT)))


# ---------- portada ----------

def portada_hero(latest, n):
    return f'''  <header class="tape-hero">
    <div class="tape-hero-img" style="background-image:{hero_bg(latest)}"></div>
    <div class="scanlines"></div>
    <div class="tracking-bar" aria-hidden="true"></div>

    <div class="osd osd-corner osd-tl" aria-hidden="true">▶ Play<span class="osd-small">Cinta {n:02d} · SP</span></div>
    <div class="osd osd-corner osd-tr" aria-hidden="true"><span class="rec-dot"></span><span id="osdClock">--:--</span></div>
    <div class="osd osd-corner osd-bl" aria-hidden="true" id="osdCounter">0:00:00</div>
    <div class="osd osd-corner osd-br" aria-hidden="true">{vhsdate(latest['fecha'])}</div>

    <div class="tape-hero-content">
      <p class="tape-label"><span class="rec-dot"></span>Última investigación</p>
      <h1 class="tape-title">{latest['titulo']}</h1>
      <p class="tape-desc">{latest['tarjeta']}</p>
      <div class="tape-actions">
        <a href="/investigaciones/{latest['slug']}.html" class="btn-vhs">▶ Reproducir cinta</a>
        <a href="#archivo" class="btn-vhs ghost">Ver el archivo</a>
      </div>
    </div>
  </header>
'''


def portada_cinta(it):
    return f'''        <a href="/investigaciones/{it['slug']}.html" class="tape-card">
          <div class="tape-screen">
            <img src="{thumb(it, 'hqdefault')}" alt="{it['titulo']}" loading="lazy" width="480" height="360" />
            <span class="osd tape-osd tl">Cinta {it['num']:02d}</span>
            <span class="osd tape-osd tr">{vhsdate(it['fecha'])}</span>
            <span class="osd tape-osd bl">▶ Play</span>
            <span class="osd tape-osd br">{it['duracion']}</span>
          </div>
          <div class="tape-spine">
            <span class="tape-num">#{it['num']:02d}</span>
            <h3 class="tape-name">{it['titulo']}</h3>
          </div>
          <p class="tape-text">{it['tarjeta']}</p>
        </a>'''


def build_portada(items, changed):
    path = ROOT / 'index.html'
    html = path.read_text(encoding='utf-8')
    n = len(items)
    html = replace_block(html, 'portada-hero', portada_hero(items[0], n))
    html = replace_block(html, 'portada-contador',
                         f'            <p class="osd archive-kicker">⏏ Archivo de cintas · {n} grabaciones</p>\n')
    html = replace_block(html, 'portada-cintas', '\n'.join(portada_cinta(i) for i in items) + '\n')
    write_if_changed(path, html, changed)


# ---------- videoteca ----------

def videoteca_cinta(it):
    return f'''          <a href="/investigaciones/{it['slug']}.html" class="vt-tape" data-year="{it['fecha'][:4]}" data-tag="{tag_slug(it['tipo'])}">
            <div class="vt-spine" aria-hidden="true"><span>Cinta {it['num']:02d}</span></div>
            <div class="tape-screen">
              <img src="{thumb(it, 'hqdefault')}" alt="{it['titulo']}" loading="lazy" width="480" height="360" />
              <span class="osd tape-osd tl">▶ Play</span>
              <span class="osd tape-osd tr">SP</span>
              <span class="osd tape-osd bl">● Rec</span>
              <span class="osd tape-osd br">{it['duracion']}</span>
            </div>
            <div class="vt-info">
              <div class="vt-meta"><span class="vt-tag">{it['tipo']}</span><span>{vhsdate(it['fecha'])}</span><span>{it['duracion']} min</span></div>
              <h2 class="vt-name">{it['titulo']}</h2>
              <p class="vt-text">{it['tarjeta']}</p>
              <span class="vt-cta">▶ Reproducir cinta</span>
            </div>
          </a>'''


def build_videoteca(items, changed):
    path = ROOT / 'investigaciones' / 'index.html'
    html = path.read_text(encoding='utf-8')
    n = len(items)
    years = sorted({i['fecha'][:4] for i in items}, reverse=True)
    tipos = sorted({i['tipo'] for i in items}, key=lambda t: (t != 'Sitio visitado', t))
    total = sum(seconds(i['duracion']) for i in items)

    mosaico = ''.join(f'<div style="background-image:url(\'{thumb(i, "mqdefault")}\')"></div>' for i in items[:6])
    html = replace_block(html, 'videoteca-mosaico',
                         f'    <div class="vt-hero-bg" aria-hidden="true">{mosaico}</div>\n')

    html = replace_block(html, 'videoteca-display', f'''      <div class="vcr-display" aria-label="Resumen del archivo">
        <p class="vcr-stat">{n:02d}<small>Cintas</small></p>
        <p class="vcr-stat">{total // 3600}H{(total // 60) % 60:02d}M<small>Grabación</small></p>
        <p class="vcr-stat">{years[-1]}–{years[0]}<small>Archivo</small></p>
      </div>
''')

    btns = [f'<button class="vt-btn" data-filter="all" aria-pressed="true">Todas<span class="count">{n}</span></button>']
    btns += [f'<button class="vt-btn" data-filter="year:{y}" aria-pressed="false">{y}'
             f'<span class="count">{sum(i["fecha"][:4] == y for i in items)}</span></button>' for y in years]
    btns += [f'<button class="vt-btn" data-filter="tag:{tag_slug(t)}" aria-pressed="false">{t}'
             f'<span class="count">{sum(i["tipo"] == t for i in items)}</span></button>' for t in tipos]
    html = replace_block(html, 'videoteca-filtros',
                         '      <span class="osd vt-controls-label">Filtro ▸</span>\n'
                         + ''.join(f'      {b}\n' for b in btns))

    groups = []
    for y in years:
        ys = [i for i in items if i['fecha'][:4] == y]
        cintas = '\n'.join(videoteca_cinta(i) for i in ys)
        groups.append(f'''      <section class="vt-year" data-year="{y}">
        <div class="vt-year-head">
          <h2 class="osd vt-year-num">▶ {y}</h2>
          <span class="vt-year-count">{len(ys)} {'cinta' if len(ys) == 1 else 'cintas'}</span>
        </div>
        <div class="vt-list">
{cintas}
        </div>
      </section>''')
    html = replace_block(html, 'videoteca-estanteria', '\n'.join(groups) + '\n')
    write_if_changed(path, html, changed)


# ---------- fichas ----------

def nav_card(it, kind):
    label = '◀◀ Más reciente' if kind == 'rew' else 'Más antigua ▶▶'
    return f'''        <a href="/investigaciones/{it['slug']}.html" class="pb-nav-card {kind}">
          <div class="tape-screen">
            <img src="{thumb(it, 'mqdefault')}" alt="" loading="lazy" width="320" height="180" />
          </div>
          <div class="pb-nav-info">
            <span class="osd pb-nav-dir">{label}</span>
            <span class="pb-nav-name">Cinta {it['num']:02d} · {it['titulo']}</span>
          </div>
        </a>'''


def ficha(it, newer, older, n, nav, footer):
    seo = it['seo']
    url = f"{SITE}/investigaciones/{it['slug']}.html"
    vid = it['youtube_id']
    ld = {
        '@context': 'https://schema.org', '@type': 'VideoObject',
        'name': htmllib.unescape(it['titulo']), 'description': htmllib.unescape(seo['descripcion']),
        'thumbnailUrl': thumb(it), 'uploadDate': it['fecha'],
        'duration': iso_duration(it['duracion']),
        'embedUrl': f'https://www.youtube.com/embed/{vid}',
        'contentUrl': f'https://www.youtube.com/watch?v={vid}',
        'publisher': {'@type': 'Organization', 'name': 'Enclave Paranormal',
                      'logo': {'@type': 'ImageObject', 'url': LOGO}},
    }
    t = tag_slug(it['tipo'])
    spacer = '        <div class="pb-nav-spacer"></div>'
    nav_html = (nav_card(newer, 'rew') if newer else spacer) + '\n' + (nav_card(older, 'ff') if older else spacer)
    parrafos = '\n'.join(f'        <p>{p}</p>' for p in it['parrafos'])
    return f'''<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{seo['titulo']}</title>
  <meta name="description" content="{seo['descripcion']}" />
  <meta name="keywords" content="{seo['keywords']}" />
  <meta name="author" content="Enclave Paranormal" />
  <meta name="robots" content="index, follow" />
  <link rel="canonical" href="{url}" />

  <!-- Open Graph -->
  <meta property="og:type" content="{seo['og_type']}" />
  <meta property="og:title" content="{seo['titulo']}" />
  <meta property="og:description" content="{seo['descripcion']}" />
  <meta property="og:url" content="{url}" />
  <meta property="og:image" content="{thumb(it)}" />
  <meta property="og:site_name" content="Enclave Paranormal" />
  <meta property="og:locale" content="es_ES" />

  <!-- Twitter Card -->
  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:title" content="{seo['titulo']}" />
  <meta name="twitter:description" content="{seo['descripcion']}" />
  <meta name="twitter:image" content="{thumb(it)}" />
  <link rel="stylesheet" href="/css/style.css" />
  <link rel="stylesheet" href="/css/home.css" />
  <link rel="stylesheet" href="/css/investigaciones.css" />
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@400;700&family=Inter:wght@300;400;500&family=VT323&display=swap" rel="stylesheet" />
  <script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>
</head>
<body class="home">

  <canvas class="vhs-noise" id="vhsNoise" aria-hidden="true"></canvas>

{nav}

  <header class="pb-hero" data-tag="{t}">
    <div class="pb-hero-img" style="background-image:{hero_bg(it)}"></div>
    <div class="scanlines"></div>
    <div class="pb-hero-inner">
      <a href="/investigaciones/" class="osd vt-back">◀◀ Volver a la videoteca</a>
      <p class="osd pb-meta"><span class="vt-tag">{it['tipo']}</span><span>Cinta {it['num']:02d}</span><span>{vhsdate(it['fecha'])}</span><span>{it['duracion']}</span></p>
      <h1 class="pb-title">{it['titulo']}</h1>
    </div>
  </header>

  <div class="crt">
    <div class="crt-frame">
      <div class="crt-bar" aria-hidden="true">
        <span class="osd">▶ Play</span>
        <span class="osd"><span class="rec-dot"></span>SP · Cinta {it['num']:02d}</span>
      </div>
      <div class="crt-screen">
        <iframe
          src="https://www.youtube.com/embed/{vid}"
          title="{it['titulo']}"
          allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
          allowfullscreen loading="lazy">
        </iframe>
      </div>
      <div class="crt-bar bottom" aria-hidden="true">
        <span class="osd"><span class="crt-led"></span>Enclave Paranormal</span>
        <span class="osd">{vhsdate(it['fecha'])}</span>
      </div>
    </div>
  </div>

  <main class="pb-body">
    <aside class="pb-card" data-tag="{t}">
      <div class="vt-spine" aria-hidden="true"><span>Cinta {it['num']:02d}</span></div>
      <dl>
        <div><dt>Cinta</dt><dd>{it['num']:02d} / {n:02d}</dd></div>
        <div><dt>Grabación</dt><dd>{vhsdate(it['fecha'])}</dd></div>
        <div><dt>Duración</dt><dd>{it['duracion']}</dd></div>
        <div><dt>Tipo</dt><dd>{it['tipo']}</dd></div>
        <div><a class="pb-yt" href="https://www.youtube.com/watch?v={vid}" target="_blank" rel="noopener">▶ Ver en YouTube</a></div>
      </dl>
    </aside>
    <div class="pb-text">
      <h2 class="osd">Sobre esta investigación</h2>
{parrafos}
    </div>
  </main>

  <nav class="pb-nav" aria-label="Más investigaciones">
    <div class="container">
      <div class="pb-nav-grid">
{nav_html}
      </div>
      <div class="pb-nav-all"><a href="/investigaciones/" class="btn-vhs ghost">⏏ Ver todas las cintas</a></div>
    </div>
  </nav>

{footer}

  <script src="/js/main.js"></script>
  <script src="/js/home.js"></script>
  <script data-goatcounter="https://enclaveparanormal.goatcounter.com/count" async src="//gc.zgo.at/count.js"></script>
</body>
</html>
'''


def build_fichas(items, changed):
    home = (ROOT / 'index.html').read_text(encoding='utf-8')
    nav = home[home.index('  <nav'):home.index('</nav>') + 6].replace(
        '<li><a href="/investigaciones/">',
        '<li><a href="/investigaciones/" aria-current="page" style="color:#a855f7">')
    footer = home[home.index('  <footer'):home.index('</footer>') + 9]
    for i, it in enumerate(items):
        newer = items[i - 1] if i > 0 else None
        older = items[i + 1] if i + 1 < len(items) else None
        write_if_changed(ROOT / 'investigaciones' / f"{it['slug']}.html",
                         ficha(it, newer, older, len(items), nav, footer), changed)


# ---------- vídeos cortos ----------

def vistas(n):
    """1400 → '1,4K', 8000 → '8K', 245 → '245'."""
    if n < 1000:
        return str(n)
    if n < 1_000_000:
        v, suf = n / 1000, 'K'
    else:
        v, suf = n / 1_000_000, 'M'
    txt = f'{v:.1f}'.rstrip('0').rstrip('.') if v < 100 else f'{v:.0f}'
    return txt.replace('.', ',') + suf


def camara(sh, num):
    t = htmllib.escape(sh['titulo'], quote=True)
    return f'''        <a class="cam" href="https://www.youtube.com/shorts/{sh['id']}" data-id="{sh['id']}" target="_blank" rel="noopener">
          <div class="cam-screen">
            <img src="https://i.ytimg.com/vi/{sh['id']}/oar2.jpg" alt="" loading="lazy" width="270" height="480" />
            <span class="osd tape-osd tl">Cam {num:03d}</span>
            <span class="osd tape-osd tr">● Rec</span>
            <span class="osd tape-osd bl">▶ Play</span>
            <span class="osd tape-osd br">{vistas(sh['vistas'])}</span>
            <span class="cam-play" aria-hidden="true">▶</span>
          </div>
          <p class="cam-title">{t}</p>
        </a>'''


def build_videos(changed):
    if not SHORTS.exists():
        return
    shorts = json.loads(SHORTS.read_text(encoding='utf-8'))
    n = len(shorts)
    path = ROOT / 'videos' / 'index.html'
    html = path.read_text(encoding='utf-8')
    top = sorted(shorts, key=lambda s: -s['vistas'])
    mosaico = ''.join(f'<div style="background-image:url(\'https://i.ytimg.com/vi/{s["id"]}/oar2.jpg\')"></div>'
                      for s in top[:8])
    html = replace_block(html, 'videos-mosaico', f'    <div class="vt-hero-bg" aria-hidden="true">{mosaico}</div>\n')
    html = replace_block(html, 'videos-display', f'''      <div class="vcr-display" aria-label="Resumen de la sala">
        <p class="vcr-stat">{n}<small>Cámaras</small></p>
        <p class="vcr-stat">{vistas(sum(s['vistas'] for s in shorts))}<small>Visualizaciones</small></p>
        <p class="vcr-stat red">● Rec<small>Grabando</small></p>
      </div>
''')
    html = replace_block(html, 'videos-camaras',
                         '\n'.join(camara(s, n - i) for i, s in enumerate(shorts[:SHORTS_INICIALES])) + '\n')
    datos = json.dumps([[s['id'], s['titulo'], s['vistas']] for s in shorts], ensure_ascii=False, separators=(',', ':'))
    datos = datos.replace('</', '<\\/')
    html = replace_block(html, 'videos-datos',
                         f'  <script type="application/json" id="shortsData" data-inicial="{SHORTS_INICIALES}">{datos}</script>\n')
    write_if_changed(path, html, changed)


# ---------- sitemap ----------

def build_sitemap(items, changed):
    path = ROOT / 'sitemap.xml'
    xml = path.read_text(encoding='utf-8')
    anchor = f'    <loc>{SITE}/investigaciones/</loc>'
    missing = [i for i in items if f"{SITE}/investigaciones/{i['slug']}.html</loc>" not in xml]
    if missing:
        end = xml.index('</url>\n', xml.index(anchor)) + len('</url>\n')
        add = ''.join(f'''  <url>
    <loc>{SITE}/investigaciones/{i['slug']}.html</loc>
    <changefreq>monthly</changefreq>
    <priority>0.8</priority>
  </url>
''' for i in missing)
        write_if_changed(path, xml[:end] + add + xml[end:], changed)


def main():
    items = load()
    slugs = [i['slug'] for i in items]
    if len(slugs) != len(set(slugs)):
        sys.exit('Hay slugs repetidos en data/investigaciones.json')
    changed = []
    build_portada(items, changed)       # primero: las fichas copian su nav/footer
    build_videoteca(items, changed)
    build_fichas(items, changed)
    build_videos(changed)
    build_sitemap(items, changed)
    print(f'{len(items)} investigaciones.', 'Archivos cambiados:' if changed else 'Sin cambios.')
    for c in changed:
        print('  ' + c)


if __name__ == '__main__':
    main()
