// Portada VHS: grano de vídeo, reloj OSD y contador de cinta
(function () {
  const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  // Grano: canvas a baja resolución escalado a pantalla completa
  const canvas = document.getElementById('vhsNoise');
  if (canvas) {
    const ctx = canvas.getContext('2d');
    const W = 160, H = 90;
    canvas.width = W; canvas.height = H;
    const img = ctx.createImageData(W, H);
    const draw = () => {
      const d = img.data;
      for (let i = 0; i < d.length; i += 4) {
        const v = Math.random() * 255;
        d[i] = d[i + 1] = d[i + 2] = v;
        d[i + 3] = 255;
      }
      ctx.putImageData(img, 0, 0);
    };
    draw();
    if (!reduce) {
      let last = 0;
      const loop = t => {
        if (t - last > 80) { draw(); last = t; }
        requestAnimationFrame(loop);
      };
      requestAnimationFrame(loop);
    }
  }

  // Reloj tipo cámara: "PM 11:47"
  const clock = document.getElementById('osdClock');
  const pad = n => String(n).padStart(2, '0');
  const tickClock = () => {
    if (!clock) return;
    const d = new Date();
    const h = d.getHours();
    clock.textContent = `${h < 12 ? 'AM' : 'PM'} ${pad(h % 12 || 12)}:${pad(d.getMinutes())}`;
  };
  tickClock();
  setInterval(tickClock, 15000);

  // Contador de cinta desde que se abre la página
  const counter = document.getElementById('osdCounter');
  if (counter) {
    const start = Date.now();
    setInterval(() => {
      const s = Math.floor((Date.now() - start) / 1000);
      counter.textContent = `${Math.floor(s / 3600)}:${pad(Math.floor(s / 60) % 60)}:${pad(s % 60)}`;
    }, 1000);
  }
})();
