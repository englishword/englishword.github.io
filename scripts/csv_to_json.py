#!/usr/bin/env python3
"""把 words_list.csv 转换为 words.json 供网站搜索使用。

数据源:books/Black/Tables/words_list.csv(4 列:word,ips,ipsm,meaning)
输出:englishword.github.io/assets/data/words.json

可在任意目录运行,路径基于脚本自身位置计算。
"""
import csv
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))      # englishword.github.io/scripts
SITE = os.path.dirname(HERE)                            # englishword.github.io
ROOT = os.path.dirname(SITE)                            # 项目根
SRC = os.path.join(ROOT, 'books', 'Black', 'Tables', 'words_list.csv')
DST = os.path.join(SITE, 'assets', 'data', 'words.json')


def main():
    words = []
    with open(SRC, encoding='utf-8-sig', newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            words.append({
                'word': (row.get('word') or '').strip(),
                'ips': (row.get('ips') or '').strip(),
                'ipsm': (row.get('ipsm') or '').strip(),
                'meaning': (row.get('meaning') or '').strip(),
            })
    os.makedirs(os.path.dirname(DST), exist_ok=True)
    with open(DST, 'w', encoding='utf-8') as f:
        json.dump(words, f, ensure_ascii=False)
    print(f'已生成 {DST}')
    print(f'共 {len(words)} 条')


if __name__ == '__main__':
    main()
