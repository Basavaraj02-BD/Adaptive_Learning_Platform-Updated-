/* ═══════════════════════════════════════════
   AdaptLearn — Main JavaScript
   Utilities + Interactive Features
═══════════════════════════════════════════ */

'use strict';

/* ── TOAST SYSTEM ── */
const Toast = {
  container: null,

  init() {
    this.container = document.getElementById('toastContainer');
    if (!this.container) {
      this.container = document.createElement('div');
      this.container.className = 'toast-container-custom';
      this.container.id = 'toastContainer';
      document.body.appendChild(this.container);
    }
    // Auto-dismiss existing Django messages
    document.querySelectorAll('.toast-msg').forEach(t => {
      setTimeout(() => Toast._dismiss(t), 4500);
    });
  },

  show(message, type = 'info', duration = 4500) {
    const icons = {
      success: 'fa-check-circle',
      error:   'fa-exclamation-circle',
      warning: 'fa-exclamation-triangle',
      info:    'fa-info-circle',
    };
    const colors = {
      success: '#00e676', error: '#ff6584', warning: '#ffd700', info: '#00d4ff',
    };
    const item = document.createElement('div');
    item.className = `toast-item ${type}`;
    item.innerHTML = `
      <i class="fas ${icons[type] || icons.info}" style="color:${colors[type]};flex-shrink:0"></i>
      <span style="flex:1">${message}</span>
      <span class="toast-dismiss" onclick="Toast._dismiss(this.parentElement)">
        <i class="fas fa-times"></i>
      </span>`;
    this.container.appendChild(item);
    if (duration > 0) setTimeout(() => Toast._dismiss(item), duration);
    return item;
  },

  _dismiss(el) {
    if (!el || !el.parentElement) return;
    el.style.animation = 'slideInRight .3s ease reverse';
    setTimeout(() => el.remove(), 280);
  },
};

/* ── CSRF TOKEN HELPER ── */
function getCsrf() {
  return document.querySelector('[name=csrfmiddlewaretoken]')?.value ||
         document.cookie.split('; ').find(r => r.startsWith('csrftoken='))?.split('=')[1] || '';
}

/* ── API HELPER ── */
async function api(url, data = {}, method = 'POST') {
  try {
    const res = await fetch(url, {
      method,
      headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCsrf() },
      body: method !== 'GET' ? JSON.stringify(data) : undefined,
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } catch (err) {
    console.error('API error:', err);
    throw err;
  }
}

/* ── SIDEBAR ── */
const Sidebar = {
  el: null,
  overlay: null,

  init() {
    this.el = document.getElementById('sidebar');
    if (!this.el) return;

    // Overlay for mobile
    this.overlay = document.createElement('div');
    this.overlay.style.cssText = 'position:fixed;inset:0;background:rgba(0,0,0,.5);z-index:899;display:none';
    this.overlay.addEventListener('click', () => Sidebar.close());
    document.body.appendChild(this.overlay);

    // Keyboard shortcut: Ctrl + B
    document.addEventListener('keydown', e => {
      if ((e.ctrlKey || e.metaKey) && e.key === 'b') {
        e.preventDefault(); Sidebar.toggle();
      }
    });
  },

  toggle() { this.el?.classList.toggle('open'); this._syncOverlay(); },
  open()   { this.el?.classList.add('open');    this._syncOverlay(); },
  close()  { this.el?.classList.remove('open'); this._syncOverlay(); },
  _syncOverlay() {
    if (this.overlay) {
      this.overlay.style.display = this.el?.classList.contains('open') ? 'block' : 'none';
    }
  },
};
function toggleSidebar() { Sidebar.toggle(); }

/* ── SMOOTH COUNTER ── */
function animateCounter(el, target, duration = 1500) {
  const start = performance.now();
  const startVal = 0;
  const easing = t => t < .5 ? 2*t*t : -1+(4-2*t)*t;

  function step(timestamp) {
    const elapsed = timestamp - start;
    const progress = Math.min(elapsed / duration, 1);
    const value = Math.round(startVal + easing(progress) * (target - startVal));
    el.textContent = value.toLocaleString();
    if (progress < 1) requestAnimationFrame(step);
  }
  requestAnimationFrame(step);
}

/* ── PROGRESS BARS — animate on scroll ── */
function initProgressBars() {
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const bar = entry.target;
        const target = bar.dataset.width || bar.style.width;
        bar.style.width = '0';
        setTimeout(() => { bar.style.width = target; }, 100);
        observer.unobserve(bar);
      }
    });
  }, { threshold: .2 });

  document.querySelectorAll('.progress-glow .bar').forEach(b => {
    b.dataset.width = b.style.width;
    observer.observe(b);
  });
}

