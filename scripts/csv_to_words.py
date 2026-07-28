#!/usr/bin/env python3
"""把 words_list.csv 转为 A–Z 26 个字母聚合页(10 种语言各一套)供网站词库浏览/SEO。

每个字母页 = 该字母开头的所有 rootLemma 家族的全部成员词,扁平一张大表
(word | ips | ism | ipsm | meaning),按 rootLemma → rank 排序。

数据源:books/Black/Tables/words_list.csv(8 列:word,ips,ism,rootLemma,rank,ipsm,meaningCN,meaningEN)
输出:englishword.github.io/_words[_<lang>]/<letter>.md,共 10 套 × 26 页
  - en  → _words/        meaning ← meaningEN
  - zh  → _words_zh/     meaning ← meaningCN
  - 其余 8 语言 → _words_<lang>/   meaning ← meaningEN(CSV 无对应翻译,复用英文,与搜索页硬约束一致)

文案全面本地化:title/description/表头/计数/返回链接按 LANGS 表各语言翻译;
释义列受数据源限制,非中文一律英文。hreflang 指向全部 10 种语言。

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

LETTERS = list(string.ascii_lowercase)                  # a..z

# hreflang 互指的全部语言(与 _data/languages.yml 顺序一致)
HREFLANG_LANGS = ['en', 'zh', 'es', 'fr', 'de', 'vi', 'ru', 'ja', 'ko', 'ar']

# 每语言配置:目录名/URL 前缀/释义列 + 本地化文案模板({U}=大写字母, {count}=词数)
LANGS = [
    dict(code='en', prefix='', dst='_words', meaning='meaningEN',
         title='Words starting with {U}',
         desc='{count} English words starting with {U}, with IPS pronunciation, ISM morpheme breakdown and IPSM notation.',
         count='{count} words',
         headers=('Word', 'IPS', 'ISM', 'IPSM', 'Meaning'),
         back='← Back to word index'),
    dict(code='zh', prefix='/zh', dst='_words_zh', meaning='meaningCN',
         title='{U} 开头的单词',
         desc='{count} 个 {U} 开头的英语单词,含 IPS 音形标注、ISM 词素划分与 IPSM 记忆符号。',
         count='{count} 个单词',
         headers=('单词', 'IPS', 'ISM', 'IPSM', '释义'),
         back='← 返回词库索引'),
    dict(code='es', prefix='/es', dst='_words_es', meaning='meaningEN',
         title='Palabras que empiezan por {U}',
         desc='{count} palabras en inglés que empiezan por {U}, con pronunciación IPS, desglose morfológico ISM y notación IPSM.',
         count='{count} palabras',
         headers=('Palabra', 'IPS', 'ISM', 'IPSM', 'Significado'),
         back='← Volver al índice de palabras'),
    dict(code='fr', prefix='/fr', dst='_words_fr', meaning='meaningEN',
         title='Mots commençant par {U}',
         desc='{count} mots anglais commençant par {U}, avec prononciation IPS, décomposition morphémique ISM et notation IPSM.',
         count='{count} mots',
         headers=('Mot', 'IPS', 'ISM', 'IPSM', 'Sens'),
         back='← Retour à l’index des mots'),
    dict(code='de', prefix='/de', dst='_words_de', meaning='meaningEN',
         title='Wörter mit {U}',
         desc='{count} englische Wörter mit Anfangsbuchstabe {U}, mit IPS-Aussprache, ISM-Morphemaufschlüsselung und IPSM-Notation.',
         count='{count} Wörter',
         headers=('Wort', 'IPS', 'ISM', 'IPSM', 'Bedeutung'),
         back='← Zurück zum Wortindex'),
    dict(code='vi', prefix='/vi', dst='_words_vi', meaning='meaningEN',
         title='Từ bắt đầu bằng {U}',
         desc='{count} từ tiếng Anh bắt đầu bằng {U}, kèm phiên âm IPS, phân tích hình vị ISM và ký hiệu IPSM.',
         count='{count} từ',
         headers=('Từ', 'IPS', 'ISM', 'IPSM', 'Nghĩa'),
         back='← Quay lại chỉ mục từ'),
    dict(code='ru', prefix='/ru', dst='_words_ru', meaning='meaningEN',
         title='Слова на букву {U}',
         desc='{count} английских слов на букву {U}, с произношением IPS, разбором морфем ISM и нотацией IPSM.',
         count='{count} слов',
         headers=('Слово', 'IPS', 'ISM', 'IPSM', 'Значение'),
         back='← Назад к индексу слов'),
    dict(code='ja', prefix='/ja', dst='_words_ja', meaning='meaningEN',
         title='{U} で始まる単語',
         desc='{U} で始まる英語単語 {count} 語、IPS 発音、ISM 形態素分解、IPSM 表記付き。',
         count='{count} 語',
         headers=('単語', 'IPS', 'ISM', 'IPSM', '意味'),
         back='← 単語インデックスに戻る'),
    dict(code='ko', prefix='/ko', dst='_words_ko', meaning='meaningEN',
         title='{U}(으)로 시작하는 단어',
         desc='{U}(으)로 시작하는 영어 단어 {count}개, IPS 발음, ISM 형태소 분해, IPSM 표기 포함.',
         count='{count}개 단어',
         headers=('단어', 'IPS', 'ISM', 'IPSM', '뜻'),
         back='← 단어 인덱스로 돌아가기'),
    dict(code='ar', prefix='/ar', dst='_words_ar', meaning='meaningEN',
         title='كلمات تبدأ بـ {U}',
         desc='{count} كلمة إنجليزية تبدأ بـ {U}، مع نطق IPS وتحليل الصرف ISM ورموز IPSM.',
         count='{count} كلمة',
         headers=('كلمة', 'IPS', 'ISM', 'IPSM', 'المعنى'),
         back='← العودة إلى فهرس الكلمات'),
]


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
    out = [nav_block(letter, cfg, count), '<table>', '<thead>',
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

    for cfg in LANGS:                            # 幂等:清所有语言的生成目录
        d = os.path.join(SITE, cfg['dst'])
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
        for cfg in LANGS:
            write_page(os.path.join(SITE, cfg['dst'], f'{l}.md'), cfg, l, count, rows)

    print(f'共 {total} 词(去重后),生成 {len(LETTERS)}×{len(LANGS)} = {len(LETTERS) * len(LANGS)} 个字母页')
    print(f'丢弃(无法归类):{dropped}')
    print('字母分布:', ' '.join(f'{l}:{dist[l]}' for l in LETTERS))


if __name__ == '__main__':
    main()
