# sitios-paranormales

Web estática de **www.enclaveparanormal.com**: investigaciones, historias y ubicaciones paranormales.
Se sirve desde PythonAnywhere (`/home/agfcsoad/sitios-paranormales/`).

## Añadir una investigación nueva

Requisitos: Python 3 y [yt-dlp](https://github.com/yt-dlp/yt-dlp) (`brew install yt-dlp`).

```bash
python3 tools/nueva_investigacion.py <ID o URL de YouTube> --titulo "Título en la web" [--tipo Leyenda]
```

El script saca de YouTube la fecha, la duración y la descripción, la añade a
`data/investigaciones.json` y regenera la web. Opciones útiles:

| Opción | Para qué |
|---|---|
| `--slug nombre` | Nombre del archivo (`investigaciones/nombre.html`). Por defecto sale del título. |
| `--tipo "..."` | Etiqueta y filtro: `Sitio visitado` (por defecto), `Leyenda`… |
| `--tarjeta "..."` | Texto corto de las tarjetas (portada y videoteca). |
| `--parrafo "..."` | Párrafo de "Sobre esta investigación". Se puede repetir. |
| `--seo-descripcion`, `--keywords` | Meta tags. |

Si no pasas los textos se rellenan con la descripción de YouTube. Repásalos en
`data/investigaciones.json` y vuelve a generar la web.

## Actualizar los vídeos cortos

```bash
python3 tools/actualizar_shorts.py
```

Descarga la lista de Shorts del canal (títulos sin hashtags y visualizaciones) a
`data/shorts.json` y regenera `videos/index.html`. Ejecútalo cuando subas Shorts nuevos.

## Editar textos o datos existentes

1. Cambia `data/investigaciones.json`. Los textos son HTML: un `&` suelto se escribe `&amp;`.
2. Regenera la web: `python3 tools/build.py`

`build.py` reescribe:

- `index.html`: solo los bloques entre `<!-- auto:portada-… -->`.
- `investigaciones/index.html`: solo los bloques `<!-- auto:videoteca-… -->`.
- `investigaciones/<slug>.html`: la página entera. **No edites estas páginas a mano**: cambia la plantilla en `tools/build.py`.
- `videos/index.html`: solo los bloques `<!-- auto:videos-… -->`, a partir de `data/shorts.json`.
- `sitemap.xml`: añade las investigaciones que falten.

Todo lo que está fuera de los marcadores `auto:` se puede editar a mano.

## Publicar

```bash
git add -A && git commit -m "…" && git push
python3 tools/desplegar.py --simular   # ver qué se subiría
python3 tools/desplegar.py             # subir a PythonAnywhere
```

`desplegar.py` compara cada archivo de la web con producción y sube solo los distintos.
El token de la API de PythonAnywhere se lee de la variable `PA_TOKEN` o del archivo
`tools/.pa_token`. Ese archivo está en `.gitignore`: **no subas nunca el token**, porque este repositorio es público.
