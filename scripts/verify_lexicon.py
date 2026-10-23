#!/usr/bin/env python3
"""Check every Search field and Words table cell against the installed source."""
from collections import Counter
from html.parser import HTMLParser
import json
import string
import lingose
from lingose_data import SITE, load_entries

LANGUAGES = ('en', 'zh', 'es', 'fr', 'de', 'vi', 'ru', 'ja', 'ko', 'ar')


class Table(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.rows = []
        self.row = None
        self.cell = None

    def handle_starttag(self, tag, attrs):
        if tag == 'tr':
            self.row = []
        elif tag == 'td':
            self.cell = ''
        elif tag == 'br' and self.cell is not None:
            self.cell += '\n'

    def handle_data(self, text):
        if self.cell is not None:
            self.cell += text

    def handle_endtag(self, tag):
        if tag == 'td':
            self.row.append(self.cell)
            self.cell = None
        elif tag == 'tr' and self.row:
            self.rows.append(self.row)
            self.row = None


def main():
    entries, metadata = load_entries()
    saved = json.loads((SITE / '_data/lexicon.json').read_text(encoding='utf-8'))
    assert saved == metadata, 'Source identity or count changed; regenerate the lexicon'
    source = {row['word']: row for row in entries}
    search = {}
    for lang, name in [('en', 'words.json'), ('zh', 'words_zh.json')]:
        data = json.loads((SITE / 'assets/data' / name).read_text(encoding='utf-8'))
        assert len(data) == len(source)
        assert Counter(row['word'] for row in data) == Counter(source.keys())
        # Compare all projected values, including null, exact case and Unicode.
        for row in data:
            expected = source[row['word']]
            assert set(row) == {'word', 'ips', 'ism', 'ipsm', 'root_lemma', 'rank', 'meaning'}
            assert all(row[key] == expected[key] for key in row if key != 'meaning'), row['word']
            assert row['meaning'] == expected['meaning_' + lang], row['word']
        # Independently assert each adjacent root/rank pair is monotonic.
        keys = [((r['root_lemma'] or r['word']).casefold(), r['rank'] is None,
                 r['rank'] or '', r['word'].casefold(), r['word']) for r in data]
        assert all(a <= b for a, b in zip(keys, keys[1:])), name
        search[lang] = data
    assert [r['word'] for r in search['en']] == [r['word'] for r in search['zh']]

    # Cross-check the resource projection with public API, including incomplete
    # records, variant spellings, source nulls, multiline meanings and root families.
    samples = {'run', 'running', 'ran', 'act', 'action', 'Dept.', 'Hippomenes'}
    for field in ('ips', 'ism', 'ipsm', 'root_lemma', 'rank', 'meaning_en', 'meaning_zh'):
        samples.update([r['word'] for r in entries if r[field] is None][:3])
    samples.update(r['word'] for r in entries[::500])
    for word in samples & source.keys():
        public = lingose.lookup(word)
        row = source[word]
        assert all(public[key] == row[key] for key in ('ips', 'ism', 'ipsm', 'root_lemma', 'rank')), word
        assert public['meaning'] == {'en': row['meaning_en'], 'zh': row['meaning_zh']}, word

    distribution = Counter()
    pages = 0
    for lang in LANGUAGES:
        directory = SITE / ('_words' if lang == 'en' else '_words_' + lang)
        assert {p.stem for p in directory.glob('*.md')} == set(string.ascii_lowercase)
        meaning_lang = 'zh' if lang == 'zh' else 'en'
        flattened = []
        for letter in string.ascii_lowercase:
            path = directory / (letter + '.md')
            text = path.read_text(encoding='utf-8')
            expected = [r for r in search[meaning_lang]
                        if (r['root_lemma'] or r['word'])[0].casefold() == letter]
            assert f'count: {len(expected)}\n' in text, str(path)
            assert f'lang: {lang}\n' in text, str(path)
            table = Table()
            table.feed(text)
            cells = [[(r[key] or '').replace('\r\n', '\n').replace('\r', '\n')
                      for key in ('word', 'ips', 'ism', 'ipsm', 'meaning')] for r in expected]
            assert table.rows == cells, f'Table differs from Search/source: {path}'
            flattened.extend(row[0] for row in table.rows)
            if lang == 'en':
                distribution[letter] = len(expected)
            pages += 1
        assert flattened == [r['word'] for r in search[meaning_lang]], lang
        index = SITE / ('words.md' if lang == 'en' else lang + '/words.md')
        assert '{{ site.data.lexicon.count }}' in index.read_text(encoding='utf-8')
    print(json.dumps({'entries': len(source), 'search_files': len(search), 'word_pages': pages,
                      'public_api_checks': len(samples & source.keys()),
                      'sorted': True, 'all_source_fields_match': True,
                      'largest_letter': distribution.most_common(1)}, ensure_ascii=False))


if __name__ == '__main__':
    main()
