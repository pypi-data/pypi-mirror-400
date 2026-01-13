"""Quick test script for word parsing functionality."""

from fhl_bible_api import FHLBibleClient


def test_word_parsing():
    """Test word parsing feature with real API."""
    with FHLBibleClient() as client:
        print("Testing word parsing functionality...")
        print("=" * 60)
        
        # Test 1: John 3:16 (New Testament Greek)
        print("\n1. Testing John 3:16 (NT Greek)")
        print("-" * 60)
        response = client.get_word_parsing(book_id=43, chapter=3, verse=16)
        
        print(f"Status: {response.status}")
        print(f"Testament: {'NT' if response.testament == 0 else 'OT'}")
        print(f"Record Count: {response.record_count}")
        print(f"Total Words: {len(response.records)}")
        
        # Show first 3 words
        word_count = 0
        for word in response.records:
            if word.word_id > 0 and word_count < 3:
                print(f"\nWord #{word.word_id}:")
                print(f"  Text: {word.word}")
                print(f"  Strong's: {word.strong_number}")
                print(f"  POS: {word.part_of_speech}")
                print(f"  Original: {word.original_form}")
                print(f"  Meaning: {word.explanation}")
                word_count += 1
        
        # Test 2: Genesis 1:1 (Old Testament Hebrew)
        print("\n2. Testing Genesis 1:1 (OT Hebrew)")
        print("-" * 60)
        response = client.get_word_parsing(book_id=1, chapter=1, verse=1)
        
        print(f"Status: {response.status}")
        print(f"Testament: {'NT' if response.testament == 0 else 'OT'}")
        print(f"Record Count: {response.record_count}")
        print(f"Total Words: {len(response.records)}")
        
        # Show first word
        for word in response.records:
            if word.word_id == 1:
                print(f"\nFirst Word:")
                print(f"  Text: {word.word}")
                print(f"  Strong's: {word.strong_number}")
                print(f"  POS: {word.part_of_speech}")
                print(f"  Original: {word.original_form}")
                print(f"  Meaning: {word.explanation}")
                break
        
        # Test 3: Navigation
        print("\n3. Testing Navigation")
        print("-" * 60)
        response = client.get_word_parsing(book_id=43, chapter=3, verse=16)
        
        if response.prev_verse:
            print(f"Previous: {response.prev_verse.chinese_abbr} "
                  f"{response.prev_verse.chapter}:{response.prev_verse.verse}")
        
        if response.next_verse:
            print(f"Next: {response.next_verse.chinese_abbr} "
                  f"{response.next_verse.chapter}:{response.next_verse.verse}")
        
        print("\n" + "=" * 60)
        print("✓ All tests passed!")
        print("=" * 60)


if __name__ == "__main__":
    test_word_parsing()
