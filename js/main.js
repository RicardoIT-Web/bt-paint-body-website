(function () {
  var MAX_FILES = 8, MAX_MB = 10;

  document.getElementById('year').textContent = new Date().getFullYear();

  // Mobile menu
  var toggle = document.querySelector('.nav-toggle');
  var nav = document.getElementById('nav');
  function setMenu(open) {
    nav.classList.toggle('open', open);
    toggle.setAttribute('aria-expanded', String(open));
    toggle.setAttribute('aria-label', open ? 'Fechar menu' : 'Abrir menu');
  }
  toggle.addEventListener('click', function () { setMenu(!nav.classList.contains('open')); });
  nav.addEventListener('click', function (e) { if (e.target.tagName === 'A') setMenu(false); });

  // Photo picker with thumbnails
  var input = document.getElementById('photos');
  var list = document.getElementById('previews');
  var drop = document.getElementById('drop');
  var msg = document.getElementById('form-msg');
  var files = [];

  function say(text, cls) { msg.textContent = text; msg.className = 'form-msg ' + (cls || ''); }

  function sync() {
    var dt = new DataTransfer();
    files.forEach(function (f) { dt.items.add(f); });
    input.files = dt.files;
    list.innerHTML = '';
    files.forEach(function (f, i) {
      var li = document.createElement('li');
      var img = document.createElement('img');
      img.alt = 'Fotografia ' + (i + 1);
      img.src = URL.createObjectURL(f);
      img.onload = function () { URL.revokeObjectURL(img.src); };
      var b = document.createElement('button');
      b.type = 'button'; b.textContent = '×'; b.setAttribute('aria-label', 'Remover fotografia ' + (i + 1));
      b.addEventListener('click', function () { files.splice(i, 1); sync(); });
      li.appendChild(img); li.appendChild(b); list.appendChild(li);
    });
  }

  function addFiles(incoming) {
    var problems = [];
    Array.prototype.forEach.call(incoming, function (f) {
      if (!/^image\//.test(f.type)) { problems.push(f.name + ' não é uma imagem.'); return; }
      if (f.size > MAX_MB * 1024 * 1024) { problems.push(f.name + ' excede ' + MAX_MB + ' MB.'); return; }
      if (files.length >= MAX_FILES) { problems.push('Máximo de ' + MAX_FILES + ' fotografias.'); return; }
      files.push(f);
    });
    sync();
    say(problems.length ? problems[0] : '', problems.length ? 'error' : '');
  }

  input.addEventListener('change', function () { addFiles(input.files); });
  ['dragover', 'dragenter'].forEach(function (ev) {
    drop.addEventListener(ev, function (e) { e.preventDefault(); drop.classList.add('over'); });
  });
  ['dragleave', 'drop'].forEach(function (ev) {
    drop.addEventListener(ev, function () { drop.classList.remove('over'); });
  });
  drop.addEventListener('drop', function (e) { e.preventDefault(); addFiles(e.dataTransfer.files); });

  // Submit via fetch so the page stays put
  var form = document.getElementById('quote-form');
  form.addEventListener('submit', function (e) {
    e.preventDefault();
    if (!form.checkValidity()) { form.reportValidity(); return; }
    if (form.action.indexOf('YOUR_FORM_ID') !== -1) {
      say('Formulário em modo de demonstração: ainda não está ligado a um serviço de envio.', 'error');
      return;
    }
    var btn = form.querySelector('button[type=submit]');
    btn.disabled = true; say('A enviar…');
    fetch(form.action, { method: 'POST', body: new FormData(form), headers: { Accept: 'application/json' } })
      .then(function (r) {
        if (!r.ok) throw new Error();
        form.reset(); files = []; sync();
        say('Pedido enviado! Entraremos em contacto em breve.', 'ok');
      })
      .catch(function () { say('Não foi possível enviar. Tente novamente ou ligue-nos.', 'error'); })
      .then(function () { btn.disabled = false; });
  });
})();
