// Desktop auto-scale: the layout is fluid up to 1600px, and beyond that the whole page scales
// proportionally, so a 4K monitor shows the same composition instead of a small centered column.
(function () {
  var base = 1600;
  function apply() {
    var w = window.innerWidth, z = (w > 1025 && w > base) ? Math.min(w / base, 2.4) : 1;
    document.documentElement.style.setProperty('--z', z.toFixed(3));
    document.body.style.zoom = z === 1 ? '' : z;
  }
  apply(); addEventListener('resize', apply);
})();
