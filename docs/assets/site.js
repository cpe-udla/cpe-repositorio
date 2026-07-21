// menú móvil + buscador de publicaciones
(function(){
  var btn = document.getElementById('menuToggle');
  if(btn){
    btn.addEventListener('click', function(){
      var open = document.body.classList.toggle('menu-open');
      btn.setAttribute('aria-expanded', open ? 'true' : 'false');
      btn.textContent = open ? 'Cerrar' : 'Menú';
    });
  }
  var q = document.getElementById('pubSearch');
  if(q){
    var pubs = Array.prototype.slice.call(document.querySelectorAll('.pub'));
    var blocks = Array.prototype.slice.call(document.querySelectorAll('.year-block'));
    var count = document.getElementById('pubCount');
    var total = pubs.length;
    function norm(s){
      return s.toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g,'');
    }
    function update(){
      var term = norm(q.value.trim());
      var visible = 0;
      pubs.forEach(function(p){
        var hit = !term || norm(p.textContent).indexOf(term) !== -1;
        p.classList.toggle('hidden', !hit);
        if(hit) visible++;
      });
      blocks.forEach(function(b){
        var any = b.querySelector('.pub:not(.hidden)');
        b.classList.toggle('hidden', !any);
      });
      if(count) count.textContent = visible + ' de ' + total + ' publicaciones';
    }
    q.addEventListener('input', update);
    update();
  }
})();
