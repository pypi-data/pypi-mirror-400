import streamlit as st
import sys
import os
import pandas as pd
import re

# Add project root to path so we can import the src module
sys.path.append(os.path.abspath("."))

from src.quran_phonemizer.core import QuranPhonemizer

# --- Page Configuration ---
st.set_page_config(
    page_title="Quran Phonemizer Demo",
    page_icon="📖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom CSS for RTL, Fonts, and Dark Mode Support ---
st.markdown("""
    <style>
    /* Import Arabic Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Noto+Naskh+Arabic:wght@400;700&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Scheherazade+New:wght@400;700&display=swap');

    /* Target all text areas (Input and Output) for Quranic Text */
    .stTextArea textarea {
        direction: rtl;
        text-align: right;
        font-family: 'Scheherazade New', 'Noto Naskh Arabic', serif;
        font-size: 26px !important;
        line-height: 2.2 !important;
    }

    /* Input Labels */
    .stTextArea label {
        font-size: 18px;
        font-weight: bold;
    }

    /* Footer Links */
    a {
        text-decoration: none;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# --- Title & Intro ---
st.title("📖 Quran Phonemizer Live Demo")
st.markdown("""
**Industrial-strength Deterministic Phonemizer** for Quranic Arabic. 
Generates context-aware, Tajweed-compliant phonemes for TTS and AI Reciter models.
""")


# --- Initialize Engine ---
def load_engine():
    try:
        return QuranPhonemizer()
    except FileNotFoundError:
        return None


phonemizer = load_engine()

# Error Handling for DB
if not phonemizer:
    st.error("🚨 **Database not found!**")
    st.markdown("Please run the database builder first:")
    st.code("python src/quran_phonemizer/db_builder.py", language="bash")
    st.stop()

# --- Sidebar: Configuration ---
st.sidebar.title("⚙️ Configuration")

with st.sidebar.expander("🗣️ Linguistics", expanded=True):
    enable_ibtida = st.checkbox(
        "Start of Sentence Rule (Ibtida')",
        value=True,
        help="Pronounce initial Hamzat Wasl (e.g. 'Allahu' instead of 'llahu')."
    )
    enable_waqf = st.checkbox(
        "End of Sentence Rule (Waqf)",
        value=True,
        help="Apply stopping rules to the last word (e.g. 'Ahad' instead of 'Ahadun')."
    )

st.sidebar.markdown("---")
st.sidebar.info(
    "This engine uses a **Hybrid Architecture**: Database Lookup for exact Quran matches, and Rule-Based Fallback for general Arabic.")

# --- Layout ---
tab1, tab2 = st.tabs(["🔢 Select by Number", "🔍 Search by Text"])

selected_surah = 112
selected_ayah = 1
# Mode flags
mode = None  # "full_ayah", "snippet", "fallback", "multi_match"
snippet_indices = None  # (start_idx, end_idx) 1-based
fallback_text = ""
multi_results = []  # List of result dicts for multi-match

with tab1:
    col1, col2 = st.columns(2)
    with col1:
        num_surah_input = st.number_input("Surah Number", min_value=1, max_value=114, value=112)
    with col2:
        num_ayah_input = st.number_input("Ayah Number", min_value=1, value=1)

    if st.button("Phonemize Selection", type="primary", use_container_width=True):
        selected_surah = num_surah_input
        selected_ayah = num_ayah_input
        mode = "full_ayah"

with tab2:
    st.info("Paste any Arabic text. Supports Snippets, Tatweels (ـ), and Numbers.")
    # Changed to text_area for wrapping and better UI
    text_query = st.text_area("Paste Text (Arabic)", height=150,
                              placeholder="e.g. وَإِذْ قَالَ رَبُّكَ لِلْمَلَـٰٓئِكَةِ")

    if st.button("Search & Phonemize", type="primary", use_container_width=True):
        if text_query:
            with st.spinner("Searching database..."):
                # 1. Attempt Multi-Verse Split (Splitting by Verse Numbers)
                chunks = re.split(r'[\u0660-\u06690-9]+', text_query)
                chunks = [c.strip() for c in chunks if c.strip()]

                matches = []
                failed_chunks = []

                for chunk in chunks:
                    match = phonemizer._find_snippet_in_db(chunk)
                    if match:
                        matches.append((match, chunk))
                    else:
                        failed_chunks.append(chunk)

                # Logic to determine mode
                if failed_chunks or len(matches) == 0:
                    whole_match = phonemizer._find_snippet_in_db(text_query)

                    if whole_match:
                        surah, ayah, start_w, end_w = whole_match
                        selected_surah = surah
                        selected_ayah = ayah
                        mode = "snippet"
                        snippet_indices = (start_w, end_w)
                        st.success(f"✅ Found in Surah {surah}, Ayah {ayah} (Words {start_w}-{end_w})")
                    else:
                        st.warning(
                            "⚠️ Text not found in exact Quran Database (or spans multiple verses without separators). Switching to **Fallback Mode**.")
                        mode = "fallback"
                        fallback_text = text_query

                elif len(matches) > 0:
                    mode = "multi_match"
                    multi_results = matches
                    st.success(f"✅ Found {len(matches)} matching segments in Database.")


# --- DISPLAY LOGIC ---

def display_phonetic_table(words_to_show):
    table_data = []
    full_phonemes = []

    for i, word in enumerate(words_to_show):
        rules_list = [r.rule for r in word.rules]
        rules_display = ", ".join(rules_list) if rules_list else "—"

        # Determine phoneme to show
        is_last_in_selection = (i == len(words_to_show) - 1)

        # 1. Base Phoneme
        if is_last_in_selection and enable_waqf:
            pho = phonemizer._apply_stopping_rules(word, word.phonemes_isolated)
        else:
            pho = word.phonemes_connected
            # If user disabled waqf, but it is the last word, we might want isolated form?
            # Core logic usually handles connection. If waqf is disabled,
            # we keep the connected form (which has the vowel).
            if is_last_in_selection and not enable_waqf:
                pho = word.phonemes_isolated  # Isolated form usually has the vowel/tanween

        # 2. Ibtida
        if i == 0 and enable_ibtida:
            pho = phonemizer._apply_ibtida_rules(word, pho)

        # Collect data for table
        table_data.append({
            "Position": word.word_position,
            "Uthmani": word.text_uthmani,
            "Base (Isolated)": word.phonemes_isolated,
            "Contextual (Final)": pho,
            "Tajweed Rules": rules_display
        })

        full_phonemes.append(pho)

    # 1. Full Phonetic String
    st.info("**Full Phonetic String (Context-Aware):**")
    st.code(" ".join(full_phonemes), language="text")

    # 2. Detailed Token Table
    df = pd.DataFrame(table_data)
    st.dataframe(
        df,
        column_config={
            "Uthmani": st.column_config.TextColumn("Uthmani", help="Original Text"),
            "Contextual (Final)": st.column_config.TextColumn("Connected", help="Pronunciation with Wasl/Waqf applied"),
        },
        use_container_width=True,
        hide_index=True
    )


# --- Render Results ---

if mode in ["full_ayah", "snippet"]:
    st.divider()
    try:
        result = phonemizer.get_ayah(selected_surah, selected_ayah)
        words_to_show = result.words
        is_partial = False

        if mode == "snippet" and snippet_indices:
            start_w, end_w = snippet_indices
            words_to_show = result.words[start_w - 1: end_w]
            if len(words_to_show) < len(result.words):
                is_partial = True

        label_text = f"Surah {selected_surah}, Ayah {selected_ayah}" + (" (Snippet)" if is_partial else "")
        st.subheader(label_text)

        # Using text_area for display to handle Dark Mode and wrapping correctly
        display_text = " ".join([w.text_uthmani for w in words_to_show])
        st.text_area("Quranic Text", value=display_text, height=200, key="display_ayah")

        st.subheader("Phonetic Analysis (Database Mode)")
        display_phonetic_table(words_to_show)

    except Exception as e:
        st.error(f"Error fetching Ayah: {str(e)}")

elif mode == "multi_match":
    st.divider()
    st.subheader("Multi-Verse Analysis")

    for idx, (match_data, original_chunk) in enumerate(multi_results):
        surah, ayah, start_w, end_w = match_data

        # Fetch Data
        result = phonemizer.get_ayah(surah, ayah)
        words_to_show = result.words[start_w - 1: end_w]

        st.markdown(f"#### Segment {idx + 1}: Surah {surah}, Ayah {ayah}")

        display_text = " ".join([w.text_uthmani for w in words_to_show])
        # Unique key for each text area in loop
        st.text_area(f"Segment {idx + 1}", value=display_text, height=100, key=f"seg_{idx}")

        display_phonetic_table(words_to_show)
        st.markdown("---")

elif mode == "fallback":
    st.divider()
    st.subheader("Result (Fallback Mode)")

    # Using text_area for display
    st.text_area("Input Text", value=fallback_text, height=200, key="display_fallback")

    # Generate Phonemes using the new method with config
    ipa_output = phonemizer.phonemize_text(
        fallback_text,
        start_of_sentence=enable_ibtida,
        end_of_sentence=enable_waqf
    )

    st.info("**Generated Phonetic String:**")
    st.code(ipa_output, language="text")

    st.caption("""
    **Note:** Fallback mode uses standard rule-based transliteration. 
    It handles Short Vowels, Shadda, Sun Letters, and Basic Stops, but does not include 
    advanced Tajweed rules (like Madd 6 counts) which require database validation.
    """)

# --- Footer ---
st.markdown("---")
col_footer_1, col_footer_2, col_footer_3 = st.columns([1, 4, 1])
with col_footer_2:
    st.markdown(
        """
        <div style='text-align: center;'>
            <b>Developed by Razwan M. Haji</b><br>
            <a href="https://github.com/RazwanSiktany/quran-phonemizer" target="_blank">GitHub Repo</a> | 
            <a href="https://pypi.org/project/quran-phonemizer/" target="_blank">PyPI Package</a><br>
            <br>
            <small style='color: grey;'>Built with ❤️ for Quranic AI Technology</small>
        </div>
        """,
        unsafe_allow_html=True
    )