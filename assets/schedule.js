// Сезон 2027: фильтр программ по месяцам + название программы в заявке
(function () {
  var $$ = function (s, r) { return [].slice.call((r || document).querySelectorAll(s)); };
  var sec = document.getElementById('schedule'); if (!sec) return;
  var btns = $$('.smon', sec), progs = $$('.prog', sec), all = sec.querySelector('.sall');
  function apply(m) {
    btns.forEach(function (b) { b.setAttribute('aria-pressed', String(b.dataset.smon === m)); });
    progs.forEach(function (p) { p.hidden = m !== 'all' && p.dataset.months.split(' ').indexOf(m) < 0; if (!p.hidden) p.classList.add('in'); });
    if (all) all.hidden = m === 'all';
  }
  btns.forEach(function (b) { b.addEventListener('click', function () { apply(b.getAttribute('aria-pressed') === 'true' ? 'all' : b.dataset.smon); }); });
  if (all) all.addEventListener('click', function () { apply('all'); });
  document.addEventListener('click', function (e) {
    var a = e.target.closest && e.target.closest('[data-sched-tour]'); if (!a) return;
    var f = document.querySelector('.modal form'); if (f) f.dataset.tour = a.getAttribute('data-sched-tour');
  }, true);
})();
