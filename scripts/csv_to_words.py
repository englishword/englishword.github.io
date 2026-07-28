#!/usr/bin/env python3
"""把 words_list.csv 转为 A–Z 26 个字母聚合页(中英各一套)供网站词库浏览/SEO。

每个字母页 = 该字母开头的所有 rootLemma 家族的全部成员词,扁平一张大表
(word | ips | ism | ipsm | meaning),按 rootLemma → rank 排序。

数据源:books/Black/Tables/words_list.csv(8 列:word,ips,ism,rootLemma,rank,ipsm,meaningCN,meaningEN)
输出:
  englishword.github.io/_words/<letter>.md     英文,meaning 取 meaningEN
  englishword.github.io/_words_zh/<letter>.md  中文,meaning 取 meaningCN

字母键:rootLemma 非空取 rootLemma[0],空则取 word[0](6 个空 rootLemma 按 word 归入)。
可在任意目录运行,路径基于脚本自身位置计算。与 csv_to_json.py 并存,不替换它。
"""
import csv
import html
import os
import shutil
import string

HERE = os.path.dirname(os.path.abspath(__file__))      # englishword.github.io/scripts
SITE = os.path.dirname(HERE)                            # englishword.github.io
ROOT = os.path.dirname(SITE)                            # 项目根
SRC = os.path.join(ROOT, 'books', 'Black', 'Tables', 'words_list.csv')
DST_EN = os.path.join(SITE, '_words')                   # meaning ← meaningEN
DST_ZH = os.path.join(SITE, '_words_zh')                # meaning ← meaningCN

LETTERS = list(string.ascii_lowercase)                  # a..z


def letter_key(row):
    """返回该行归属的字母(a-z);rootLemma 优先,空则用 word;都无法归类返回 None。"""
    lemma = (row.get('rootLemma') or '').strip().lower()
    if lemma and lemma[0] in string.ascii_lowercase:
        return lemma[0]
    word = (row.get('word') or '').strip().lower()
    if word and word[0] in string.ascii_lowercase:
        return word[0]
    return None


def cell(s):
    """HTML 安全:escape 后把换行转 <br>(与 search.js 的 escape + \\n→<br> 同策略)。"""
    s = html.escape(s or '')
    return s.replace('\r\n', '\n').replace('\r', '\n').replace('\n', '<br>\n')


def sort_key(row):
    return (
        (row.get('rootLemma') or '').strip().lower(),
        (row.get('rank') or '').strip(),
        (row.get('word') or '').strip().lower(),
    )


def nav_block(letter, lang, count):
    """A–Z 导航(静态 HTML)。
    放进 body 而非 layout,避免 layout 里 26×多 Liquid 标签触发 Ruby 栈溢出。
    当前字母用 <strong>,其余为链接;含语言前缀与词数。"""
    prefix = '' if lang == 'en' else '/' + lang
    links = []
    for c in string.ascii_lowercase:
        label = c.upper()
        if c == letter:
            links.append('<strong>{}</strong>'.format(label))
        else:
            links.append('<a href="{}/words/{}/">{}</a>'.format(prefix, c, label))
    count_text = '{} 个单词'.format(count) if lang == 'zh' else '{} words'.format(count)
    return ('<nav class="az-nav" aria-label="A-Z">\n'
            + ' '.join(links) + '\n</nav>\n'
            + '<p>' + count_text + '</p>\n')


def write_page(path, title, letter, lang, count, desc, rows, meaning_col):
    frontmatter = (
        '---\n'
        f'title: "{title}"\n'
        f'letter: {letter}\n'
        f'lang: {lang}\n'
        f'count: {count}\n'
        f'description: "{desc}"\n'
        'hreflang_langs: [en, zh]\n'
        '---\n\n'
    )
    out = [nav_block(letter, lang, count), '<table>', '<thead>',
           '<tr><th>Word</th><th>IPS</th><th>ISM</th><th>IPSM</th><th>Meaning</th></tr>',
           '</thead>', '<tbody>']
    for r in rows:
        out.append(
            '<tr><td>{w}</td><td>{p}</td><td>{s}</td><td>{m}</td><td>{e}</td></tr>'.format(
                w=cell(r.get('word')), p=cell(r.get('ips')), s=cell(r.get('ism')),
                m=cell(r.get('ipsm')), e=cell(r.get(meaning_col))))
    out.append('</tbody>')
    out.append('</table>')
    with open(path, 'w', encoding='utf-8') as f:
        f.write(frontmatter)
        f.write('\n'.join(out))
        f.write('\n')


def main():
    buckets = {l: [] for l in LETTERS}
    seen = set()
    dropped = 0
    with open(SRC, encoding='utf-8-sig', newline='') as f:
        for row in csv.DictReader(f):
            word = (row.get('word') or '').strip()
            ips = (row.get('ips') or '').strip()
            if (word.lower(), ips) in seen:       # 去重(10 个重复 word)
                continue
            seen.add((word.lower(), ips))
            l = letter_key(row)
            if l is None:
                dropped += 1
                continue
            buckets[l].append(row)

    for d in (DST_EN, DST_ZH):                     # 幂等:只清这两个生成目录
        if os.path.isdir(d):
            shutil.rmtree(d)
        os.makedirs(d, exist_ok=True)

    total = 0
    dist = {}
    for l in LETTERS:
        rows = buckets[l]
        rows.sort(key=sort_key)
        count = len(rows)
        total += count
        dist[l] = count
        U = l.upper()
        write_page(os.path.join(DST_EN, f'{l}.md'),
                   f'Words starting with {U}', l, 'en', count,
                   f'{count} English words starting with {U}, with IPS pronunciation, '
                   f'ISM morpheme breakdown and IPSM notation.',
                   rows, 'meaningEN')
        write_page(os.path.join(DST_ZH, f'{l}.md'),
                   f'{U} 开头的单词', l, 'zh', count,
                   f'{count} 个 {U} 开头的英语单词,含 IPS 音形标注、ISM 词素划分与 IPSM 记忆符号。',
                   rows, 'meaningCN')

    print(f'共 {total} 词(去重后),生成 {len(LETTERS)}×2 = {len(LETTERS) * 2} 个字母页')
    print(f'丢弃(无法归类):{dropped}')
    print('字母分布:', ' '.join(f'{l}:{dist[l]}' for l in LETTERS))


if __name__ == '__main__':
    main()
