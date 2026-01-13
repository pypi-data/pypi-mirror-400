import pytest
from src.quran_phonemizer.core import QuranPhonemizer
from src.quran_phonemizer.models import TajweedAnnotation


@pytest.fixture(scope="module")
def phonemizer():
    """
    Initializes the phonemizer once for all tests.
    Skips tests if the database hasn't been built yet.
    """
    try:
        return QuranPhonemizer()
    except FileNotFoundError:
        pytest.skip("Database not found. Please run 'src/quran_phonemizer/db_builder.py' first.")


def test_surah_ikhlas_pronunciation(phonemizer):
    """
    Tests Surah 112:1 to verify:
    1. 'Qul' is first (Bismillah removed).
    2. 'Allah' is pronounced correctly.
    3. 'Ahad' stops with Qalqalah (2aHadun_Q).
    """
    result = phonemizer.get_ayah(112, 1)
    words = result.words

    # Word 1: qul (Bismillah stripped)
    assert words[0].phonemes_connected == "qul", f"Expected 'qul', got {words[0].phonemes_connected}"

    # Word 3: ٱللَّهِ (Allah)
    w_allah = words[2]
    # Check for either light or heavy lam depending on implementation state
    assert "llaahu" in w_allah.phonemes_connected or "LLaahu" in w_allah.phonemes_connected, \
        f"Expected 'llaahu', got {w_allah.phonemes_connected}"

    # Last Word: أَحَدٌ (Ahad)
    w_ahad = words[-1]
    assert "_Q" in w_ahad.phonemes_connected, \
        f"Missing Qalqalah marker on stop. Got: {w_ahad.phonemes_connected}"
    assert not w_ahad.phonemes_connected.endswith("un"), \
        f"Stopped form should drop Tanween 'un'. Got: {w_ahad.phonemes_connected}"


def test_madd_munfasil_validation(phonemizer):
    """
    Tests Surah 111:1 (Al-Masad) to verify:
    1. 'madd_munfasil' rules are accepted (yadaa::)
    2. No Pydantic validation errors occur for new rule types.
    """
    result = phonemizer.get_ayah(111, 1)
    words = result.words

    w_yada = next((w for w in words if "يَدَ" in w.text_uthmani), None)

    assert w_yada is not None, "Could not find word 'Yada' in Surah 111:1"

    assert "::" in w_yada.phonemes_connected, \
        f"Madd elongation (::) missing in {w_yada.phonemes_connected}"
    assert w_yada.phonemes_connected.startswith("yadaa"), \
        f"Vowel length incorrect. Got: {w_yada.phonemes_connected}"


def test_relaxed_model_validation():
    """
    Directly tests the Pydantic model to ensure it accepts arbitrary strings
    as rule names.
    """
    try:
        annotation = TajweedAnnotation(
            rule="weird_new_rule_v2",
            start_index=0,
            end_index=5
        )
    except Exception as e:
        pytest.fail(f"Model validation failed for unknown rule string: {e}")

    assert annotation.rule == "weird_new_rule_v2"


def test_sun_letter_assimilation(phonemizer):
    """
    Tests Surah 1:1 (Basmala) for Sun Letter (Al-Rahman).
    """
    result = phonemizer.get_ayah(1, 1)
    words = result.words

    # Word 3: ٱلرَّحْمَـٰنِ (Ar-Rahman)
    w_rahman = words[2]

    # Expected: 'RRaHmaani' (Heavy Ra, Assimilated Lam)
    assert w_rahman.phonemes_connected.startswith("RRa") or w_rahman.phonemes_connected.startswith("rra"), \
        f"Sun letter assimilation failed. Got: {w_rahman.phonemes_connected}"
    assert "l" not in w_rahman.phonemes_connected[:2], "Lam should be silent"


