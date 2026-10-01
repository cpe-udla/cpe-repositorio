(function(){
  var i18n = document.body.dataset;
  var menuOpenLabel = i18n.menuOpen || 'Menú';
  var menuCloseLabel = i18n.menuClose || 'Cerrar';
  var countTemplate = i18n.pubCountTemplate || '{n} de {total} publicaciones';
  var btn = document.getElementById('menuToggle');
  if(btn){
    btn.addEventListener('click', function(){
      var open = document.body.classList.toggle('menu-open');
      btn.setAttribute('aria-expanded', open ? 'true' : 'false');
      btn.textContent = open ? menuCloseLabel : menuOpenLabel;
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
      if(count) count.textContent = countTemplate.replace('{n}', visible).replace('{total}', total);
    }
    q.addEventListener('input', update);
    update();
  }
})();

/* CLACSO: mención de membresía plena en el pie de cada página */
(function () {
  var footer = document.querySelector('footer.footer');
  if (!footer || footer.querySelector('.clacso-badge')) return;
  var url = 'https://www.clacso.org/';
  var a = '<a href="' + url + '" target="_blank" rel="noopener">';
  var T = {
    es: 'El CPE es miembro pleno del ' + a + 'Consejo Latinoamericano de Ciencias Sociales (CLACSO)</a>.',
    en: 'CPE is a full member of the ' + a + 'Latin American Council of Social Sciences (CLACSO)</a>.',
    fr: 'Le CPE est membre à part entière du ' + a + 'Conseil latino-américain des sciences sociales (CLACSO)</a>.',
    pt: 'O CPE é membro pleno do ' + a + 'Conselho Latino-Americano de Ciências Sociais (CLACSO)</a>.',
    zh: 'CPE 是' + a + '拉丁美洲社会科学理事会（CLACSO）</a>的正式成员。',
    ru: 'CPE является полноправным членом ' + a + 'Латиноамериканского совета по социальным наукам (CLACSO)</a>.',
    ar: 'مركز CPE عضو كامل العضوية في ' + a + 'المجلس الأمريكي اللاتيني للعلوم الاجتماعية (CLACSO)</a>.'
  };
  var lang = (document.documentElement.lang || 'es').slice(0, 2);
  var script = document.querySelector('script[src$="assets/site.js"]');
  var logo = script ? script.getAttribute('src').replace(/site\.js$/, 'clacso-logo.svg') : 'assets/clacso-logo.svg';
  var div = document.createElement('div');
  div.className = 'clacso-badge';
  div.innerHTML = a + '<img src="' + logo + '" alt="Logo CLACSO" height="40"></a><p>' + (T[lang] || T.es) + '</p>';
  footer.insertBefore(div, footer.firstChild);
})();
