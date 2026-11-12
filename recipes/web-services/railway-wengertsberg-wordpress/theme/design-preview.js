(() => {
  'use strict';
  if (!document.body.classList.contains('design-preview')) return;
  const bar = document.querySelector('.preview-reviewbar');
  if (!bar) { document.body.classList.remove('design-preview'); return; }
  const current = new URL(location.href);
  const design = document.querySelector('#preview-design-panel');
  const original = document.querySelector('#preview-original-panel');
  const frame = original?.querySelector('iframe');
  const viewButtons = [...document.querySelectorAll('[data-review-view]')];
  const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
  document.documentElement.classList.add('has-design-review');
  const measureBar = () => document.documentElement.style.setProperty('--preview-reviewbar-height', `${Math.ceil(bar.getBoundingClientRect().height)}px`);
  if ('ResizeObserver' in window) new ResizeObserver(measureBar).observe(bar);
  window.addEventListener('resize', measureBar);
  measureBar();

  // Keep review navigation and its embedded comparison out of analytics views.
  document.querySelectorAll('a[href]').forEach(link => {
    if (link.hasAttribute('data-original-view')) return;
    const next = new URL(link.href, current);
    if (next.origin === current.origin && next.pathname === current.pathname && (next.hash || link.classList.contains('brand'))) {
      next.searchParams.set('entwurf', '2'); link.href = next.href;
    }
  });
  frame?.addEventListener('load', () => {
    if (!frame.getAttribute('src')) return;
    try {
      frame.contentDocument?.querySelectorAll('a[href]').forEach(link => {
        const next = new URL(link.href, current);
        if (next.origin === current.origin && !/^\/(wp-admin|wp-login\.php|wp-json)(\/|$)/.test(next.pathname)) {
          next.searchParams.set('vergleich', '1'); link.href = next.href;
        }
      });
    } catch { /* The normal live-page link remains available. */ }
  });
  const setView = (view, keepPosition = false) => {
    if (!design || !original || !frame) return;
    const showOriginal = view === 'original';
    design.hidden = showOriginal; original.hidden = !showOriginal;
    document.body.classList.toggle('review-view-original', showOriginal);
    viewButtons.forEach(button => button.setAttribute('aria-pressed', String(button.dataset.reviewView === view)));
    if (showOriginal) {
      const url = new URL(frame.dataset.originalSrc, current);
      url.hash = location.hash;
      if (url.origin === current.origin && frame.getAttribute('src') !== url.href) frame.src = url.href;
    }
    if (!keepPosition) window.scrollTo({ top: 0, behavior: 'instant' });
  };
  viewButtons.forEach(button => button.addEventListener('click', () => setView(button.dataset.reviewView)));

  const triggers = new WeakMap();
  const openDialog = (id, trigger) => {
    const dialog = document.querySelector(id);
    if (!dialog) return;
    triggers.set(dialog, trigger);
    document.querySelectorAll('dialog[open]').forEach(other => other.close());
    dialog.showModal();
  };
  [['[data-preview-notes]', '#preview-notes'], ['[data-preview-cases]', '#preview-cases'], ['[data-preview-consent]', '#preview-consent']].forEach(([selector, id]) => {
    document.querySelector(selector)?.addEventListener('click', event => openDialog(id, event.currentTarget));
  });
  document.querySelector('[data-open-cases]')?.addEventListener('click', () => openDialog('#preview-cases', document.querySelector('[data-preview-cases]')));
  document.querySelectorAll('.preview-dialog').forEach(dialog => {
    dialog.querySelector('[data-close-preview]')?.addEventListener('click', () => dialog.close());
    dialog.addEventListener('click', event => {
      const rect = dialog.getBoundingClientRect();
      if (event.target === dialog && (event.clientX < rect.left || event.clientX > rect.right || event.clientY < rect.top || event.clientY > rect.bottom)) dialog.close();
    });
    dialog.addEventListener('close', () => {
      if (!document.querySelector('dialog[open]')) triggers.get(dialog)?.focus();
    });
  });
  document.querySelectorAll('[data-review-jump]').forEach(button => button.addEventListener('click', () => {
    const dialog = button.closest('dialog');
    if (dialog) { triggers.delete(dialog); dialog.close(); }
    setView('design', true);
    const target = document.querySelector(button.dataset.reviewJump);
    if (target) {
      const destination = new URL(location.href);
      destination.hash = button.dataset.reviewJump;
      history.replaceState(null, '', destination.href);
      target.setAttribute('tabindex', '-1');
      target.scrollIntoView({ behavior: reducedMotion.matches ? 'auto' : 'smooth', block: 'start' });
      target.focus({ preventScroll: true });
    }
  }));

  const logoDemo = document.querySelector('[data-logo-demo]');
  const pause = document.querySelector('[data-logo-pause]');
  document.querySelectorAll('[data-logo-mode]').forEach(button => button.addEventListener('click', () => {
    if (!logoDemo || !pause) return;
    logoDemo.dataset.mode = button.dataset.logoMode;
    document.querySelectorAll('[data-logo-mode]').forEach(other => other.setAttribute('aria-pressed', String(other === button)));
    pause.hidden = button.dataset.logoMode !== 'band' || reducedMotion.matches;
  }));
  pause?.addEventListener('click', () => {
    const paused = logoDemo.dataset.paused !== 'true';
    logoDemo.dataset.paused = String(paused);
    pause.setAttribute('aria-pressed', String(paused));
    pause.textContent = paused ? 'Bewegung fortsetzen' : 'Bewegung pausieren';
  });
  reducedMotion.addEventListener('change', () => { if (pause) pause.hidden = logoDemo?.dataset.mode !== 'band' || reducedMotion.matches; });
})();
