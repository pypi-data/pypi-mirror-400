import sys
import os

sys.path.append(os.path.abspath("."))
from src.quran_phonemizer.core import QuranPhonemizer


def main():
    USER_TEXT = "إِنَّهُۥ مِن سُلَيْمَـٰنَ وَإِنَّهُۥ بِسْمِ ٱللَّهِ ٱلرَّحْمَـٰنِ ٱلرَّحِيمِ"

    print("Initializing Quran Phonemizer Engine...")
    try:
        qp = QuranPhonemizer()
        print("✅ Engine loaded.\n")
    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
        return

    print("=== Phase 3: ML Atomic Tokenization Test ===")
    print(f"Input Text: {USER_TEXT}")

    # 1. Get Human-Readable Phonemes
    readable_phonemes = qp.phonemize_text(USER_TEXT)
    print(f"\n[Human Readable]:\n{readable_phonemes}")

    # 2. Get Atomic Tokens (for ML)
    atomic_tokens = qp.tokenize_to_atomic(readable_phonemes)
    print(f"\n[ML Atomic Tokens]:\n{atomic_tokens}")

    print("\n--- Summary ---")
    print(f"Total Words: {len(USER_TEXT.split())}")
    print(f"Total Tokens: {len(atomic_tokens)}")
    print(f"Atomic Tokens per Word average: {len(atomic_tokens) / len(USER_TEXT.split()):.2f}")


if __name__ == "__main__":
    main()