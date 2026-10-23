#!/usr/bin/env python3
"""Verify built Search pages: all languages use the full lexicon and correct meanings."""
import argparse
from html import unescape
import json
from pathlib import Path
import re
from urllib.parse import parse_qs, urlsplit
from lingose_data import SITE, load_entries

LANGUAGES = ('en', 'zh', 'es', 'fr', 'de', 'vi', 'ru', 'ja', 'ko', 'ar')


def verify(destination):
    entries, metadata = load_entries()
    expected_words = [row['word'] for row in entries]
    for lang, filename in [('en', 'words.json'), ('zh', 'words_zh.json')]:
        rows = json.loads((destination / 'assets/data' / filename).read_text(encoding='utf-8'))
        assert [row['word'] for row in rows] == expected_words, f'Incomplete or unsorted {filename}'
        assert all(row['meaning'] == entry['meaning_' + lang]
                   for row, entry in zip(rows, entries)), f'Wrong meaning language: {filename}'

    version = metadata['data_version']
    urls = {}
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
    assert (destination / 'assets/js/search.js').read_bytes() == (SITE / 'assets/js/search.js').read_bytes()
    return {'passed': True, 'entries_per_language': len(entries), 'languages': len(urls),
            'meaning': 'zh: Chinese; en/es/fr/de/vi/ru/ja/ko/ar: English', 'urls': urls}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--site-dir', type=Path, default=SITE / '_site')
    args = parser.parse_args()
    print(json.dumps(verify(args.site_dir), ensure_ascii=False))
