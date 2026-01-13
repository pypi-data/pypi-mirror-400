"""Example: Comprehensive Verse Analysis - 哈巴谷書 2:1

This example demonstrates how to combine multiple API calls to create
a comprehensive analysis of a Bible verse, including:
- Literal translation from original languages (原文直譯)
- Multiple Chinese translations (和合本, 呂振中譯本)
- Word-by-word parsing with Strong's numbers
- Commentary notes

Copyright Notice:
    All Bible content is provided by 信望愛資訊中心 (Faith, Hope, Love Information Center).
    Website: https://www.fhl.net/
"""

from fhl_bible_api import FHLBibleClient


def print_section(title: str, content: str = "") -> None:
    """Print a formatted section."""
    print(f"\n{'=' * 70}")
    print(f"  {title}")
    print('=' * 70)
    if content:
        print(content)


def format_parsing_table(words: list) -> str:
    """Format word parsing data into a table."""
    lines = []
    lines.append("\n| 序 | 原文字 | SN | 詞性 | 原型 | 簡義 |")
    lines.append("|---|--------|-----|------|------|------|")
    
    for idx, word in enumerate(words, 1):
        if word.word_id > 0:  # Skip summary record
            lines.append(
                f"| {idx} | {word.word} | "
                f"{word.strong_number or 'N/A'} | "
                f"{word.part_of_speech or 'N/A'} | "
                f"{word.original_form or 'N/A'} | "
                f"{word.explanation or 'N/A'} |"
            )
    
    return "\n".join(lines)


def analyze_verse(book_id: int, chapter: int, verse: int) -> None:
    """Perform comprehensive analysis of a Bible verse.
    
    Args:
        book_id: Book ID (e.g., 35 for Habakkuk)
        chapter: Chapter number
        verse: Verse number
    """
    with FHLBibleClient() as client:
        # Get book information
        book_info = client.get_book_info(book_id)
        verse_ref = f"{book_info['full_name']} {chapter}:{verse}"
        
        print_section(f"📖 經文分析：{verse_ref}")
        
        # 1. Display translations
        print_section("一、多版本對照")
        
        # 原文 (BHS for OT, try to get original text from parsing for NT)
        response_bhs = client.get_verse(book_id=book_id, chapter=chapter, verse=verse, version="bhs")
        if response_bhs.records and response_bhs.records[0].text.strip():
            print(f"\n【1. 原文】")
            print(response_bhs.records[0].text)
        else:
            # For NT, extract from parsing
            parsing_temp = client.get_word_parsing(book_id=book_id, chapter=chapter, verse=verse)
            if parsing_temp.records:
                original_words = [word.word for word in parsing_temp.records if word.word_id > 0 and word.word]
                if original_words:
                    print(f"\n【1. 原文】")
                    print(" ".join(original_words))
        
        # 原文直譯 (CBOL)
        response_cbol = client.get_verse(book_id=book_id, chapter=chapter, verse=verse, version="cbol")
        if response_cbol.records:
            print(f"\n【2. 原文直譯】")
            print(response_cbol.records[0].text)
        
        # 中文和合本 (UNV)
        response_unv = client.get_verse(book_id=book_id, chapter=chapter, verse=verse, version="unv")
        if response_unv.records:
            print(f"\n【3. 中文和合本】")
            print(response_unv.records[0].text)
        
        # 呂振中譯本 (LCC)
        response_lzz = client.get_verse(book_id=book_id, chapter=chapter, verse=verse, version="lcc")
        if response_lzz.records:
            print(f"\n【4. 呂振中譯本】")
            print(response_lzz.records[0].text)
        
        # 2. Detailed word parsing analysis
        print_section("二、原文字彙分析")
        
        parsing = client.get_word_parsing(book_id=book_id, chapter=chapter, verse=verse)
        
        if parsing.records:
            testament = "舊約 (OT)" if parsing.testament == 1 else "新約 (NT)"
            word_count = len([w for w in parsing.records if w.word_id > 0])
            print(f"\n約別: {testament}")
            print(f"詞彙總數: {word_count} 個")
            
            # Print parsing table
            print(format_parsing_table(parsing.records))
            
            # Show detailed analysis for first 5 words
            print("\n\n【前 5 個詞詳細分析】")
            count = 0
            for word in parsing.records:
                if word.word_id > 0 and count < 5:
                    print(f"\n詞 #{word.word_id}: {word.word}")
                    if word.strong_number:
                        print(f"  Strong's Number: {word.strong_number}")
                    if word.part_of_speech:
                        print(f"  詞性: {word.part_of_speech}")
                    if word.word_form:
                        print(f"  字彙分析: {word.word_form}")
                    if word.original_form:
                        print(f"  原型: {word.original_form}")
                    if word.explanation:
                        print(f"  簡義: {word.explanation}")
                    if word.remark:
                        print(f"  備註: {word.remark}")
                    count += 1
        
        # 3. Get commentary
        print_section("三、經文註釋")
        
        commentary = client.get_commentary(book_id=book_id, chapter=chapter, verse=verse)
        
        if commentary.records:
            for comm in commentary.records:
                print(f"\n【{comm.book_name}】")
                print(f"範圍: {comm.title}")
                print(f"\n{comm.com_text[:500]}...")
                if len(comm.com_text) > 500:
                    print(f"\n(註釋內容共 {len(comm.com_text)} 字，以上為前 500 字)")
        else:
            print("\n(本節無可用註釋)")
        
        print("\n" + "=" * 70)
        print("  分析完成！")
        print("=" * 70 + "\n")


def main() -> None:
    """Run the comprehensive verse analysis example."""
    print("\n" + "=" * 70)
    print("  FHL Bible API - 綜合經文分析範例")
    print("=" * 70)
    print("\n📖 資料來源：信望愛資訊中心 (https://www.fhl.net/)")
    print("=" * 70)
    
    # Example 1: Habakkuk 2:1 (哈巴谷書 2:1)
    print("\n\n範例一：哈巴谷書 2:1 詳細分析")
    analyze_verse(book_id=35, chapter=2, verse=1)
    
    # Example 2: John 3:16 (約翰福音 3:16) - New Testament example
    print("\n\n範例二：約翰福音 3:16 詳細分析")
    analyze_verse(book_id=43, chapter=3, verse=16)


if __name__ == "__main__":
    main()
