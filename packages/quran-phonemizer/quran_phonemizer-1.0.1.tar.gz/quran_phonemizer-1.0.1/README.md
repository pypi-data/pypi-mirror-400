# 📖 quran-phonemizer

[![PyPI version](https://badge.fury.io/py/quran-phonemizer.svg)](https://badge.fury.io/py/quran-phonemizer)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://quran-phonemizer.streamlit.app/)

**quran-phonemizer** is an industrial-strength, **Tajweed-aware** phonemization library designed specifically for **Quranic Arabic**.

It uses a **Hybrid Architecture** combining a "Golden Source" database (82,000+ expert-verified words) with a robust rule-based fallback engine. This ensures the accuracy for Quranic text while gracefully handling Hadith, poetry, or imperfect input.

It is specifically optimized for training **Neural TTS** models (VITS, FastSpeech2) in the style of reciters like **Mishary Al-Afasy**.

---

## 🚀 Live Demo

Try the library instantly in your browser:
👉 **[Click here to open the Live App](https://quran-phonemizer.streamlit.app/)**

Or run it locally:
```bash
pip install streamlit
streamlit run demo_app.py
```

---

## ⚡ Quick Start

```python
from quran_phonemizer import QuranPhonemizer

# 1. Initialize Engine (Loads bundled DB)
qp = QuranPhonemizer()

# 2. Phonemize Quranic Text (Database Mode)
text = "ٱللَّهُ ٱلصَّمَدُ"
phonemes = qp.phonemize_text(text)

print(phonemes)
# Output: 2aLLaahu SSamad_Q
# (Note: '2a' = Glottal Stop, 'LL' = Heavy Lam, '_Q' = Qalqalah on Stop)

# 3. Get Atomic Tokens for ML Training (VITS format)
tokens = qp.tokenize_to_atomic(phonemes)
print(tokens)
# Output: ['2', 'a', 'L_H', 'aa', 'h', 'u', 'SP', 'S', 'S', 'a', 'm', 'a', 'd', 'u', 'QK']
```

---

## 🎛️ Advanced Configuration

You can customize how verses are connected or separated.

```python
# Multi-Verse Input
text = "بِسْمِ ٱللَّهِ ٱلرَّحْمَـٰنِ ٱلرَّحِيمِ ١ ٱلْحَمْدُ لِلَّهِ رَبِّ ٱلْعَـٰلَمِينَ ٢"

# Option A: Standard Stop (Waqf) at each Ayah
print(qp.phonemize_text(text, segment_separator=" | "))
# Output: ...RRaHiym: | 2alHamdu...

# Option B: Continuous Recitation (Wasl)
print(qp.phonemize_text(text, apply_stopping_rules=False))
# Output: ...RRaHiymi lHamdu...
# (Note: Preserves vowel 'i' and merges Hamzat Wasl)
```

---

## 🌟 Key Features

### 1. 🕌 High-Fidelity Tajweed
Captures nuances that standard Arabic G2P tools miss:
* **Heavy/Light Letters (Tafkhim/Tarqiq):**
    * Distinguishes **Heavy Lam** (`LL`) in "Allah" vs **Light Lam** (`ll`).
    * Distinguishes **Heavy Ra** (`R`) vs **Light Ra** (`r`).
* **Madd (Elongation):** Numeric markers for duration (`:` = 2, `::` = 4, `:::` = 6 counts).
* **Qalqalah (Echo):** Automatically adds `_Q` when stopping on Qaf, Taa, Ba, Jim, Dal.
* **Ghunnah (Nasal):** Marks nasalization (`ŋ`) for Noon/Meem Shadda.
* **Idgham/Iqlab:** Merges sounds across word boundaries (e.g. `min ba'di` -> `mim ba'di`).

### 2. 🧠 ML-Ready Tokenization
Includes a tokenizer that converts human-readable strings into **Atomic Tokens** for model training.
* **Separated Phonemes:** `in` becomes `['i', 'n']`.
* **Symbol Mapping:** `_Q` becomes `QK`, `LL` becomes `L_H`.
* **Word Boundaries:** Inserts `SP` tokens automatically.

### 3. 🛡️ Robust Search & Fallback
* **FTS5 Search:** Instantly finds verses even with missing diacritics or spelling variations.
* **Smart Normalization:** Handles `Tatweel` (ـ), `Alif Khanjareeya` (ٰ), and `Hamza` forms transparently.
* **Fallback Engine:** If text is not in the Quran, a sophisticated rule-based engine generates phonetically accurate approximations.

---

## 📦 Installation & Setup

```bash
pip install quran-phonemizer
```

*(The Golden Source database is included automatically)*

---

## 👨‍💻 Author

**Razwan M. Haji**
* **GitHub:** [RazwanSiktany](https://github.com/RazwanSiktany/)
* **PyPI:** [quran-phonemizer](https://pypi.org/project/quran-phonemizer/)

## 📄 License

This project is licensed under the [MIT License](https://opensource.org/licenses/MIT).