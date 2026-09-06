/* Progressive enhancement: all projects remain readable without JavaScript. */
(() => {
  const menu = document.getElementById('navPanelToggle');
  const close = document.querySelector('#navPanel .close');
  const chinese = document.documentElement.lang === 'zh-CN';
  if (menu) menu.textContent = chinese ? '菜单' : 'Menu';
  if (close) close.setAttribute('aria-label', chinese ? '关闭菜单' : 'Close menu');
  const filters = document.querySelector('.filters');
  if (!filters) return;
  const buttons = [...filters.querySelectorAll('button')];
  const groups = [...document.querySelectorAll('[data-group]')];
  const status = document.querySelector('.filter-status');
  filters.hidden = false;
  status.hidden = false;
  function select(value) {
    if (!buttons.some(button => button.dataset.filter === value)) value = 'all';
    buttons.forEach(button => button.setAttribute('aria-pressed', String(button.dataset.filter === value)));
    let count = 0;
    groups.forEach(group => {
      group.hidden = value !== 'all' && group.dataset.group !== value;
      if (!group.hidden) count += group.querySelectorAll('article').length;
    });
    status.textContent = status.dataset.template.replace('{count}', count);
  }
  filters.addEventListener('click', event => {
    const button = event.target.closest('button');
    if (!button) return;
    select(button.dataset.filter);
  });
  // Legacy URLs may point to a group or project; never hide that destination.
  window.addEventListener('hashchange', () => select('all'));
  select('all');
})();
