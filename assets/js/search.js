(function () {
  var input = document.getElementById('word-search-input');
  var results = document.getElementById('word-search-results');
  var count = document.getElementById('word-search-count');
  if (!input || !results) return;

  var words = null;
  var LIMIT = 500;

  function load(cb) {
    if (words) { cb(); return; }
    fetch(window.WORDS_URL)
      .then(function (r) { return r.json(); })
      .then(function (data) { words = data; cb(); })
      .catch(function () { results.innerHTML = '<p>Failed to load word data.</p>'; });
  }

  function escape(s) {
    return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  }

  function render(list, total) {
    var shown = Math.min(list.length, LIMIT);
    count.textContent = shown + ' / ' + total + (list.length > LIMIT ? ' (showing first ' + LIMIT + ')' : '');
    if (!list.length) {
      results.innerHTML = '<p>No results.</p>';
      return;
    }
    var rows = list.slice(0, LIMIT).map(function (w) {
      return '<tr><td>' + escape(w.word) + '</td><td>' + escape(w.ips) + '</td><td>' + escape(w.ipsm) + '</td><td>' + escape(w.meaning).replace(/\n/g, '<br>') + '</td></tr>';
    }).join('');
    results.innerHTML = '<table class="word-table"><thead><tr><th>Word</th><th>IPS</th><th>IPSM</th><th>Meaning</th></tr></thead><tbody>' + rows + '</tbody></table>';
  }

  function filter(q) {
    if (!q) return words.slice();
    q = q.toLowerCase();
    return words.filter(function (w) {
      return (w.word || '').toLowerCase().indexOf(q) !== -1;
    });
  }

  input.addEventListener('input', function () {
    load(function () {
      var q = input.value.trim();
      var list = filter(q);
      render(list, words.length);
    });
  });

  load(function () { render(words.slice(0, LIMIT), words.length); });
})();
