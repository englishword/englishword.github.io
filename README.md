# IPSM Approach

> [中文](#zh) below.

<p align="center"><img src="images/logo/logo.svg" alt="IPSM Approach" height="40"></p>

**IPSM Approach** (Integrated Pronunciation, Spelling and Meaning) is a unified method for memorizing English vocabulary — it brings **sound**, **form**, and **meaning** together into a single learning framework.

---

## What is IPSM?

IPSM integrates three perspectives that are usually taught separately:

- **IPS — Integrated Pronunciation & Spelling**: embed pronunciation rules directly into the word using phoneme marks, so the spelling itself encodes how it sounds.
- **ISM — Integrated Spelling & Meaning**: segment words into morphemes, making the building rules that carry meaning visible in the spelling.
- **IPM — Integrated Pronunciation & Meaning**: feel the inner link between the phoneme rhythm of a word and its meaning.

The method is presented across **9 bilingual chapters** (English / 简体中文), with an interactive IPA-vs-IPS comparison page and a client-side word search over the full lexicon.

## Features

- 📖 **9 bilingual chapters** — English at the site root, Chinese under `/zh/`.
- 🔤 **IPA & IPS comparison page** — an interactive layout contrasting IPA with the project's IPS notation.
- 🔎 **Client-side word search** — 50,335 entries, substring filter on the word, paginated 200/page, showing IPS / IPSM notation and meaning. Chinese uses `words_zh.json`; all other languages use English meanings in `words.json`.
- 🌍 **Language switcher** — English / 简体中文 dropdown in the top-right.

---

<a id="zh"></a>

# IPSM Approach 音形意统一记忆法

> [English](#ipsm-approach) 见上方。

<p align="center"><img src="images/logo/logo-zh.svg" alt="音形意统一记忆法" height="40"></p>

**IPSM Approach（音形意统一记忆法）** 是一套英语单词记忆方法，把**音、形、意**三者统一进同一个学习框架。

---

## 什么是 IPSM？

IPSM 把通常分开教学的三个角度统一在一起：

- **IPS 音形统一**：用音素标注符号把发音规则直接融入单词，让拼写本身就能体现读音。
- **ISM 形意统一**：用词素划分把构词规则融入单词，让承载词意的构造在拼写中可见。
- **IPM 音意统一**：体会单词的音素音律与词意之间的内在联系。

整套方法以**9 章双语文档**（英文 / 简体中文）呈现，并配有交互式 IPA 与 IPS 对照页，以及对全词库的客户端单词搜索。

## 功能特性

- 📖 **9 章双语文档**：英文在站点根目录，中文在 `/zh/` 下。
- 🔤 **IPA 与 IPS 对照页**：以交互排版对比 IPA 与本项目自创的 IPS 标注。
- 🔎 **客户端单词搜索**：50,335 个词条，按单词子串过滤、每页 200 条分页，显示 IPS / IPSM 标注与释义；中文用 `words_zh.json`，其他语言用英文释义 `words.json`。
- 🌍 **语言切换**：右上角 English / 简体中文 下拉。

## 更新 Words / Search 词库

安装 Python `lingose==0.3.0` 后，在网站目录运行：

```powershell
python scripts/generate_lexicon.py
python scripts/verify_lexicon.py
bundle exec jekyll build
python scripts/verify_search_pages.py
```

生成器从已安装包的 `runtime.sqlite` 只读提取全部条目，一次生成两份搜索 JSON、十语言 × 26 个字母页及 `_data/lexicon.json` 来源记录。常规 Jekyll 构建直接使用这些已提交产物，不需要安装 Lingose。该流程替代旧的 `csv_to_json.py` / `csv_to_words.py`，不再依赖旧书稿 CSV。

两类页面共用排序：`root_lemma` 不区分大小写升序 → 原始 `rank` 编码升序 → 单词拼写打破并列。`rank` 是词族层级编码，不是词频数值；不转换为数字。缺失词根用单词本身归组，缺失 rank 排在该词族有 rank 的条目之后。保留原始大小写、编码、空值和全部条目；显示时缺失标注或释义留空。中文使用中文释义，其余九种语言沿用英文释义。

来源版本、数据库 SHA-256、条目总数和缺失字段统计见 `_data/lexicon.json`。再次更新时重新运行同一命令，并验证生成结果。

Search 的数据和脚本 URL 附带词库版本号，防止扩容后复用旧缓存。构建后运行 `verify_search_pages.py`，核对十语言均使用完整词库，且只有中文使用中文释义，其他九种语言的 Meaning 全部来自英文释义。

## 许可与致谢

- **许可**：MIT——见 [`LICENSE`](LICENSE)。
- **主题**：基于 [Jekyll Serif](https://github.com/zerostaticthemes/jekyll-serif-theme)（作者 [Zerostatic Themes](https://www.zerostatic.io) / Robert Austin）。
