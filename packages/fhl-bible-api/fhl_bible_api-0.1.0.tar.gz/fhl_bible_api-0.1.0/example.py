"""Example script demonstrating FHL Bible API usage.

Copyright Notice:
    All Bible content is provided by 信望愛資訊中心 (Faith, Hope, Love Information Center).
    Website: https://www.fhl.net/
    Please comply with their terms of service and respect Bible translation copyrights.

    版權聲明：所有聖經內容由信望愛資訊中心提供。
    請遵守其服務條款並尊重各譯本版權。
"""

from fhl_bible_api import FHLBibleClient


def main() -> None:
    """Run example queries."""
    # Create client using context manager
    with FHLBibleClient() as client:
        print("=" * 60)
        print("FHL Bible API Client - Example Usage")
        print("=" * 60)
        print("\n📖 聖經資料來源：信望愛資訊中心 (https://www.fhl.net/)")
        print("📖 Bible data: Faith, Hope, Love Information Center")
        print("=" * 60)

        # Example 1: Get a single verse
        print("\n1. Get Genesis 1:1")
        print("-" * 60)
        response = client.get_verse(book_id=1, chapter=1, verse=1)
        verse = response.records[0]
        print(f"Reference: {verse.get_reference()}")
        print(f"Text: {verse.text}")

        # Example 2: Get a verse in different version
        print("\n2. Get John 3:16 in KJV")
        print("-" * 60)
        response = client.get_verse(book_id=43, chapter=3, verse=16, version="kjv")
        if response.records:
            verse = response.records[0]
            print(f"Reference: {verse.get_reference(use_english=True)}")
            print(f"Text: {verse.text}")

        # Example 3: Search for a book
        print("\n3. Search for books")
        print("-" * 60)
        results = client.search_book_by_name("創")
        for book_id, book_info in results[:3]:
            print(f"  {book_id}: {book_info['full_name']} ({book_info['english']})")

        # Example 4: Get book information
        print("\n4. Get book information")
        print("-" * 60)
        info = client.get_book_info(19)  # Psalms
        print(f"Book: {info['full_name']}")
        print(f"Chinese: {info['chinese']}")
        print(f"English: {info['english']}")

        # Example 5: Get first 5 verses of a chapter
        print("\n5. Get Psalm 23 (first 5 verses)")
        print("-" * 60)
        chapter_responses = client.get_chapter(book_id=19, chapter=23)
        for resp in chapter_responses[:5]:
            if resp.records:
                verse = resp.records[0]
                print(f"{verse.get_reference()}: {verse.text}")

        # Example 6: List some available versions
        print("\n6. Available Bible versions (sample)")
        print("-" * 60)
        versions = client.get_available_versions()
        sample_versions = ["unv", "rcuv", "kjv", "esv", "tcv2019"]
        for code in sample_versions:
            if code in versions:
                print(f"  {code}: {versions[code]}")

        # Example 7: Word Parsing (原文字彙分析)
        print("\n7. Word Parsing for John 3:16")
        print("-" * 60)
        parsing = client.get_word_parsing(book_id=43, chapter=3, verse=16)
        print(f"Testament: {'New Testament (新約)' if parsing.testament == 0 else 'Old Testament (舊約)'}")
        print(f"Total words: {len([w for w in parsing.records if w.word_id > 0])}")
        print("\nFirst 3 words:")
        word_count = 0
        for word in parsing.records:
            if word.word_id > 0 and word_count < 3:
                print(f"\n  Word #{word.word_id}: {word.word}")
                if word.strong_number:
                    print(f"    Strong's: {word.strong_number}")
                if word.part_of_speech:
                    print(f"    Part of Speech: {word.part_of_speech}")
                if word.original_form:
                    print(f"    Original: {word.original_form}")
                if word.explanation:
                    print(f"    Meaning: {word.explanation}")
                word_count += 1

        print("\n" + "=" * 60)
        print("Examples completed!")
        print("=" * 60)


if __name__ == "__main__":
    main()