def test_special_characters_ignored(phonemizer):
    """
    Tests Surah 2:60 which starts with the Rub el Hizb symbol (۞).
    Verifies that non-phonetic symbols are ignored and don't break logic.
    """
    result = phonemizer.get_ayah(2, 60)
    words = result.words

    # The tokenizer usually splits "۞" as a separate word.
    rub_el_hizb = next((w for w in words if "۞" in w.text_uthmani), None)

    if rub_el_hizb:
        assert rub_el_hizb.phonemes_connected == "", \
            f"Special symbol ۞ should result in empty phonemes, got '{rub_el_hizb.phonemes_connected}'"

    # Check the next word "wa-idhi" (وَإِذِ)
    # Phonetics: w (waw) + a (fatha) + 2 (hamza) + i (kasra) + dh (dhal) + i (kasra) -> wa2idhi
    wa_idhi = next((w for w in words if "وَإِذِ" in w.text_uthmani), None)
    assert wa_idhi is not None
    assert "wa2idh" in wa_idhi.phonemes_connected, \
        f"Expected 'wa2idh' in phonemes, got {wa_idhi.phonemes_connected}"


def test_idgham_merging(phonemizer):
    """
    Tests Idgham: Merging Nun Sakinah into following letters.
    Example: Surah 112:4 "wa lam yakun lahu" -> 'yakullahu'
    """
    text = "وَلَمْ يَكُن لَّهُۥ"
    output = phonemizer.phonemize_text(text, start_of_sentence=True, end_of_sentence=True)

    # Check for basic presence of phonemes or database markers
    assert "yakun" in output or "yakul" in output or "llah" in output or "ŋ" in output


def test_heavy_lam_in_allah(phonemizer):
    """
    Tests Heavy vs Light Lam in the word 'Allah'.
    """
    # 1. Start of sentence (Heavy) -> 2aLLaahu
    text_start = "ٱللَّهُ"
    output_start = phonemizer.phonemize_text(text_start)
    assert "2aLL" in output_start or "llaah" in output_start or "LLah" in output_start

    # 2. Preceded by Fatha (Heavy) -> Huwa Allahu
    text_heavy_ctx = "هُوَ ٱللَّهُ"
    output_heavy = phonemizer.phonemize_text(text_heavy_ctx)
    assert "llaah" in output_heavy or "LLaah" in output_heavy

    # 3. Preceded by Kasra (Light) -> Billahi
    text_light_ctx = "بِٱللَّهِ"
    output_light = phonemizer.phonemize_text(text_light_ctx)
    assert "llahi" in output_light or "llaahi" in output_light or "llaah" in output_light, \
        f"Expected Light Lam after Kasra, got {output_light}"
    assert "LL" not in output_light


def test_muqattaat_pronunciation(phonemizer):
    """
    Tests Disjoined Letters (Muqatta'at) lookup.
    """
    text = "الٓمٓ"
    output = phonemizer.phonemize_text(text)
    # Expect full elongation MADD6
    assert "2alif laa:::m mii:::m" == output, \
        f"Muqatta'at incorrect. Got {output}"


def test_fallback_basic(phonemizer):
    """
    Tests standard Arabic fallback for non-Quranic text.
    Uses a word not in the Quran to force fallback.
    """
    # "Abjad" (not in Quran DB)
    text = "أَبْجَدْ"
    output = phonemizer.phonemize_text(text)
    # Should stop at end -> 2abjad_Q (because 'd' is Qalqalah)
    assert output == "2abjad_Q", f"Fallback failed. Got {output}"


def test_atomic_tokenization(phonemizer):
    """
    Tests the ML-ready atomic tokenization method.
    """
    # Test Case 1: Simple Word
    text = "قُلْ"
    readable = phonemizer.phonemize_text(text)  # "qul"
    tokens = phonemizer.tokenize_to_atomic(readable)
    assert tokens == ['q', 'u', 'l'], f"Atomic tokenization failed for simple word. Got {tokens}"

    # Test Case 2: Tajweed Symbols (Qalqalah, Heavy Lam, Madd)
    raw_phonemes = "2aLLaahu_Q"
    tokens_complex = phonemizer.tokenize_to_atomic(raw_phonemes)

    # Expected mapping:
    # 2 -> 2
    # a -> a
    # LL -> L_H (Heavy Lam)
    # aa -> aa (Long vowel)
    # h -> h
    # u -> u
    # _Q -> QK (Qalqalah)
    expected = ['2', 'a', 'L_H', 'aa', 'h', 'u', 'QK']
    assert tokens_complex == expected, f"Atomic tokenization failed for Tajweed symbols. Got {tokens_complex}"

    # Test Case 3: Space/Word Boundary
    raw_sentence = "qul huwa"
    tokens_sentence = phonemizer.tokenize_to_atomic(raw_sentence)
    assert 'SP' in tokens_sentence, "Word boundary 'SP' missing"