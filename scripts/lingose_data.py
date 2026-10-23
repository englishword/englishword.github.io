"""Read the installed Lingose 0.3 runtime without changing the package or its data."""
import hashlib
import importlib.metadata
import importlib.resources
import json
from pathlib import Path
import sqlite3

SITE = Path(__file__).resolve().parents[1]


def sort_key(row):
    """Root A–Z, then Lingose's original hierarchical rank code, then spelling.

    Missing roots use the word itself. Missing ranks follow ranked family members.
    Rank is a source string (e.g. 50-40-...-1i), NOT a frequency integer.
    """
    return ((row['root_lemma'] or row['word']).casefold(),
            row['rank'] is None, row['rank'] or '',
            row['word'].casefold(), row['word'])


def load_entries():
    resource = importlib.resources.files('lingose').joinpath('runtime.sqlite')
    with importlib.resources.as_file(resource) as path:
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        with sqlite3.connect(path.as_uri() + '?mode=ro&immutable=1', uri=True) as db:
            db.row_factory = sqlite3.Row
            db.execute('PRAGMA query_only=ON')
            info = dict(db.execute('SELECT * FROM runtime_info').fetchone())
            if (info['format_version'], info['projection_version']) != (1, 1):
                raise ValueError('Unsupported Lingose runtime format')
            entries = [dict(row) for row in db.execute('''
                SELECT word, ips, ism, ipsm, root_lemma, rank, meaning_en, meaning_zh
                FROM runtime_entry
            ''')]
        if hashlib.sha256(path.read_bytes()).hexdigest() != digest:
            raise ValueError('Lingose runtime changed during export')
    if not entries or len({row['word'] for row in entries}) != len(entries):
        raise ValueError('Expected a nonempty lexicon with unique source spellings')
    entries.sort(key=sort_key)
    metadata = {
        'count': len(entries),
        'source': 'Installed Python lingose / runtime.sqlite',
        'package_version': importlib.metadata.version('lingose'),
        'runtime_sha256': digest,
        'data_version': info['data_version'],
        'sort': ['root_lemma (casefold; missing: word)',
                 'rank (source code; missing last)', 'word (casefold)', 'word'],
        'missing': {key: sum(row[key] is None for row in entries)
                    for key in entries[0] if key != 'word'},
    }
    return entries, metadata


def write_metadata(metadata):
    (SITE / '_data' / 'lexicon.json').write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
