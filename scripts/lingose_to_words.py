#!/usr/bin/env python3
"""生成十语言 A–Z 词库页；来源和 root_lemma / rank 排序与 Search 完全一致。

仅中文使用中文释义，其余九种语言共用英文释义。缺失字段留空，不丢弃条目。
"""
import html
import os
import string
from lingose_data import SITE, load_entries, write_metadata

LETTERS = list(string.ascii_lowercase)                  # a..z

# hreflang 互指的全部语言(与 _data/languages.yml 顺序一致)
HREFLANG_LANGS = ['en', 'zh', 'es', 'fr', 'de', 'vi', 'ru', 'ja', 'ko', 'ar']

# 每语言配置:目录名/URL 前缀/释义列 + 本地化文案模板({U}=大写字母, {count}=词数)
LANGS = [
    dict(code='en', prefix='', dst='_words', meaning='meaning_en',
         title='Words starting with {U}',
         desc='{count} English words starting with {U}, with IPS pronunciation, ISM morpheme breakdown and IPSM notation.',
         count='{count} words',
         headers=('Word', 'IPS', 'ISM', 'IPSM', 'Meaning'),
         back='← Back to word index'),
    dict(code='zh', prefix='/zh', dst='_words_zh', meaning='meaning_zh',
         title='{U} 开头的单词',
         desc='{count} 个 {U} 开头的英语单词,含 IPS 音形标注、ISM 词素划分与 IPSM 记忆符号。',
         count='{count} 个单词',
         headers=('单词', 'IPS', 'ISM', 'IPSM', '释义'),
         back='← 返回词库索引'),
    dict(code='es', prefix='/es', dst='_words_es', meaning='meaning_en',
         title='Palabras que empiezan por {U}',
         desc='{count} palabras en inglés que empiezan por {U}, con pronunciación IPS, desglose morfológico ISM y notación IPSM.',
         count='{count} palabras',
         headers=('Palabra', 'IPS', 'ISM', 'IPSM', 'Significado'),
         back='← Volver al índice de palabras'),
    dict(code='fr', prefix='/fr', dst='_words_fr', meaning='meaning_en',
         title='Mots commençant par {U}',
         desc='{count} mots anglais commençant par {U}, avec prononciation IPS, décomposition morphémique ISM et notation IPSM.',
         count='{count} mots',
         headers=('Mot', 'IPS', 'ISM', 'IPSM', 'Sens'),
         back='← Retour à l’index des mots'),
    dict(code='de', prefix='/de', dst='_words_de', meaning='meaning_en',
         title='Wörter mit {U}',
         desc='{count} englische Wörter mit Anfangsbuchstabe {U}, mit IPS-Aussprache, ISM-Morphemaufschlüsselung und IPSM-Notation.',
         count='{count} Wörter',
         headers=('Wort', 'IPS', 'ISM', 'IPSM', 'Bedeutung'),
         back='← Zurück zum Wortindex'),
    dict(code='vi', prefix='/vi', dst='_words_vi', meaning='meaning_en',
         title='Từ bắt đầu bằng {U}',
         desc='{count} từ tiếng Anh bắt đầu bằng {U}, kèm phiên âm IPS, phân tích hình vị ISM và ký hiệu IPSM.',
         count='{count} từ',
         headers=('Từ', 'IPS', 'ISM', 'IPSM', 'Nghĩa'),
         back='← Quay lại chỉ mục từ'),
    dict(code='ru', prefix='/ru', dst='_words_ru', meaning='meaning_en',
         title='Слова на букву {U}',
         desc='{count} английских слов на букву {U}, с произношением IPS, разбором морфем ISM и нотацией IPSM.',
         count='{count} слов',
         headers=('Слово', 'IPS', 'ISM', 'IPSM', 'Значение'),
         back='← Назад к индексу слов'),
    dict(code='ja', prefix='/ja', dst='_words_ja', meaning='meaning_en',
         title='{U} で始まる単語',
         desc='{U} で始まる英語単語 {count} 語、IPS 発音、ISM 形態素分解、IPSM 表記付き。',
         count='{count} 語',
         headers=('単語', 'IPS', 'ISM', 'IPSM', '意味'),
         back='← 単語インデックスに戻る'),
    dict(code='ko', prefix='/ko', dst='_words_ko', meaning='meaning_en',
         title='{U}(으)로 시작하는 단어',
         desc='{U}(으)로 시작하는 영어 단어 {count}개, IPS 발음, ISM 형태소 분해, IPSM 표기 포함.',
         count='{count}개 단어',
         headers=('단어', 'IPS', 'ISM', 'IPSM', '뜻'),
         back='← 단어 인덱스로 돌아가기'),
    dict(code='ar', prefix='/ar', dst='_words_ar', meaning='meaning_en',
         title='كلمات تبدأ بـ {U}',
         desc='{count} كلمة إنجليزية تبدأ بـ {U}، مع نطق IPS وتحليل الصرف ISM ورموز IPSM.',
         count='{count} كلمة',
         headers=('كلمة', 'IPS', 'ISM', 'IPSM', 'المعنى'),
         back='← العودة إلى فهرس الكلمات'),
]


