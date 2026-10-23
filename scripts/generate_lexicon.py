#!/usr/bin/env python3
"""Refresh Search and all ten Words collections from one installed Lingose snapshot."""
from lingose_data import load_entries, write_metadata
from lingose_to_json import write_data
from lingose_to_words import write_pages


def main():
    entries, metadata = load_entries()
    # Validate all A–Z memberships before writing any generated outputs.
    from lingose_to_words import letter_key
    unclassified = [row['word'] for row in entries if letter_key(row) is None]
    if unclassified:
        raise ValueError(f'Words outside A–Z: {unclassified!r}')
    write_data(entries)
    write_pages(entries)
    write_metadata(metadata)
    print(f"Lingose {metadata['package_version']}: {metadata['count']:,} entries")
    print(f"runtime.sqlite SHA-256: {metadata['runtime_sha256']}")


if __name__ == '__main__':
    main()
