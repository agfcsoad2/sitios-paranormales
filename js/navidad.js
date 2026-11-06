// Navidad oscura: nieve, guirnalda de luces que fallan y Calendario de Adviento maldito.
(function () {
  const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const pad = n => String(n).padStart(2, '0');

  /* ---------- Nieve ---------- */
  const snow = document.createElement('canvas');
  snow.className = 'snow';
  snow.setAttribute('aria-hidden', 'true');
  document.body.prepend(snow);
  const ctx = snow.getContext('2d');
  let W = 0, H = 0, flakes = [];
  const dpr = Math.min(window.devicePixelRatio || 1, 2);
  const makeFlake = (y) => ({
    x: Math.random() * W,
    y: y ?? Math.random() * H,
    r: 0.6 + Math.random() * 2.2,
    vy: 0.25 + Math.random() * 0.9,
    vx: -0.2 + Math.random() * 0.4,
    ph: Math.random() * Math.PI * 2,
    a: 0.25 + Math.random() * 0.55,
  });
  const resize = () => {
    W = window.innerWidth; H = window.innerHeight;
    snow.width = W * dpr; snow.height = H * dpr;
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    const target = reduce ? 0 : Math.min(160, Math.round(W / 10));
    while (flakes.length < target) flakes.push(makeFlake());
    flakes.length = target;
  };
  resize();
  window.addEventListener('resize', resize);
  let wind = 0, t0 = 0;
  const frame = (t) => {
    const dt = Math.min(3, (t - t0) / 16.7 || 1); t0 = t;
    wind = Math.sin(t / 5200) * 0.5 + Math.sin(t / 1700) * 0.15;
    ctx.clearRect(0, 0, W, H);
    for (const f of flakes) {
      f.ph += 0.01 * dt;
      f.y += f.vy * dt;
      f.x += (f.vx + wind * f.r * 0.4 + Math.sin(f.ph) * 0.25) * dt;
      if (f.y > H + 4) Object.assign(f, makeFlake(-4));
      if (f.x > W + 4) f.x = -4; else if (f.x < -4) f.x = W + 4;
      ctx.beginPath();
      ctx.arc(f.x, f.y, f.r, 0, Math.PI * 2);
      ctx.fillStyle = `rgba(222,238,255,${f.a})`;
      ctx.fill();
    }
    requestAnimationFrame(frame);
  };
  if (!reduce) requestAnimationFrame(frame);

  /* ---------- Guirnalda ---------- */
  const nav = document.getElementById('nav');
  if (nav) {
    const g = document.createElement('div');
    g.className = 'garland';
    g.setAttribute('aria-hidden', 'true');
    nav.appendChild(g);
    const colors = ['#e23a4a', '#e8c46a', '#bfe6ff', '#3fae7a', '#e23a4a', '#e8c46a'];
    let seed = 7;
    const rnd = () => (seed = (seed * 16807) % 2147483647) / 2147483647; // estable entre recargas
    const draw = () => {
      seed = 7;
      const w = nav.clientWidth;
      const h = g.clientHeight;
      const span = w < 600 ? 90 : 130;
      const swags = Math.max(3, Math.round(w / span));
      const seg = w / swags;
      const sag = h * 0.55;
      let d = `M0 0`;
      const bulbs = [];
      for (let i = 0; i < swags; i++) {
        const x0 = i * seg, x1 = x0 + seg, cx = x0 + seg / 2;
        d += ` Q${cx} ${sag * 2} ${x1} 0`;
        const per = w < 600 ? 3 : 4;
        for (let k = 1; k <= per; k++) {
          const u = k / (per + 1);
          const x = (1 - u) * (1 - u) * x0 + 2 * (1 - u) * u * cx + u * u * x1;
          const y = 2 * (1 - u) * u * sag * 2;
          bulbs.push({ x, y, r: (u - 0.5) * -24 }); // ligera inclinación siguiendo el cable
        }
      }
      let html = `<svg viewBox="0 0 ${w} ${h}" preserveAspectRatio="none"><path class="wire" d="${d}"/></svg>`;
      bulbs.forEach((b, i) => {
        const c = colors[i % colors.length];
        const roll = rnd();
        const cls = roll < 0.08 ? 'bulb dead' : roll < 0.28 ? 'bulb flicker' : 'bulb';
        html += `<span class="${cls}" style="left:${b.x.toFixed(1)}px;top:${(b.y + 1).toFixed(1)}px;--c:${c};--r:${b.r.toFixed(1)}deg;--d:${(2.4 + rnd() * 4).toFixed(2)}s;--delay:-${(rnd() * 5).toFixed(2)}s"></span>`;
      });
      g.innerHTML = html;
    };
    draw();
    let rt;
    window.addEventListener('resize', () => { clearTimeout(rt); rt = setTimeout(draw, 150); });
    // Apagones ocasionales
    if (!reduce) {
      const blackout = () => {
        g.classList.add('blackout');
        setTimeout(() => g.classList.remove('blackout'), 90 + Math.random() * 160);
        if (Math.random() < 0.5) setTimeout(() => {
          g.classList.add('blackout');
          setTimeout(() => g.classList.remove('blackout'), 70);
        }, 260);
        setTimeout(blackout, 9000 + Math.random() * 14000);
      };
      setTimeout(blackout, 6000);
    }
  }

  /* ---------- Fechas ---------- */
  const params = new URLSearchParams(location.search);
  const now = new Date();
  const year = now.getMonth() === 0 ? now.getFullYear() - 1 : now.getFullYear();
  const nochebuena = new Date(year, 11, 24);
  const today0 = new Date(now.getFullYear(), now.getMonth(), now.getDate());
  const nightsTo = d => Math.round((d - today0) / 86400000);

  // OSD de la portada: cuenta atrás a Nochebuena
  const tl = document.querySelector('.osd-tl');
  if (tl) {
    const n = nightsTo(nochebuena);
    const s = document.createElement('span');
    s.className = 'osd-xmas';
    s.textContent = n > 1 ? `❄ ${n} noches para Nochebuena` : n === 1 ? '❄ Mañana es Nochebuena' : n === 0 ? '❄ Nochebuena' : '❄ Noches de Navidad';
    tl.appendChild(s);
  }

  /* ---------- Calendario de Adviento maldito ---------- */
  const grid = document.getElementById('adventGrid');
  if (!grid) return;

  const YT = {
    'pont-del-diable': 'Vm9UtqlORaI', 'torre-salvana-metodo-estes': 'GzM0WQy0Ees', 'la-puda': 'f7gzWaYCBv4',
    'torre-salvana': 'wQhoyPUMCVE', 'masia-20-regreso': 'HX9sQFek4YA', 'masia-20': 'MsQbhA6tvio',
    'hotel-posesion': 'LYUW1VVWfro', 'hotel-abandonado': '4mL61nR2MlM', 'casa-juguetes': 'Nfm2knJwWuw',
    'restaurante-abandonado': '_ErBKJlGehc', 'restaurante-herencia': '-Jar-H5dIGA', 'fabrica-abandonada': 'i0V-Z5xZnGM',
    'masia-siglo-xi': '7MXmSyKsec4', 'la-puda-psicofonias': 'nR0aEtGWnZI', 'casa-talamanca': '2T3MUeZsacQ',
    'casa-prohibida-2': 'GO7cf9rBY90', 'masia-tinajas': '9owuBb0xJpc', 'masia-mas-alla': 'Vn0e7CcTXUY',
  };
  const TITULOS = {
    'pont-del-diable': 'El Pont del Diable de Martorell', 'torre-salvana-metodo-estes': 'Torre Salvana — Método Estes',
    'la-puda': 'La Puda de Montserrat', 'torre-salvana': 'Torre Salvana', 'masia-20-regreso': 'Masía 20 — El regreso',
    'masia-20': 'Masía 20', 'hotel-posesion': 'Hotel Abandonado — Posesión', 'hotel-abandonado': 'Hotel Abandonado',
    'casa-juguetes': 'La Casa de los Juguetes', 'restaurante-abandonado': 'Restaurante Abandonado',
    'restaurante-herencia': 'Restaurante — La Herencia Olvidada', 'fabrica-abandonada': 'La Fábrica Abandonada',
    'masia-siglo-xi': 'Masía del Siglo XI', 'la-puda-psicofonias': 'La Puda — Psicofonías',
    'casa-talamanca': 'La Casa de Talamanca', 'casa-prohibida-2': 'La Casa Prohibida (Parte 2)',
    'masia-tinajas': 'La Masía de las Tinajas', 'masia-mas-alla': 'La Masía del Más Allá',
  };

  const L = [
    ['Krampus', 'Alpes · Austria y Baviera', ['Medio cabra, medio demonio, con cuernos, lengua larga y cadenas. La noche del 5 de diciembre, la Krampusnacht, acompaña a San Nicolás: el santo premia a los niños buenos y él se ocupa del resto, con un manojo de varas y un cesto a la espalda para llevárselos.', 'Todavía hoy, en muchos pueblos alpinos, cientos de Krampus con máscaras talladas a mano recorren las calles haciendo sonar cencerros.'], 'pont-del-diable'],
    ['Frau Perchta', 'Alpes · Baviera y Austria', ['La señora de los Doce Días. Durante las noches entre Navidad y Reyes entra en las casas para ver quién ha trabajado durante el año.', 'A los diligentes les deja una moneda de plata. A los perezosos, según la leyenda, les abre el vientre, les saca las entrañas y lo rellena de paja y piedras.'], 'masia-tinajas'],
    ['Jólakötturinn, el Gato de Yule', 'Islandia', ['Un gato enorme y hambriento que ronda las granjas en Nochebuena. No le interesan los regalos: busca a quien no haya estrenado ninguna prenda de ropa antes de Navidad.', 'A esos, se los come. Por eso en Islandia nadie llega a la Nochebuena sin algo nuevo encima.'], 'masia-20'],
    ['Grýla', 'Islandia', ['Una ogresa que vive en las montañas y baja cuando llega el frío. Lleva un saco a la espalda y huele a los niños desobedientes desde lejos.', 'Se los lleva a su cueva y los cocina en un caldero. Es la madre de los trece Jólasveinar, y su gato es el Gato de Yule.'], 'masia-mas-alla'],
    ['Los trece Jólasveinar', 'Islandia', ['Los hijos de Grýla bajan de las montañas uno por noche, del 12 al 24 de diciembre. Cada uno tiene su manía: uno lame los cucharones, otro roba salchichas, otro da portazos de madrugada.', 'Y uno de ellos, Gluggagægir, se queda quieto al otro lado del cristal mirando hacia dentro. Si de noche te sientes observado desde la ventana, ya sabes quién es.'], 'casa-prohibida-2'],
    ['Krampusnacht', 'Noche del 5 de diciembre', ['Esta es la noche. Antes del día de San Nicolás, las calles de los pueblos alpinos se llenan de fuego, humo y cencerros.', 'Se decía que, si un niño se portaba muy mal, Krampus no se conformaba con azotarle: lo metía en el cesto y lo arrastraba hasta el infierno.'], 'torre-salvana'],
    ['Knecht Ruprecht', 'Alemania', ['El sirviente oscuro de San Nicolás: barba larga, ropa negra o de paja, una vara y un saco de ceniza.', 'Llamaba a las puertas y preguntaba a los niños si sabían rezar. Si sabían, había manzanas y nueces. Si no, recibían la vara o el saco de ceniza.'], 'casa-talamanca'],
    ['Père Fouettard', 'Francia y Bélgica', ['El "padre azotador". La leyenda cuenta que era un carnicero que atrajo a tres niños a su tienda, los mató y los dejó en salmuera. San Nicolás los resucitó.', 'Como castigo, el carnicero tuvo que acompañar al santo para siempre, vestido de negro y con un látigo, para castigar a los niños que se portan mal.'], 'restaurante-abandonado'],
    ['El Tió de Nadal', 'Cataluña', ['El 8 de diciembre aparece en casa un tronco con cara, barretina y una manta para que no pase frío. Cada noche se le da de comer.', 'En Nochebuena se le golpea con palos mientras se le canta para que "cague" regalos. Detrás de la tradición asoman viejos ritos paganos del fuego y del árbol en pleno solsticio.'], 'masia-siglo-xi'],
    ['Hans Trapp', 'Alsacia', ['Un hombre rico y cruel al que la Iglesia expulsó y que se refugió en el bosque. Allí se disfrazaba de espantapájaros para atrapar niños.', 'La leyenda dice que un rayo lo mató justo antes de comerse a uno. Desde entonces vuelve en Navidad, vestido de paja, para asustar a los que se portan mal.'], 'fabrica-abandonada'],
    ['Belsnickel', 'Palatinado · Pensilvania', ['Un hombre vestido de pieles sucias, con la cara tiznada y un látigo, que aparece unas semanas antes de Navidad.', 'Lanza dulces al suelo y, cuando los niños se agachan a cogerlos, golpea a los que han sido malos. Llegó a América con los emigrantes alemanes.'], 'casa-juguetes'],
    ['La Cacería Salvaje', 'Europa del norte', ['En las noches más largas del invierno, un cortejo de jinetes espectrales cruza el cielo con perros y cuernos de caza.', 'Quien lo veía podía morir ese mismo año o ser arrastrado con ellos. Se recomendaba no salir y, sobre todo, no mirar hacia arriba.'], 'torre-salvana-metodo-estes'],
    ['La noche de Lussi', 'Suecia y Noruega · 13 de diciembre', ['Con el antiguo calendario, era la noche más larga del año. Esa noche Lussi y su cortejo, los lussiferdi, cabalgaban por los aires.', 'Si el trabajo de la casa no estaba hecho, castigaban a la familia. A los niños traviesos se los podían llevar por la chimenea.'], 'hotel-abandonado'],
    ['El Tomte', 'Escandinavia', ['Un duende pequeño y viejo que cuida la granja y a los animales desde hace siglos. Es fiel, pero orgulloso.', 'En Nochebuena hay que dejarle un cuenco de gachas con mantequilla. Si se olvida, o si se le falta al respeto, se venga: mata ganado, rompe cosas o se marcha y se lleva la buena suerte de la casa.'], 'masia-20-regreso'],
    ['Els Pastorets', 'Cataluña', ['El teatro de Navidad más antiguo de Cataluña. Los pastores intentan llegar a Belén y los diablos, con Satanàs y Lucifer a la cabeza, hacen todo lo posible por impedirlo.', 'Durante más de un siglo, el infierno ha subido cada diciembre al escenario de los teatros de barrio.'], 'pont-del-diable'],
    ['La Befana', 'Italia', ['Una anciana con escoba que vuela la noche del 5 al 6 de enero y entra por las chimeneas.', 'Se dice que los Reyes Magos le pidieron que les acompañara y no quiso. Desde entonces los busca de casa en casa y deja carbón a los niños que se han portado mal.'], 'casa-juguetes'],
    ['Olentzero', 'País Vasco y Navarra', ['Un carbonero gigante que vive en el monte y baja al pueblo en Nochebuena.', 'Hoy trae regalos, pero en las versiones más antiguas era un gigante temible, de los que se usaban para asustar a los niños para que se fueran a dormir.'], 'masia-tinajas'],
    ['Joulupukki', 'Finlandia', ['Antes de convertirse en el Papá Noel finlandés, el Joulupukki era "el macho cabrío de Yule": un hombre vestido de pieles y con cuernos.', 'No traía regalos. Iba de casa en casa exigiéndolos y asustando a los que no le daban nada.'], 'restaurante-herencia'],
    ['Las Rauhnächte', 'Alemania y Austria', ['Las noches entre Navidad y Reyes, cuando el año viejo ya se ha ido y el nuevo aún no ha llegado. Se creía que la frontera con el otro lado quedaba abierta.', 'No se debía lavar ni tender la ropa: los espíritus podían llevarse una sábana para usarla como mortaja de alguien de la casa.'], 'la-puda-psicofonias'],
    ['Cuentos de fantasmas en Nochebuena', 'Inglaterra victoriana', ['Mucho antes de Halloween, el momento de los fantasmas era la Navidad. En la Inglaterra del siglo XIX, las familias se reunían junto al fuego para contar historias de aparecidos en Nochebuena.', 'De ahí nace "Cuento de Navidad" de Charles Dickens (1843): la historia de un hombre visitado por su socio muerto y por tres espíritus.'], 'hotel-posesion'],
    ['Los Kallikantzaroi', 'Grecia y los Balcanes', ['Duendes que viven bajo tierra serrando el árbol que sostiene el mundo. Cuando están a punto de terminar, llega la Navidad y suben a la superficie.', 'Durante los doce días hasta Epifanía entran en las casas por la chimenea. Se mantiene el fuego encendido toda la noche para que no bajen.'], 'la-puda'],
    ['Los animales que hablan', 'Bretaña y otras partes de Europa', ['Se dice que a medianoche de Nochebuena los animales del establo reciben el don de la palabra.', 'Pero nadie debe escucharlos. La leyenda cuenta que quien lo intenta los oye hablar de su propia muerte.'], 'masia-20'],
    ['Velas en las tumbas', 'Finlandia', ['En Nochebuena, miles de familias finlandesas van al cementerio cuando ya ha anochecido para dejar velas encendidas a sus muertos.', 'Los cementerios nevados quedan iluminados por miles de llamas pequeñas. Es la noche en que los vivos van a buscar a los que ya no están.'], 'torre-salvana'],
    ['Nochebuena', 'Enclave Paranormal', ['La última puerta. Dice la tradición que esta es la noche en que el velo entre los dos mundos es más fino.', 'Esta noche, cuando se apague la última vela de la mesa, escucha bien. Y si oyes algo, cuéntanoslo.'], null],
  ];

  const forceOpen = params.has('adviento');
  const m = now.getMonth(), d = now.getDate();
  // Puertas disponibles: diciembre hasta el día de hoy; del 25-dic al 6-ene, todas
  let available = 0;
  if (forceOpen) available = 24;
  else if (m === 11) available = Math.min(24, d);
  else if (m === 0 && d <= 6) available = 24;
  const todayDoor = m === 11 && d <= 24 ? d : 0;

  const KEY = `adviento-${year}`;
  let opened = [];
  try { opened = JSON.parse(localStorage.getItem(KEY) || '[]'); } catch (e) {}
  const save = () => { try { localStorage.setItem(KEY, JSON.stringify(opened)); } catch (e) {} };

  // Contador de la cabecera
  const count = document.getElementById('adventCount');
  if (count) {
    const dic1 = new Date(year, 11, 1);
    const n = nightsTo(dic1);
    if (available === 0 && n > 0) count.textContent = n === 1 ? '❄ La primera puerta se abre mañana' : `❄ La primera puerta se abre en ${n} noches`;
    else if (available === 0) count.textContent = '❄ Vuelve con el próximo Adviento';
    else if (available < 24) count.textContent = `❄ ${available} de 24 puertas abiertas · ${24 - available} por abrir`;
    else count.textContent = '❄ Todas las puertas están abiertas';
  }

  const dialog = document.getElementById('legendDialog');
  const esc = s => s.replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));

  const showLegend = (i) => {
    const [titulo, origen, parrafos, rel] = L[i];
    const actions = rel
      ? `<a class="btn-vhs" href="/investigaciones/${rel}.html">▶ Del archivo: ${esc(TITULOS[rel])}</a>`
      : `<a class="btn-vhs" href="https://www.youtube.com/channel/UC5ooPVBZplLiqx4PbtVxVrw?sub_confirmation=1" target="_blank" rel="noopener">● Suscribirse al canal</a>`;
    dialog.innerHTML = `<div class="legend-inner">
      <button class="legend-close" type="button" aria-label="Cerrar">✕</button>
      <p class="osd legend-day">✦ Noche ${i + 1} de 24</p>
      <h3 class="legend-title">${esc(titulo)}</h3>
      <p class="legend-origin">${esc(origen)}</p>
      ${parrafos.map(p => `<p class="legend-text">${esc(p)}</p>`).join('')}
      <div class="legend-actions">${actions}</div>
    </div>`;
    dialog.querySelector('.legend-close').addEventListener('click', () => dialog.close());
    if (typeof dialog.showModal === 'function') dialog.showModal(); else dialog.setAttribute('open', '');
  };
  if (dialog) dialog.addEventListener('click', e => { if (e.target === dialog) dialog.close(); });

  const render = () => {
    grid.innerHTML = L.map((l, i) => {
      const n = i + 1;
      const isOpen = n <= available && opened.includes(n);
      const cls = ['door', n > available ? 'locked' : isOpen ? 'opened' : 'ready', n === todayDoor ? 'today' : ''].join(' ');
      const thumb = isOpen && l[3] ? ` style="--thumb:url('https://img.youtube.com/vi/${YT[l[3]]}/mqdefault.jpg')"` : '';
      const state = n > available ? 'Cerrada' : 'Abrir';
      const label = n > available ? `Noche ${n}, todavía cerrada` : isOpen ? `Noche ${n}: ${l[0]}` : `Abrir la puerta de la noche ${n}`;
      return `<button class="${cls}" type="button" data-n="${n}" aria-label="${esc(label)}"${thumb}>
        <span class="door-num">${n}</span><span class="door-state">${state}</span><span class="door-name">${esc(l[0])}</span></button>`;
    }).join('');
  };
  render();

  grid.addEventListener('click', e => {
    const b = e.target.closest('.door');
    if (!b) return;
    const n = +b.dataset.n;
    if (n > available) {
      b.classList.remove('shake'); void b.offsetWidth; b.classList.add('shake');
      const st = b.querySelector('.door-state');
      const dia = new Date(year, 11, n);
      const faltan = nightsTo(dia);
      st.textContent = faltan > 0 ? (faltan === 1 ? 'Mañana' : `En ${faltan} noches`) : 'Cerrada';
      return;
    }
    if (!opened.includes(n)) { opened.push(n); save(); render(); }
    showLegend(n - 1);
  });
})();
