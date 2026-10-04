// Sala de vigilancia: orden, "cargar más" y reproductor de Shorts
(function () {
  const dataEl = document.getElementById('shortsData');
  const grid = document.getElementById('camGrid');
  if (!dataEl || !grid) return;

  const PAGE = 24;
  const all = JSON.parse(dataEl.textContent).map(([id, titulo, vistas], i, arr) => ({
    id, titulo, vistas, num: arr.length - i,
  }));
  const orders = {
    recientes: all,
    vistos: [...all].sort((a, b) => b.vistas - a.vistas),
  };
  let list = orders.recientes;
  let shown = Number(dataEl.dataset.inicial) || PAGE;

  const moreWrap = document.getElementById('camMore');
  const moreBtn = moreWrap.querySelector('button');
  const status = document.getElementById('camStatus');

  const esc = s => s.replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
  const fmtViews = n => {
    if (n < 1000) return String(n);
    const [v, suf] = n < 1e6 ? [n / 1e3, 'K'] : [n / 1e6, 'M'];
    const txt = v < 100 ? v.toFixed(1).replace(/\.0$/, '') : v.toFixed(0);
    return txt.replace('.', ',') + suf;
  };
  const pad = n => String(n).padStart(3, '0');

  const card = s => `
        <a class="cam" href="https://www.youtube.com/shorts/${s.id}" data-id="${s.id}" target="_blank" rel="noopener">
          <div class="cam-screen">
            <img src="https://i.ytimg.com/vi/${s.id}/oar2.jpg" alt="" loading="lazy" width="270" height="480" />
            <span class="osd tape-osd tl">Cam ${pad(s.num)}</span>
            <span class="osd tape-osd tr">● Rec</span>
            <span class="osd tape-osd bl">▶ Play</span>
            <span class="osd tape-osd br">${fmtViews(s.vistas)}</span>
            <span class="cam-play" aria-hidden="true">▶</span>
          </div>
          <p class="cam-title">${esc(s.titulo)}</p>
        </a>`;

  const updateStatus = () => {
    moreWrap.hidden = shown >= list.length;
    status.textContent = `${Math.min(shown, list.length)} / ${list.length} cámaras`;
  };

  const render = (from = 0) => {
    const html = list.slice(from, shown).map(card).join('');
    if (from === 0) grid.innerHTML = html;
    else grid.insertAdjacentHTML('beforeend', html);
    updateStatus();
  };

  moreBtn.addEventListener('click', () => {
    const from = shown;
    shown += PAGE;
    render(from);
  });

  document.querySelectorAll('.vt-btn[data-sort]').forEach(btn => btn.addEventListener('click', () => {
    if (orders[btn.dataset.sort] === list) return;
    list = orders[btn.dataset.sort];
    shown = PAGE;
    document.querySelectorAll('.vt-btn[data-sort]').forEach(b =>
      b.setAttribute('aria-pressed', String(b === btn)));
    render();
  }));

  updateStatus();

  // --- Reproductor ---
  const modal = document.getElementById('camModal');
  if (!modal || typeof modal.showModal !== 'function') return;   // sin <dialog>: los enlaces van a YouTube
  const player = document.getElementById('camPlayer');
  const numEl = document.getElementById('camModalNum');
  const viewsEl = document.getElementById('camModalViews');
  const ytEl = document.getElementById('camModalYt');
  const titleEl = document.getElementById('camModalTitle');
  const prev = modal.querySelector('.cam-nav.prev');
  const next = modal.querySelector('.cam-nav.next');
  let current = -1;
  let opener = null;

  const play = idx => {
    current = idx;
    const s = list[idx];
    player.src = `https://www.youtube.com/embed/${s.id}?autoplay=1&rel=0&playsinline=1`;
    numEl.textContent = `Cam ${pad(s.num)}`;
    viewsEl.textContent = `${fmtViews(s.vistas)} vistas`;
    ytEl.href = `https://www.youtube.com/shorts/${s.id}`;
    titleEl.textContent = s.titulo;
    prev.disabled = idx === 0;
    next.disabled = idx === list.length - 1;
  };

  grid.addEventListener('click', e => {
    const a = e.target.closest('a.cam');
    if (!a || e.metaKey || e.ctrlKey || e.shiftKey) return;
    const idx = list.findIndex(s => s.id === a.dataset.id);
    if (idx < 0) return;
    e.preventDefault();
    opener = a;
    play(idx);
    modal.showModal();
  });

  prev.addEventListener('click', () => current > 0 && play(current - 1));
  next.addEventListener('click', () => current < list.length - 1 && play(current + 1));
  modal.querySelector('.cam-close').addEventListener('click', () => modal.close());
  modal.addEventListener('click', e => {
    if (e.target === modal || e.target.classList.contains('cam-modal-inner')) modal.close();
  });
  modal.addEventListener('keydown', e => {
    if (e.key === 'ArrowLeft') prev.click();
    if (e.key === 'ArrowRight') next.click();
  });
  modal.addEventListener('close', () => {
    player.src = 'about:blank';
    if (opener) opener.focus();
  });
})();
