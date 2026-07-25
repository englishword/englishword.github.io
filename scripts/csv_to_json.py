#!/usr/bin/env python3
"""把 words_list.csv 转换为中英两份 JSON 供网站搜索使用。

数据源:books/Black/Tables/words_list.csv(8 列:word,ips,ism,rootLemma,rank,ipsm,meaningCN,meaningEN)
输出:
  englishword.github.io/assets/data/words.json      英文/默认,meaning 取 meaningEN
  englishword.github.io/assets/data/words_zh.json   中文,meaning 取 meaningCN

可在任意目录运行,路径基于脚本自身位置计算。
"""
import csv
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))      # englishword.github.io/scripts
SITE = os.path.dirname(HERE)                            # englishword.github.io
ROOT = os.path.dirname(SITE)                            # 项目根
SRC = os.path.join(ROOT, 'books', 'Black', 'Tables', 'words_list.csv')
DST_EN = os.path.join(SITE, 'assets', 'data', 'words.json')       # meaning ← meaningEN
DST_ZH = os.path.join(SITE, 'assets', 'data', 'words_zh.json')    # meaning ← meaningCN


def main():
    words_en = []
    words_zh = []
    with open(SRC, encoding='utf-8-sig', newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            common = {
                'word': (row.get('word') or '').strip(),
                'ips': (row.get('ips') or '').strip(),
                'ipsm': (row.get('ipsm') or '').strip(),
            }
            words_en.append({**common, 'meaning': (row.get('meaningEN') or '').strip()})
            words_zh.append({**common, 'meaning': (row.get('meaningCN') or '').strip()})
    os.makedirs(os.path.dirname(DST_EN), exist_ok=True)
    for dst, words in [(DST_EN, words_en), (DST_ZH, words_zh)]:
        with open(dst, 'w', encoding='utf-8') as f:
            json.dump(words, f, ensure_ascii=False)
    print(f'已生成 {DST_EN} (meaning←meaningEN)')
    print(f'已生成 {DST_ZH} (meaning←meaningCN)')
    print(f'共 {len(words_en)} 条')


if __name__ == '__main__':
    main()
