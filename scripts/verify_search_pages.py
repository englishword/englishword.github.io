#!/usr/bin/env python3
"""Verify all built Search data and Words tables against the installed lexicon."""
import argparse
from html import unescape
import json
from pathlib import Path
import re
import string
from urllib.parse import parse_qs, urlsplit
from lingose_data import SITE, load_entries
from verify_lexicon import Table

LANGUAGES = ('en', 'zh', 'es', 'fr', 'de', 'vi', 'ru', 'ja', 'ko', 'ar')


def verify(destination):
    entries, metadata = load_entries()
    saved = json.loads((SITE / '_data/lexicon.json').read_text(encoding='utf-8'))
    assert saved == metadata, 'Source identity changed; regenerate the lexicon'
    search = {}
    for lang, filename in [('en', 'words.json'), ('zh', 'words_zh.json')]:
        rows = json.loads((destination / 'assets/data' / filename).read_text(encoding='utf-8'))
        expected = [{**{key: entry[key] for key in
                        ('word', 'ips', 'ism', 'ipsm', 'root_lemma', 'rank')},
                     'meaning': entry['meaning_' + lang]} for entry in entries]
        assert rows == expected, f'Built data differs from source: {filename}'
        search[lang] = rows

    version = metadata['data_version']
    urls = {}
    word_pages = 0
    for lang in LANGUAGES:
        prefix = '' if lang == 'en' else lang
        page = (destination / prefix / 'search/index.html').read_text(encoding='utf-8')
        match = re.search(r'window\.WORDS_URL\s*=\s*("[^"\n]+")\s*;', page)
        assert match, f'No word data URL: {lang}'
        url = json.loads(match.group(1))
        parts = urlsplit(url)
        expected_name = 'words_zh.json' if lang == 'zh' else 'words.json'
        assert parts.path.endswith('/assets/data/' + expected_name), (lang, url)
        assert parse_qs(parts.query) == {'v': [version]}, (lang, url)
        script = re.search(r'<script\s+src="([^"]*/assets/js/search\.js[^\"]*)"', page)
        assert script, f'No Search script: {lang}'
        assert parse_qs(urlsplit(unescape(script.group(1))).query) == {'v': [version]}, lang
        urls[lang] = url

        rows = search['zh' if lang == 'zh' else 'en']
        for letter in string.ascii_lowercase:
            path = destination / prefix / 'words' / letter / 'index.html'
            table = Table()
            table.feed(path.read_text(encoding='utf-8'))
            expected = [row for row in rows
                        if (row['root_lemma'] or row['word'])[0].casefold() == letter]
            cells = [[(row[key] or '').replace('\r\n', '\n').replace('\r', '\n')
                      for key in ('word', 'ips', 'ism', 'ipsm', 'meaning')]
                     for row in expected]
            assert table.rows == cells, f'Built Words table differs from source: {path}'
            word_pages += 1
    assert (destination / 'assets/js/search.js').read_bytes() == (SITE / 'assets/js/search.js').read_bytes()
    return {'passed': True, 'entries_per_language': len(entries), 'languages': len(urls),
            'all_source_fields_match': True, 'word_pages': word_pages,
            'meaning': 'zh: Chinese; en/es/fr/de/vi/ru/ja/ko/ar: English', 'urls': urls}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--site-dir', type=Path, default=SITE / '_site')
    args = parser.parse_args()
    print(json.dumps(verify(args.site_dir), ensure_ascii=False))
