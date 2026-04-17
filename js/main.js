// Nav scroll effect
const nav = document.getElementById('nav');
window.addEventListener('scroll', () => {
  nav.classList.toggle('scrolled', window.scrollY > 40);
});

// Mobile nav toggle
const navToggle = document.getElementById('navToggle');
const navLinks  = document.querySelector('.nav-links');
navToggle.addEventListener('click', () => navLinks.classList.toggle('open'));
document.querySelectorAll('.nav-links a').forEach(a => {
  a.addEventListener('click', () => navLinks.classList.remove('open'));
});

// Particles
const container = document.getElementById('particles');
const COUNT = 35;
for (let i = 0; i < COUNT; i++) {
  const p = document.createElement('div');
  p.className = 'particle';
  const size = Math.random() * 3 + 1;
  p.style.cssText = `
    left: ${Math.random() * 100}%;
    width: ${size}px;
    height: ${size}px;
    animation-duration: ${6 + Math.random() * 14}s;
    animation-delay: ${Math.random() * 10}s;
    opacity: ${Math.random() * 0.6 + 0.2};
  `;
  container.appendChild(p);
}

// Form submit
document.getElementById('reportForm').addEventListener('submit', e => {
  e.preventDefault();
  const btn = e.target.querySelector('button[type=submit]');
  btn.textContent = 'Enviando...';
  btn.disabled = true;
  setTimeout(() => {
    btn.textContent = '✓ Reporte recibido';
    btn.style.background = '#10b981';
    e.target.reset();
  }, 1200);
});

// Intersection observer for fade-in
const observer = new IntersectionObserver(entries => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      entry.target.style.opacity = '1';
      entry.target.style.transform = 'translateY(0)';
    }
  });
}, { threshold: 0.1 });

document.querySelectorAll('.case-card, .cat-card, .location-card, .timeline-item').forEach(el => {
  el.style.opacity = '0';
  el.style.transform = 'translateY(20px)';
  el.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
  observer.observe(el);
});