/* ── FORM VALIDATION HELPERS ── */
function validateEmail(email) {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}
function validatePassword(pwd) {
  return {
    length:  pwd.length >= 8,
    upper:   /[A-Z]/.test(pwd),
    number:  /[0-9]/.test(pwd),
    special: /[^A-Za-z0-9]/.test(pwd),
  };
}

/* ── PASSWORD STRENGTH ── */
function initPasswordStrength() {
  const inputs = document.querySelectorAll('input[name="password1"]');
  inputs.forEach(inp => {
    const bar  = inp.closest('form')?.querySelector('#strengthBar');
    const hint = inp.closest('form')?.querySelector('#strengthHint');
    if (!bar) return;
    inp.addEventListener('input', () => {
      const v = validatePassword(inp.value);
      const score = Object.values(v).filter(Boolean).length;
      const colors = ['', '#ff6584', '#ffd700', '#00d4ff', '#00e676'];
      const labels = ['', 'Weak', 'Fair', 'Good', 'Strong'];
      bar.style.width  = (score * 25) + '%';
      bar.style.background = colors[score] || '#ff6584';
      if (hint) { hint.textContent = labels[score] || ''; hint.style.color = colors[score]; }
    });
  });
}

/* ── COPY TO CLIPBOARD ── */
function copyToClipboard(text, button) {
  navigator.clipboard.writeText(text).then(() => {
    const orig = button.innerHTML;
    button.innerHTML = '<i class="fas fa-check"></i> Copied!';
    button.style.color = 'var(--green)';
    setTimeout(() => { button.innerHTML = orig; button.style.color = ''; }, 2000);
  });
}

/* ── CONFIRM DELETE ── */
function confirmDelete(url, itemName = 'this item') {
  const modal = document.createElement('div');
  modal.style.cssText = 'position:fixed;inset:0;background:rgba(0,0,0,.7);z-index:9999;display:flex;align-items:center;justify-content:center';
  modal.innerHTML = `
    <div style="background:#111827;border:1px solid rgba(255,255,255,.1);border-radius:20px;padding:2rem;max-width:380px;width:90%;text-align:center">
      <div style="font-size:2.5rem;margin-bottom:.8rem">⚠️</div>
      <h3 style="font-family:'Syne',sans-serif;margin-bottom:.5rem">Delete ${itemName}?</h3>
      <p style="color:#6b7280;font-size:.9rem;margin-bottom:1.5rem">This action cannot be undone.</p>
      <div class="d-flex gap-3 justify-content-center">
        <button onclick="this.closest('[style]').remove()" style="background:rgba(255,255,255,.08);border:1px solid rgba(255,255,255,.1);color:#e8eaf6;padding:.6rem 1.4rem;border-radius:10px;cursor:pointer;font-weight:600">Cancel</button>
        <a href="${url}" style="background:linear-gradient(135deg,#ff4757,#ff6584);border:none;color:#fff;padding:.6rem 1.4rem;border-radius:10px;cursor:pointer;font-weight:600;text-decoration:none">Delete</a>
      </div>
    </div>`;
  document.body.appendChild(modal);
  modal.addEventListener('click', e => { if (e.target === modal) modal.remove(); });
}

