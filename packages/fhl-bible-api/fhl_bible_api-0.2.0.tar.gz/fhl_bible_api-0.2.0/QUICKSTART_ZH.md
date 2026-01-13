# FHL Bible API - 快速入門指南

## 簡介

FHL Bible API Client 是一個用於查詢台灣信望愛聖經 API 的 Python 客戶端庫。

## 安裝

```bash
pip install fhl-bible-api
```

或使用 uv：

```bash
uv add fhl-bible-api
```

## 基本使用

### 1. 查詢單一經文

```python
from fhl_bible_api import FHLBibleClient

# 創建客戶端
client = FHLBibleClient()

# 查詢創世記 1:1
response = client.get_verse(book_id=1, chapter=1, verse=1)
print(response.records[0].text)
# 輸出: 起初,神創造天地。

# 記得關閉連接
client.close()
```

### 2. 使用 Context Manager (推薦)

```python
from fhl_bible_api import FHLBibleClient

with FHLBibleClient() as client:
    response = client.get_verse(book_id=1, chapter=1, verse=1)
    print(response.records[0].text)
# 自動關閉連接
```

### 3. 查詢不同版本

```python
with FHLBibleClient() as client:
    # 查詢英文 KJV 版本
    response = client.get_verse(
        book_id=43,  # 約翰福音
        chapter=3,
        verse=16,
        version="kjv"
    )
    print(response.records[0].text)
```

### 4. 查詢整章經文

```python
with FHLBibleClient() as client:
    # 查詢詩篇 23 篇
    verses = client.get_chapter(book_id=19, chapter=23)
    
    for verse_response in verses:
        verse = verse_response.records[0]
        print(f"{verse.get_reference()}: {verse.text}")
```

### 5. 搜尋書卷

```python
with FHLBibleClient() as client:
    # 使用中文簡稱搜尋
    results = client.search_book_by_name("創")
    
    # 使用英文搜尋
    results = client.search_book_by_name("Gen")
    
    # 使用完整書名搜尋
    results = client.search_book_by_name("創世記")
    
    for book_id, book_info in results:
        print(f"{book_id}: {book_info['full_name']}")
```

### 6. 獲取書卷資訊

```python
with FHLBibleClient() as client:
    # 獲取詩篇資訊
    info = client.get_book_info(19)
    print(f"書名: {info['full_name']}")
    print(f"中文簡稱: {info['chinese']}")
    print(f"英文簡稱: {info['english']}")
```

### 7. 原文字彙分析

獲取經文的原文字彙分析，包含 Strong's 編號、詞性、詞形變化等：

```python
with FHLBibleClient() as client:
    # 查詢約翰福音 3:16 的原文分析
    response = client.get_word_parsing(book_id=43, chapter=3, verse=16)
    
    print(f"約別: {'新約' if response.testament == 0 else '舊約'}")
    
    # 遍歷每個字詞
    for word in response.records:
        if word.word_id > 0:  # 跳過摘要記錄 (wid=0)
            print(f"\n字詞 #{word.word_id}: {word.word}")
            print(f"  Strong's 編號: {word.strong_number}")
            print(f"  詞性: {word.part_of_speech}")
            print(f"  原形: {word.original_form}")
            print(f"  中文解釋: {word.explanation}")
    
    # 前後節導航
    if response.prev_verse:
        print(f"\n前一節: {response.prev_verse.chinese_abbr} {response.prev_verse.chapter}:{response.prev_verse.verse}")
    if response.next_verse:
        print(f"下一節: {response.next_verse.chinese_abbr} {response.next_verse.chapter}:{response.next_verse.verse}")

# 輸出範例:
# 字詞 #1: Οὕτως
#   Strong's 編號: 3779
#   詞性: Adv
#   原形: οὕτω(ς)
#   中文解釋: 如此, 這樣
```

### 8. 查詢次經 (Apocrypha)

查詢次經/旁經書卷 (編號 101-115)：

```python
with FHLBibleClient() as client:
    # 查詢瑪加伯上 1:10 (1 Maccabees)
    response = client.get_apocrypha_verse(book_id=101, chapter=1, verse=10)
    verse = response.records[0]
    
    print(f"書卷: {verse.chinese_abbr} ({verse.english_abbr})")
    print(f"版本: {response.v_name}")  # 1933年聖公會出版
    print(f"經文: {verse.text}")
    
    # 查詢整章次經
    verses = client.get_apocrypha_chapter(book_id=101, chapter=1)
    print(f"\n瑪加伯上 第1章 共 {len(verses)} 節")
    
    # 顯示前3節
    for verse_response in verses[:3]:
        v = verse_response.records[0]
        print(f"{v.get_reference()}: {v.text[:30]}...")

# 輸出範例:
# 書卷: 馬一 (1Mc)
# 版本: 1933年聖公會出版
# 經文: 在他們當中生了一條禍根...
```

### 9. 查詢使徒教父著作 (Apostolic Fathers)

查詢使徒教父著作 (編號 201-217)：

```python
with FHLBibleClient() as client:
    # 查詢革利免前書 1:1 (1 Clement)
    response = client.get_apostolic_fathers_verse(book_id=201, chapter=1, verse=1)
    verse = response.records[0]
    
    print(f"書卷: {verse.chinese_abbr} ({verse.english_abbr})")
    print(f"版本: {response.v_name}")  # 黃錫木主編《使徒教父著作》
    print(f"經文: {verse.text}")
    
    # 查詢整章
    verses = client.get_apostolic_fathers_chapter(book_id=201, chapter=1)
    print(f"\n革利免前書 第1章 共 {len(verses)} 節")
    
    # 顯示前3節
    for verse_response in verses[:3]:
        v = verse_response.records[0]
        print(f"{v.get_reference()}: {v.text[:40]}...")

# 輸出範例:
# 書卷: 革一 (1Clem)
# 版本: 黃錫木主編《使徒教父著作》
# 經文: 由於突然接二連三地臨到我們的不幸和災難...
```

