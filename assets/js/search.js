(function () {
  var input = document.getElementById('word-search-input');
  var results = document.getElementById('word-search-results');
  var count = document.getElementById('word-search-count');
  if (!input || !results) return;

  var words = null;
  var PAGE_SIZE = 200;   // 每页渲染条数(避免一次画几千行卡顿)
  var page = 1;          // 当前页
  var currentList = [];  // 当前(过滤后)列表,翻页时复用,不必重新过滤

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

  function filter(q) {
    if (!q) return words.slice();
    q = q.toLowerCase();
    return words.filter(function (w) {
      return (w.word || '').toLowerCase().indexOf(q) !== -1;
    });
  }

  function totalPages() {
    return Math.max(1, Math.ceil(currentList.length / PAGE_SIZE));
  }

  function render() {
    var total = currentList.length;
    var pages = totalPages();
    if (page > pages) page = pages;
    var start = (page - 1) * PAGE_SIZE;
    var end = Math.min(start + PAGE_SIZE, total);

    count.textContent = total
      ? ('Showing ' + (start + 1) + '–' + end + ' of ' + total)
      : '';

    if (!total) {
      results.innerHTML = '<p>No results.</p>';
      return;
    }

    var rowsHtml = currentList.slice(start, end).map(function (w) {
      return '<tr><td>' + escape(w.word) + '</td><td>' + escape(w.ips) + '</td><td>' + escape(w.ipsm) + '</td><td>' + escape(w.meaning).replace(/\n/g, '<br>') + '</td></tr>';
    }).join('');

    var prevDis = page <= 1 ? ' disabled' : '';
    var nextDis = page >= pages ? ' disabled' : '';
    var pager = '<div class="word-pager">' +
      '<button type="button" data-go="first"' + prevDis + '>« First</button>' +
      '<button type="button" data-go="prev"' + prevDis + '>‹ Prev</button>' +
      '<span class="word-pager-info">Page ' + page + ' / ' + pages + '</span>' +
      '<button type="button" data-go="next"' + nextDis + '>Next ›</button>' +
      '<button type="button" data-go="last"' + nextDis + '>Last »</button>' +
      '</div>';

    results.innerHTML = pager + '<table class="word-table"><thead><tr><th>Word</th><th>IPS</th><th>IPSM</th><th>Meaning</th></tr></thead><tbody>' + rowsHtml + '</tbody></table>';
  }

  function goTo(p) {
    var pages = totalPages();
    if (p < 1) p = 1;
    if (p > pages) p = pages;
    if (p === page) return;
    page = p;
    render();
  }

  // 分页按钮(事件委托)
  results.addEventListener('click', function (e) {
    var btn = e.target.closest('[data-go]');
    if (!btn || btn.disabled) return;
    var act = btn.getAttribute('data-go');
    if (act === 'first') goTo(1);
    else if (act === 'prev') goTo(page - 1);
    else if (act === 'next') goTo(page + 1);
    else if (act === 'last') goTo(totalPages());
  });

  input.addEventListener('input', function () {
    load(function () {
      currentList = filter(input.value.trim());
      page = 1;
      render();
    });
  });

  load(function () {
    currentList = words.slice();
    page = 1;
    render();
  });
})();
