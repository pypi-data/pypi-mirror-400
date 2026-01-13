import sqlite3
import json
import re
import logging
from pathlib import Path
from typing import List, Tuple, Optional, Union
from .models import AyahUnit, WordUnit, TajweedAnnotation
from .constants import CONSONANT_MAP, DIACRITIC_MAP, MUQATTAAT_MAP, ATOMIC_TOKEN_MAP

logger = logging.getLogger("QuranPhonemizer")


class QuranPhonemizer:
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = Path(db_path) if db_path else Path(__file__).parent / "assets" / "quran.db"
        if not self.db_path.exists():
            raise FileNotFoundError(f"Database not found at {self.db_path}. Please run db_builder.py")
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row

    def _normalize_for_search(self, text: str) -> str:
        text = text.replace('آ', 'ا')
        noise = re.compile(r"[\u064B-\u065F\u0670\u06D6-\u06ED\u0640\u0660-\u06690-9\uFD3E\uFD3F\u0653]")
        return re.sub(noise, "", text).strip()

    def _find_snippet_in_db(self, text: str) -> Optional[Tuple[int, int, int, int]]:
        """High-performance verse lookup using FTS5."""
        base_clean = self._normalize_for_search(text)
        words = base_clean.split()
        if not words: return None

        candidates = [base_clean]
        if 'ى' in base_clean: candidates.append(base_clean.replace('ى', 'ي'))
        if 'ي' in base_clean: candidates.append(base_clean.replace('ي', 'ى'))
        if 'ٱ' in base_clean: candidates.append(base_clean.replace('ٱ', 'ا'))
        if 'ا' in base_clean: candidates.append(base_clean.replace('ا', 'ٱ'))

        super_normalized = re.sub(r'[أإٱآ]', 'ا', base_clean)
        if super_normalized != base_clean:
            candidates.append(super_normalized)

        cursor = self.conn.cursor()

        for search_text in candidates:
            words_search = search_text.split()
            if not words_search: continue

            search_query = '"' + " ".join(words_search) + '"'

            try:
                sql = """
                    SELECT surah_num, ayah_num 
                    FROM quran_words_fts 
                    WHERE text_simple MATCH ? 
                    LIMIT 10
                """
                cursor.execute(sql, (search_query,))
                candidates_rows = cursor.fetchall()

                for cand in candidates_rows:
                    match = self._precise_alignment(cand['surah_num'], cand['ayah_num'], words_search)
                    if match: return match
            except sqlite3.OperationalError:
                continue

        return None

    def _precise_alignment(self, surah: int, ayah: int, search_words: List[str]) -> Optional[Tuple[int, int, int, int]]:
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT word_num, text_simple FROM quran_words WHERE surah_num = ? AND ayah_num = ? ORDER BY word_num",
            (surah, ayah))

        db_rows = cursor.fetchall()
        db_words = [
            (r['word_num'], self._normalize_for_search(r['text_simple']))
            for r in db_rows
            if self._normalize_for_search(r['text_simple'])
        ]

        L = len(search_words)

        def relax(w):
            return re.sub(r'[أإٱآ]', 'ا', w)

        for i in range(len(db_words) - L + 1):
            subset_db = [x[1] for x in db_words[i:i + L]]
            if subset_db == search_words:
                return (surah, ayah, db_words[i][0], db_words[i + L - 1][0])

            subset_relaxed = [relax(w) for w in subset_db]
            search_relaxed = [relax(w) for w in search_words]
            if subset_relaxed == search_relaxed:
                return (surah, ayah, db_words[i][0], db_words[i + L - 1][0])

        return None

    def tokenize_to_atomic(self, phoneme_string: str) -> List[str]:
        tokens = []
        sorted_keys = sorted(ATOMIC_TOKEN_MAP.keys(), key=len, reverse=True)
        for i, word in enumerate(phoneme_string.split(" ")):
            remainder = word
            while remainder:
                matched = False
                for key in sorted_keys:
                    if remainder.startswith(key):
                        tokens.append(ATOMIC_TOKEN_MAP[key])
                        remainder = remainder[len(key):]
                        matched = True
                        break
                if not matched: remainder = remainder[1:]
            if i < len(phoneme_string.split(" ")) - 1: tokens.append("SP")
        return tokens

    def _base_transliterate(self, text: str) -> str:
        if self._normalize_for_search(text) in MUQATTAAT_MAP:
            return MUQATTAAT_MAP[self._normalize_for_search(text)]

        text = re.sub(r'([\u064B-\u0650])\u0651', '\u0651\\1', text)
        if "للَّه" in text: text = text.replace("للَّه", "للَّٰه")

        output, skip_counter, last_v_type = [], 0, 'heavy'
        chars = [c for c in text if
                 c != '\u0640' and not ('\u06D6' <= c <= '\u06E4') and not ('\u06E7' <= c <= '\u06ED')]

        for i, char in enumerate(chars):
            if skip_counter > 0:
                skip_counter -= 1
                continue

            next_char = chars[i + 1] if i + 1 < len(chars) else None
            next_next_char = chars[i + 2] if i + 2 < len(chars) else None
            is_shadda_next = (next_char == '\u0651')

            if char == 'ل':
                is_preceded_by_wasl = (i > 0 and chars[i - 1] in ['ٱ', 'ا'])
                is_sun_letter_context = (i + 2 < len(chars)) and (chars[i + 2] == '\u0651')
                if is_preceded_by_wasl and is_sun_letter_context: continue

            current_is_fatha = (char == '\u064E')
            if current_is_fatha:
                if next_char == 'ى' and next_next_char == 'ٰ':
                    output.append('aa');
                    skip_counter = 2;
                    last_v_type = 'heavy';
                    continue
                if next_char == 'و' and next_next_char == 'ٰ':
                    output.append('aa');
                    skip_counter = 2;
                    last_v_type = 'heavy';
                    continue
                if next_char in ['ا', 'ى', 'ٰ', 'آ']:
                    output.append('aa');
                    skip_counter = 1;
                    last_v_type = 'heavy';
                    continue

            phoneme = ""
            if char == '\u0654':
                phoneme = '2'
            elif char in CONSONANT_MAP:
                if char == 'ى' and i > 0 and chars[i - 1] == '\u0650':
                    phoneme = 'y'
                else:
                    raw_phoneme = CONSONANT_MAP[char]
                    phoneme = raw_phoneme
                    if raw_phoneme == 'r':
                        if next_char in ['\u064E', '\u064F', '\u064B', '\u064C', 'ا', 'ٰ']:
                            phoneme = 'R'
                        elif next_char in ['\u0650', '\u064D', 'ي', 'ى']:
                            phoneme = 'r'
                        elif next_char == '\u0652':
                            phoneme = 'R' if last_v_type == 'heavy' else 'r'
                        else:
                            if is_shadda_next and next_next_char in ['\u064E', '\u064F', '\u064B', '\u064C', 'ا', 'ٰ']:
                                phoneme = 'R'
                            elif is_shadda_next and next_next_char in ['\u0650', '\u064D', 'ي', 'ى']:
                                phoneme = 'r'
                            else:
                                phoneme = 'R'

                if is_shadda_next:
                    phoneme += phoneme;
                    skip_counter = 1
                    if char in ['ن', 'م']: phoneme += "ŋ"

            elif char in DIACRITIC_MAP:
                if char != '\u0651':
                    phoneme = DIACRITIC_MAP[char]
                    if char in ['\u064E', '\u064F', '\u064B', '\u064C']:
                        last_v_type = 'heavy'
                    elif char in ['\u0650', '\u064D']:
                        last_v_type = 'light'

                    # Fix Tanween Fath + Alif/Yaa/Dagger (e.g. naaran, hudan)
                    # Added 'ى' to skip list to fix 'hudanaa' -> 'hudan'
                    if char == '\u064B' and next_char in ['ا', 'ٰ', 'آ', 'ى']:
                        skip_counter = 1

            if char == 'و' and next_char == 'ا':
                skip_counter = 1

            output.append(phoneme)
        return "".join(output)

    def apply_tajweed_rules(self, base: str, rules: List[TajweedAnnotation]) -> str:
        if "::" in base and " " in base: return base
        p = base

        QALQ_SET = {'q', 'T', 'b', 'j', 'd'}

        for r in [ra.rule.lower() for ra in rules]:
            if "iqlab" in r:
                p = p.replace('n', 'm') + "ŋ"
            elif "qalqalah" in r:
                if p and p[-1] in QALQ_SET:
                    if "_Q" not in p: p += "_Q"
            elif "ghunnah" in r or "ikhfa" in r:
                if "ŋ" not in p: p += "ŋ"
            elif any(x in r for x in ["madd_6", "lazim"]):
                if ":::" not in p: p += ":::"
            elif any(x in r for x in ["madd_4", "madd_5", "muttasil", "munfasil"]):
                if "::" not in p: p += "::"
            elif any(x in r for x in ["madd_2", "normal"]):
                if ":" not in p and "::" not in p: p += ":"
        return p

    def _apply_stopping_rules(self, word_input: Union[str, WordUnit], phonemes: str) -> str:
        if "::" in phonemes and " " in phonemes: return phonemes
        text_uthmani = word_input.text_uthmani if isinstance(word_input, WordUnit) else str(word_input)
        uthmani_strip = text_uthmani.strip()

        core_phonemes = phonemes
        found_markers = []
        markers = [":::", "::", ":", "_Q", "ŋ"]

        while True:
            stripped = False
            for m in markers:
                if core_phonemes.endswith(m):
                    core_phonemes = core_phonemes[:-len(m)]
                    found_markers.insert(0, m)
                    stripped = True
                    break
            if not stripped: break

        restored_suffix = ""
        for m in found_markers:
            if m == "ŋ":
                if core_phonemes.endswith(('nn', 'mm')):
                    restored_suffix += m
            elif m == "_Q":
                pass
            else:
                restored_suffix += m

        suffix = restored_suffix

        if uthmani_strip.endswith(('ة', 'ةِ', 'ةُ', 'ةَ')):
            if core_phonemes.endswith(('t', 'ta', 'ti', 'tu', 'tan', 'tin', 'tun')):
                return re.sub(r't(a|i|u|an|in|un)?$', 'h', core_phonemes) + suffix

        if core_phonemes.endswith('an'):
            return core_phonemes[:-2] + 'aa' + suffix

        if core_phonemes.endswith(('aa', 'ii', 'uu')):
            pass
        elif core_phonemes.endswith(('in', 'un')):
            core_phonemes = core_phonemes[:-2]
        elif core_phonemes.endswith(('i', 'u', 'a')):
            core_phonemes = core_phonemes[:-1]

        QALQALAH_LETTERS = ['q', 'T', 'b', 'j', 'd']
        if core_phonemes and core_phonemes[-1] in QALQALAH_LETTERS:
            if "_Q" not in suffix: suffix += "_Q"

        return core_phonemes + suffix

    def _apply_connection_rules(self, current_pho: str, next_pho: str) -> str:
        if not next_pho: return current_pho
        if "::" in current_pho and " " in current_pho: return current_pho

        clean_current = current_pho
        for m in ["_Q", "ŋ", ":::", "::", ":"]:
            if clean_current.endswith(m):
                clean_current = clean_current[:-len(m)]

        first_char = next_pho[0] if next_pho else ""

        if clean_current.endswith('n'):
            if first_char in ['y', 'r', 'm', 'l', 'w', 'n', 'R']:
                # Check for Idgham Bilaghunnah (L, R)
                is_bilaghunnah = first_char in ['l', 'r', 'R']

                # Check if next word is ALREADY doubled (contains Shadda)
                # Heuristic: Starts with doubled char or Heavy counterpart
                is_next_doubled = False
                if len(next_pho) >= 2 and next_pho[0] == next_pho[1]: is_next_doubled = True
                if next_pho.startswith("LL") or next_pho.startswith("RR"): is_next_doubled = True

                prefix, match, suffix = current_pho.rpartition('n')
                if match == 'n':
                    # If next is already doubled, we just drop the 'n' (Assimilation)
                    # e.g. hudan + llil -> huda llil
                    if is_next_doubled:
                        replacement = ""
                    else:
                        replacement = first_char

                    # Remove Ghunnah if Bilaghunnah (L/R)
                    if is_bilaghunnah and suffix == 'ŋ':
                        suffix = ""

                    current_pho = prefix + replacement + suffix

            elif first_char == 'b':
                prefix, match, suffix = current_pho.rpartition('n')
                if match == 'n': current_pho = prefix + 'm' + suffix
        return current_pho

    def _apply_ibtida_rules(self, word_input: Union[str, WordUnit], phonemes: str) -> str:
        if "::" in phonemes and " " in phonemes: return phonemes
        text_uthmani = word_input.text_uthmani if isinstance(word_input, WordUnit) else str(word_input)
        text_uthmani = text_uthmani.strip()
        if text_uthmani.startswith('ٱ'):
            if text_uthmani.startswith('ٱل'):
                if text_uthmani.startswith('ٱللَّ'):
                    phonemes = phonemes.replace('ll', 'LL', 1)
                    return '2a' + phonemes
                return '2a' + phonemes
            return '2i' + phonemes
        return phonemes

    def phonemize_text(self, text: str, start_of_sentence: bool = True, end_of_sentence: bool = True,
                       segment_separator: str = " ", apply_stopping_rules: bool = True) -> str:
        match = self._find_snippet_in_db(text)
        words_to_process = []
        is_db_source = False

        if match:
            surah, ayah, start_w, end_w = match
            full_ayah = self.get_ayah(surah, ayah)
            words_to_process = [w for w in full_ayah.words if start_w <= w.word_position <= end_w]
            is_db_source = True

        else:
            split_pattern = r'[۝۞\u06DD\u0660-\u0669\d]+'
            segments = re.split(split_pattern, text)
            non_empty_segments = [s.strip() for s in segments if s.strip()]

            if len(non_empty_segments) > 1:
                results = []
                for i, segment in enumerate(non_empty_segments):
                    is_first = (i == 0)
                    is_last = (i == len(non_empty_segments) - 1)
                    seg_start = start_of_sentence if is_first else (False if not apply_stopping_rules else True)
                    seg_end = end_of_sentence if is_last else apply_stopping_rules
                    res = self.phonemize_text(segment, start_of_sentence=seg_start, end_of_sentence=seg_end,
                                              segment_separator=segment_separator,
                                              apply_stopping_rules=apply_stopping_rules)
                    results.append(res)
                return segment_separator.join(results)

            words_raw = text.strip().split()
            words_to_process = words_raw
            is_db_source = False

        phonemes = []
        count = len(words_to_process)
        for i, item in enumerate(words_to_process):
            if is_db_source:
                pho, word_ref, base_iso = item.phonemes_connected, item, item.phonemes_isolated
            else:
                word_ref, base_iso = item, self._base_transliterate(item)
                if not base_iso:
                    if phonemes:
                        phonemes[-1] = self._apply_stopping_rules(words_to_process[i - 1], phonemes[-1])
                    continue
                next_item = words_to_process[i + 1] if i + 1 < count else None
                if next_item:
                    next_base = self._base_transliterate(next_item)
                    pho = self._apply_connection_rules(base_iso, next_base) if next_base else base_iso
                else:
                    pho = base_iso

            if i == 0 and start_of_sentence: pho = self._apply_ibtida_rules(word_ref, pho)
            if i > 0 and pho.startswith('llaa'):
                prev = phonemes[-1] if phonemes else ""
                if prev.endswith(('a', 'u', 'aa', 'uu', 'w')): pho = pho.replace('ll', 'LL', 1)

            if i == count - 1:
                if end_of_sentence:
                    if is_db_source:
                        pho = self._apply_stopping_rules(word_ref, base_iso)
                    else:
                        pho = self._apply_stopping_rules(word_ref, base_iso)
                else:
                    if is_db_source: pho = base_iso

            phonemes.append(pho)

        return " ".join(phonemes)

    def get_ayah(self, surah: int, ayah: int) -> AyahUnit:
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM quran_words WHERE surah_num = ? AND ayah_num = ? ORDER BY word_num",
                       (surah, ayah))
        rows = cursor.fetchall()
        word_objs = []
        for r in rows:
            rules = [TajweedAnnotation(rule=j['rule'], start_index=j['start'], end_index=j['end']) for j in
                     json.loads(r['rules_json'])]
            iso = self._base_transliterate(r['text_uthmani'])
            processed_pho = self.apply_tajweed_rules(iso, rules)
            word_objs.append({'data': r, 'rules': rules, 'pho_base': processed_pho})

        for i in range(len(word_objs)):
            current = word_objs[i]
            next_w = word_objs[i + 1] if i + 1 < len(word_objs) else None
            pho_connected = self._apply_connection_rules(current['pho_base'],
                                                         word_objs[i + 1]['pho_base']) if next_w else current[
                'pho_base']
            final_pho = pho_connected
            if not next_w:
                dummy_w = WordUnit(location_id="0", surah=0, ayah=0, word_position=0,
                                   text_uthmani=current['data']['text_uthmani'], text_simple="", phonemes_isolated="",
                                   phonemes_connected="", rules=[])
                final_pho = self._apply_stopping_rules(dummy_w, current['pho_base'])

            current['final_obj'] = WordUnit(
                location_id=current['data']['id'],
                surah=current['data']['surah_num'],
                ayah=current['data']['ayah_num'],
                word_position=current['data']['word_num'],
                text_uthmani=current['data']['text_uthmani'],
                text_simple=current['data']['text_simple'],
                phonemes_isolated=current['pho_base'],
                phonemes_connected=final_pho,
                rules=current['rules']
            )
        final_words = [w['final_obj'] for w in word_objs]
        return AyahUnit(surah=surah, ayah=ayah, text_uthmani=" ".join([w.text_uthmani for w in final_words]),
                        words=final_words)

    def close(self) -> None:
        self.conn.close()