def letter_key(row):
    """root_lemma 优先，缺失时用 word 的首字母。"""
    lemma = (row.get('root_lemma') or '').casefold()
    if lemma and lemma[0] in string.ascii_lowercase:
        return lemma[0]
    word = (row.get('word') or '').strip().lower()
    if word and word[0] in string.ascii_lowercase:
        return word[0]
    return None


def cell(s):
    """HTML 安全:escape 后把换行转 <br>(与 search.js 的 escape + \\n→<br> 同策略)。"""
    s = html.escape(s or '')
    return s.replace('\r\n', '\n').replace('\r', '\n').replace('\n', '<br>')


def nav_block(letter, cfg, count):
    """A–Z 导航(静态 HTML)。
    放进 body 而非 layout,避免 layout 里 26×多 Liquid 标签触发 Ruby 栈溢出。
    当前字母用 <strong>,其余为链接;含语言前缀与词数(已本地化)。"""
    prefix = cfg['prefix']
    links = []
    for c in string.ascii_lowercase:
        label = c.upper()
        if c == letter:
            links.append('<strong>{}</strong>'.format(label))
        else:
            links.append('<a href="{}/words/{}/">{}</a>'.format(prefix, c, label))
    count_text = cfg['count'].format(count=count)
    return ('<nav class="az-nav" aria-label="A-Z">\n'
            + ' '.join(links) + '\n</nav>\n'
            + '<p>' + count_text + '</p>\n')


def write_page(path, cfg, letter, count, rows):
    U = letter.upper()
    title = cfg['title'].format(U=U, count=count)
    desc = cfg['desc'].format(U=U, count=count)
    h = cfg['headers']
    hreflang = ', '.join(HREFLANG_LANGS)
    frontmatter = (
        '---\n'
        f'title: "{title}"\n'
        f'letter: {letter}\n'
        f'lang: {cfg["code"]}\n'
        f'count: {count}\n'
        f'description: "{desc}"\n'
        f'back_label: "{cfg["back"]}"\n'
        f'hreflang_langs: [{hreflang}]\n'
        '---\n\n'
    )
    out = [nav_block(letter, cfg, count),
           f'<div class="word-table-scroll" tabindex="0" role="region" aria-label="{html.escape(title, quote=True)}">',
           '<table>', '<thead>',
           '<tr><th>{}</th><th>{}</th><th>{}</th><th>{}</th><th>{}</th></tr>'.format(*h),
           '</thead>', '<tbody>']
    meaning_col = cfg['meaning']
    for r in rows:
        out.append(
            '<tr><td>{w}</td><td>{p}</td><td>{s}</td><td>{m}</td><td>{e}</td></tr>'.format(
                w=cell(r.get('word')), p=cell(r.get('ips')), s=cell(r.get('ism')),
                m=cell(r.get('ipsm')), e=cell(r.get(meaning_col))))
    out.append('</tbody>')
    out.append('</table>')
    out.append('</div>')
    with open(path, 'w', encoding='utf-8') as f:
        f.write(frontmatter)
        f.write('\n'.join(out))
        f.write('\n')


def write_pages(entries):
    buckets = {l: [] for l in LETTERS}
    for row in entries:
        letter = letter_key(row)
        if letter is None:
            raise ValueError(f'Word outside A–Z: {row["word"]!r}')
        buckets[letter].append(row)

    for cfg in LANGS:
        os.makedirs(SITE / cfg['dst'], exist_ok=True)

    total = 0
    dist = {}
    for l in LETTERS:
        rows = buckets[l]
        count = len(rows)
        total += count
        dist[l] = count
        for cfg in LANGS:
            write_page(os.path.join(SITE, cfg['dst'], f'{l}.md'), cfg, l, count, rows)

    print(f'共 {total} 词，生成 {len(LETTERS)}×{len(LANGS)} = {len(LETTERS) * len(LANGS)} 个字母页')
    print('字母分布:', ' '.join(f'{l}:{dist[l]}' for l in LETTERS))


if __name__ == '__main__':
    entries, metadata = load_entries()
    write_pages(entries)
    write_metadata(metadata)