/* ── NUMBER FORMAT ── */
function formatNumber(n) {
  if (n >= 1e6) return (n / 1e6).toFixed(1) + 'M';
  if (n >= 1e3) return (n / 1e3).toFixed(1) + 'K';
  return n.toString();
}

/* ── COUNTDOWN TIMER ── */
function startCountdown(seconds, displayEl, onEnd) {
  let remaining = seconds;
  const interval = setInterval(() => {
    remaining--;
    const m = Math.floor(remaining / 60);
    const s = remaining % 60;
    displayEl.textContent = `${String(m).padStart(2,'0')}:${String(s).padStart(2,'0')}`;
    if (remaining <= 0) { clearInterval(interval); onEnd?.(); }
  }, 1000);
  return interval;
}

/* ── DEBOUNCE ── */
function debounce(fn, delay = 300) {
  let timer;
  return (...args) => { clearTimeout(timer); timer = setTimeout(() => fn(...args), delay); };
}

/* ── SEARCH HIGHLIGHT ── */
function highlightText(element, query) {
  if (!query) return;
  const regex = new RegExp(`(${query.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')})`, 'gi');
  element.innerHTML = element.textContent.replace(regex, '<mark style="background:rgba(108,99,255,.3);color:inherit;border-radius:3px">$1</mark>');
}

/* ── LIVE SEARCH ── */
function initLiveSearch(inputId, tableId) {
  const input = document.getElementById(inputId);
  const table = document.getElementById(tableId);
  if (!input || !table) return;

  input.addEventListener('input', debounce(() => {
    const q = input.value.toLowerCase().trim();
    table.querySelectorAll('tbody tr').forEach(row => {
      const text = row.textContent.toLowerCase();
      row.style.display = q === '' || text.includes(q) ? '' : 'none';
    });
  }));
}

/* ── NOTIFICATION MARK READ ── */
async function markNotifRead(notifId) {
  try {
    await api(`/notifications/${notifId}/read/`);
  } catch {}
}

/* ── MARK MATERIAL COMPLETE ── */
async function markComplete(materialId, btn) {
  try {
    await api(`/materials/${materialId}/complete/`);
    btn.innerHTML = '<i class="fas fa-check-circle me-1" style="color:var(--green)"></i>Done';
    btn.style.background = 'rgba(0,230,118,.12)';
    btn.style.color = 'var(--green)';
    btn.style.borderColor = 'rgba(0,230,118,.3)';
    btn.disabled = true;
    Toast.show('Material marked as complete! 🎉', 'success');
  } catch {
    Toast.show('Something went wrong. Try again.', 'error');
  }
}

/* ── DARK MODE TOGGLE (future) ── */
function toggleTheme() {
  const html = document.documentElement;
  const current = html.getAttribute('data-theme') || 'dark';
  html.setAttribute('data-theme', current === 'dark' ? 'light' : 'dark');
  localStorage.setItem('theme', html.getAttribute('data-theme'));
}

/* ── INIT ── */
document.addEventListener('DOMContentLoaded', () => {
  Toast.init();
  Sidebar.init();
  initProgressBars();
  initPasswordStrength();

  // Animate stat counters
  document.querySelectorAll('.stat-number[data-count]').forEach(el => {
    animateCounter(el, parseInt(el.dataset.count, 10));
  });

  // Active sidebar link highlight
  const path = window.location.pathname;
  document.querySelectorAll('.sidebar-link').forEach(link => {
    if (link.getAttribute('href') === path) link.classList.add('active');
  });

  // Live search tables (if present)
  initLiveSearch('tableSearch', 'dataTable');

  // Lazy-load images
  if ('IntersectionObserver' in window) {
    const imgObserver = new IntersectionObserver(entries => {
      entries.forEach(e => {
        if (e.isIntersecting) {
          const img = e.target;
          if (img.dataset.src) { img.src = img.dataset.src; delete img.dataset.src; }
          imgObserver.unobserve(img);
        }
      });
    });
    document.querySelectorAll('img[data-src]').forEach(img => imgObserver.observe(img));
  }
});
