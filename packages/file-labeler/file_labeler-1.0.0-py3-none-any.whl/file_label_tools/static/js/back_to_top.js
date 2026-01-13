// 全站通用：回到顶部按钮

(function initBackToTop() {
  const BTN_ID = 'backToTopBtn';

  function ensureButton() {
    let btn = document.getElementById(BTN_ID);
    if (btn) return btn;

    btn = document.createElement('button');
    btn.id = BTN_ID;
    btn.className = 'back-to-top';
    btn.type = 'button';
    btn.title = '回到顶部';
    btn.setAttribute('aria-label', '回到顶部');
    btn.innerHTML = '↑';
    document.body.appendChild(btn);
    return btn;
  }

  function updateVisibility(btn) {
    const show = (window.scrollY || document.documentElement.scrollTop || 0) > 200;
    btn.classList.toggle('show', show);
  }

  document.addEventListener('DOMContentLoaded', () => {
    const btn = ensureButton();

    btn.addEventListener('click', () => {
      try {
        window.scrollTo({ top: 0, behavior: 'smooth' });
      } catch (e) {
        window.scrollTo(0, 0);
      }
    });

    updateVisibility(btn);
    window.addEventListener('scroll', () => updateVisibility(btn), { passive: true });
  });
})();


