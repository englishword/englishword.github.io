#!/usr/bin/env python3
"""Export Search JSON in the same root_lemma / rank order as the Words pages."""
import json
from lingose_data import SITE, load_entries, write_metadata


def write_data(entries):
    destination = SITE / 'assets' / 'data'
    destination.mkdir(parents=True, exist_ok=True)
    for lang, filename in [('en', 'words.json'), ('zh', 'words_zh.json')]:
        words = [{**{key: row[key] for key in
                     ('word', 'ips', 'ism', 'ipsm', 'root_lemma', 'rank')},
                  'meaning': row['meaning_' + lang]} for row in entries]
        (destination / filename).write_text(
            json.dumps(words, ensure_ascii=False, separators=(',', ':')) + '\n',
            encoding='utf-8')


if __name__ == '__main__':
    entries, metadata = load_entries()
    write_data(entries)
    write_metadata(metadata)