### 10. 查詢聖經註釋

獲取經文的詳細註釋說明：

```python
with FHLBibleClient() as client:
    # 查詢創世記 1:9 的註釋
    response = client.get_commentary(book_id=1, chapter=1, verse=9)
    
    print(f"註釋筆數: {response.record_count}")
    
    for comm in response.records:
        print(f"\n標題: {comm.title}")
        print(f"來源: {comm.book_name}")
        print(f"內容: {comm.com_text[:100]}...")
    
    # 查看前後節
    if response.prev_verse:
        print(f"\n前一節註釋: {response.prev_verse.english_abbr} {response.prev_verse.chapter}:{response.prev_verse.verse}")
    if response.next_verse:
        print(f"下一節註釋: {response.next_verse.english_abbr} {response.next_verse.chapter}:{response.next_verse.verse}")

# 輸出範例:
# 註釋筆數: 1
# 標題: 創世記 1章9節 到 1章13節
# 來源: 信望愛站註釋
# 內容: 4.第三日的創造...
```

## 綜合經文分析範例

詳細的經文分析範例請參考 [example_verse_analysis.py](examples/example_verse_analysis.py)：

```python
# 此範例展示：
# - 多版本翻譯對照
# - 逐字原文解析（含 Strong's 編號）
# - 註釋整合
# - 格式化表格輸出

python examples/example_verse_analysis.py
```

範例分析哈巴谷書 2:1 和約翰福音 3:16，包含：
- 原文（希伯來文/希臘文）
- 原文直譯
- 多個中文譯本（中文和合本、呂振中譯本）
- 希伯來文/希臘文字彙分析（含 Strong's 編號）
- 信望愛站註釋詳細內容
- 經文導覽


### 7. 列出所有可用版本

```python
with FHLBibleClient() as client:
    versions = client.get_available_versions()
    
    # 顯示部分版本
    for code in ["unv", "rcuv", "kjv", "esv"]:
        print(f"{code}: {versions[code]}")
```

## 書卷編號對照

- **1-39**: 舊約 (創世記到瑪拉基書)
- **40-66**: 新約 (馬太福音到啟示錄)
- **101-115**: 次經
- **201-217**: 使徒教父著作

常用書卷編號：
- 1: 創世記
- 19: 詩篇
- 20: 箴言
- 23: 以賽亞書
- 40: 馬太福音
- 43: 約翰福音
- 45: 羅馬書

## 常用聖經版本

中文版本：
- `unv`: 和合本 (預設)
- `rcuv`: 和合本2010
- `tcv2019`: 現代中文譯本2019版
- `ncv`: 新譯本

英文版本：
- `kjv`: King James Version
- `esv`: English Standard Version
- `asv`: American Standard Version

## 錯誤處理

```python
from fhl_bible_api import (
    FHLBibleClient,
    InvalidBookError,
    InvalidVersionError,
    APIConnectionError,
)

try:
    with FHLBibleClient() as client:
        response = client.get_verse(book_id=1, chapter=1, verse=1)
        print(response.records[0].text)
except InvalidBookError as e:
    print(f"無效的書卷編號: {e}")
except InvalidVersionError as e:
    print(f"無效的聖經版本: {e}")
except APIConnectionError as e:
    print(f"連線錯誤: {e}")
```

## 進階功能

### 包含 Strong's Number

```python
with FHLBibleClient() as client:
    response = client.get_verse(
        book_id=1,
        chapter=1,
        verse=1,
        include_strong=True  # 包含原文編號
    )
```

### 使用簡體中文

```python
with FHLBibleClient() as client:
    response = client.get_verse(
        book_id=1,
        chapter=1,
        verse=1,
        simplified=True  # 使用簡體中文
    )
```

## 完整範例

查看 `example.py` 檔案以獲取更多使用範例。

執行範例：

```bash
uv run python example.py
```

## 更多資源

- [完整文檔](README.md)
- [發布指南](PUBLISHING.md)
- [變更日誌](CHANGELOG.md)
- [FHL 聖經 API](https://bible.fhl.net/api/)

## 版權與使用聲明

### 聖經內容版權

本 API 存取的所有聖經內容由 **信望愛資訊中心** 提供：

- **官方網站**: https://www.fhl.net/
- **聖經 API**: https://bible.fhl.net/
- **使用條款**: https://www.fhl.net/main/fhl/fhl8.html

聖經經文、翻譯及相關內容的版權歸屬其各自出版者與譯者：
- 和合本聖經 © 聖經公會
- 現代中文譯本 © 台灣聖經公會
- 其他譯本版權歸屬其各自出版者所有

### 使用須知

使用本函式庫及 FHL 聖經 API 時，請遵守以下原則：

1. **註明出處**：必須標示聖經內容來源為「信望愛資訊中心」
2. **非商業用途**：內容主要供非商業、教育及宗教服事使用
3. **尊重版權**：各聖經譯本有其各自的版權條款，使用時請予以尊重
4. **禁止轉載**：不得擅自將聖經內容從 API 分離並重新發布

**重要提醒**：本套件為非官方客戶端。使用者需自行負責遵守信望愛的服務條款以及各譯本的版權規定。

## 授權

MIT License

## 免責聲明

本套件為非官方客戶端函式庫。所有聖經內容由信望愛聖經 API 提供。
