// main.js — small UI helpers for redesigned frontend
document.addEventListener('DOMContentLoaded', () => {
  const btn = document.getElementById('sidebarToggle');
  const sidebar = document.getElementById('sidebar');
  const search = document.getElementById('globalSearch');

  // Sidebar collapse (mainly for smaller screens)
  if (btn && sidebar) {
    btn.addEventListener('click', () => {
      sidebar.classList.toggle('collapsed');
    });
  }

  // Simple "search" that goes to Teams on Enter
  if (search) {
    search.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') {
        const q = search.value.trim();
        if (!q) return;
        window.location.href = "/teams";
      }
    });
  }

  // Highlight current nav item based on URL
  const currentPath = window.location.pathname;
  document.querySelectorAll('.nav-item').forEach(link => {
    const href = link.getAttribute('href');
    if (href === currentPath) {
      link.classList.add('active');
    }
  });

  // Small fade-in for the page
  setTimeout(() => document.body.classList.add('page-ready'), 80);
});

// Theme & Font Picker logic (optional – safe no-op if controls are not present)
(function () {
  const themeBtn = document.getElementById('themeBtn');
  const themePanel = document.getElementById('themePanel');
  const bgSelect = document.getElementById('bgSelect');
  const fontSelect = document.getElementById('fontSelect');
  const accentSelect = document.getElementById('accentSelect');
  const applyBtn = document.getElementById('applyTheme');
  const resetBtn = document.getElementById('resetTheme');
  const ROOT = document.documentElement;
  const LSTORE_KEY = 'slm_ui_prefs_v1';

  // If there is no theme button/panel on this page, do nothing
  if (!themeBtn || !themePanel) return;

  themeBtn.addEventListener('click', () => {
    const open = themePanel.getAttribute('aria-hidden') === 'false';
    themePanel.setAttribute('aria-hidden', open ? 'true' : 'false');
  });

  document.addEventListener('click', (e) => {
    if (!themePanel.contains(e.target) && e.target !== themeBtn) {
      themePanel.setAttribute('aria-hidden', 'true');
    }
  });

  function loadPrefs() {
    try {
      const raw = localStorage.getItem(LSTORE_KEY);
      if (!raw) return null;
      return JSON.parse(raw);
    } catch {
      return null;
    }
  }

  function savePrefs(prefs) {
    localStorage.setItem(LSTORE_KEY, JSON.stringify(prefs));
  }

  function applyPrefs(prefs) {
    if (!prefs) return;

    const layout = document.querySelector('.app-layout') || document.body;
    layout.classList.remove('bg-default','bg-dark','bg-iris','bg-sand','bg-pattern');
    if (prefs.bg) layout.classList.add(prefs.bg);

    document.documentElement.classList.remove(
      'font-system','font-inter','font-sf','font-roboto','font-serif'
    );
    if (prefs.font) {
      document.documentElement.classList.add(prefs.font);
      if (prefs.font === 'font-inter') loadGoogleFont('Inter');
      if (prefs.font === 'font-roboto') loadGoogleFont('Roboto');
    }

    if (prefs.accent) {
      ROOT.style.setProperty('--user-accent', prefs.accent);
      ROOT.classList.add('app-accent');
    } else {
      ROOT.style.removeProperty('--user-accent');
      ROOT.classList.remove('app-accent');
    }
  }

  function loadGoogleFont(name) {
    const id = 'gf-' + name.toLowerCase();
    if (document.getElementById(id)) return;
    const link = document.createElement('link');
    link.id = id;
    link.rel = 'stylesheet';
    link.href = `https://fonts.googleapis.com/css2?family=${encodeURIComponent(name)}:wght@300;400;600;700&display=swap`;
    document.head.appendChild(link);
  }

  applyBtn.addEventListener('click', () => {
    const prefs = {
      bg: bgSelect.value,
      font: (fontSelect.value === 'system')
        ? 'font-system'
        : (fontSelect.value === 'inter'
          ? 'font-inter'
          : (fontSelect.value === 'sf-pro'
            ? 'font-sf'
            : (fontSelect.value === 'roboto'
              ? 'font-roboto'
              : 'font-serif'))),
      accent: accentSelect.value
    };
    applyPrefs(prefs);
    savePrefs(prefs);
    themePanel.setAttribute('aria-hidden','true');
  });

  resetBtn.addEventListener('click', () => {
    localStorage.removeItem(LSTORE_KEY);
    const defaultPrefs = {
      bg: 'bg-default',
      font: 'font-system',
      accent: '#0a84ff'
    };
    applyPrefs(defaultPrefs);
    bgSelect.value = defaultPrefs.bg;
    fontSelect.value = 'system';
    accentSelect.value = defaultPrefs.accent;
    themePanel.setAttribute('aria-hidden','true');
  });

  const saved = loadPrefs();
  if (saved) {
    bgSelect.value = saved.bg || 'bg-default';

    if (saved.font === 'font-inter') fontSelect.value = 'inter';
    else if (saved.font === 'font-roboto') fontSelect.value = 'roboto';
    else if (saved.font === 'font-sf') fontSelect.value = 'sf-pro';
    else if (saved.font === 'font-serif') fontSelect.value = 'serif';
    else fontSelect.value = 'system';

    accentSelect.value = saved.accent || '#0a84ff';
    applyPrefs(saved);
  } else {
    bgSelect.value = 'bg-default';
    fontSelect.value = 'system';
    accentSelect.value = '#0a84ff';
  }
})();

// confirmDeleteTeam(formElement, teamName)
function confirmDeleteTeam(formElement, teamName) {
  return confirm(`Delete team "${teamName}"? This action cannot be undone.`);
}

// auto-hide flash messages
setTimeout(() => {
  document.querySelectorAll('.flash').forEach(el => {
    el.style.transition = 'opacity .4s ease';
    el.style.opacity = '0';
    setTimeout(() => el.remove(), 400);
  });
}, 3500);