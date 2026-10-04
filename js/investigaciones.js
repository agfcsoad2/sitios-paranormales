// Videoteca: filtros por año y tipo
(function () {
  const buttons = document.querySelectorAll('.vt-btn[data-filter]');
  const tapes = document.querySelectorAll('.vt-tape');
  const years = document.querySelectorAll('.vt-year');
  const empty = document.getElementById('vtEmpty');

  const apply = filter => {
    const [kind, value] = filter.split(':');
    tapes.forEach(t => {
      t.hidden = kind !== 'all' && t.dataset[kind] !== value;
    });
    let any = false;
    years.forEach(y => {
      const visible = y.querySelector('.vt-tape:not([hidden])');
      y.hidden = !visible;
      if (visible) any = true;
    });
    if (empty) empty.hidden = any;
    buttons.forEach(b => b.setAttribute('aria-pressed', String(b.dataset.filter === filter)));
  };

  buttons.forEach(b => b.addEventListener('click', () => {
    apply(b.dataset.filter);
    const url = b.dataset.filter === 'all' ? location.pathname : `#${b.dataset.filter.replace(':', '-')}`;
    history.replaceState(null, '', url);
  }));

  // Permite enlazar a un filtro: /investigaciones/#year-2023, #tag-leyenda
  const fromHash = () => {
    const m = location.hash.match(/^#(year|tag)-(.+)$/);
    apply(m ? `${m[1]}:${decodeURIComponent(m[2])}` : 'all');
  };
  window.addEventListener('hashchange', fromHash);
  if (location.hash) fromHash();
})();
