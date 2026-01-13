import sqlite3
import json
import re
import logging
from pathlib import Path
from typing import List, Tuple, Dict, Any

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("DBBuilder")

CURRENT_SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_SCRIPT_DIR.parent.parent
DATA_DIR = PROJECT_ROOT / "data"
DB_PATH = CURRENT_SCRIPT_DIR / "assets" / "quran.db"
SCHEMA_PATH = CURRENT_SCRIPT_DIR / "resources" / "schema.sql"


class QuranParser:
    def __init__(self, db_path: Path):
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()

    def init_db(self, schema_path: Path):
        if not schema_path.exists():
            raise FileNotFoundError(f"Schema file not found at {schema_path}")

        with open(schema_path, 'r', encoding='utf-8') as f:
            self.cursor.executescript(f.read())
        self.conn.commit()
        logger.info("Database and FTS5 index initialized.")

    def simple_tokenize(self, text: str) -> List[str]:
        return [w for w in text.strip().split(' ') if w]

    def normalize_text(self, text: str) -> str:
        """
        Robust normalization matching core.py logic.
        Ensures DB index matches search queries perfectly.
        """
        # 1. Normalize Alif Madda (آ) to Alif (ا)
        text = text.replace('آ', 'ا')

        # 2. Remove all diacritics, tatweels, and symbols
        noise = re.compile(r"[\u064B-\u065F\u0670\u06D6-\u06ED\u0640\u0653]")
        return re.sub(noise, "", text).strip()

    def process_text_file(self, file_path: Path):
        logger.info(f"Processing text file: {file_path}")
        self.cursor.execute("DELETE FROM quran_words")
        # We also need to clear the detached FTS table manually now
        self.cursor.execute("DELETE FROM quran_words_fts")

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        except UnicodeDecodeError:
            with open(file_path, 'r', encoding='utf-8-sig') as f:
                lines = f.readlines()

        batch_data = []
        fts_data = []
        BISMILLAH = "بِسْمِ ٱللَّهِ ٱلرَّحْمَـٰنِ ٱلرَّحِيمِ"

        for line in lines:
            line = line.strip()
            if not line or '|' not in line: continue
            parts = line.split('|')
            if len(parts) < 3: continue

            surah, ayah = int(parts[0]), int(parts[1])
            text = parts[2].strip()

            # Remove Bismillah from start of Ayah 1 (except Surah 1)
            if surah > 1 and ayah == 1:
                if text.startswith(BISMILLAH):
                    text = text[len(BISMILLAH):].strip()

            if not text: continue

            # 1. Prepare FTS Data (Full Ayah Normalization)
            # This allows searching for phrases like "maliki nnas"
            full_text_simple = self.normalize_text(text)
            fts_data.append((full_text_simple, surah, ayah))

            # 2. Prepare Word Data
            words = self.simple_tokenize(text)
            for i, word in enumerate(words):
                location_id = f"{surah}:{ayah}:{i + 1}"
                text_simple = self.normalize_text(word)
                batch_data.append((location_id, surah, ayah, i + 1, word, text_simple, "[]"))

        # Insert Words
        self.cursor.executemany("""
            INSERT INTO quran_words (id, surah_num, ayah_num, word_num, text_uthmani, text_simple, rules_json)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, batch_data)

        # Insert FTS Data (Aggregated Ayahs)
        self.cursor.executemany("""
            INSERT INTO quran_words_fts (text_simple, surah_num, ayah_num)
            VALUES (?, ?, ?)
        """, fts_data)

        self.conn.commit()
        logger.info(f"Inserted {len(batch_data)} words and updated FTS5 index with {len(fts_data)} ayahs.")

    def process_tajweed_json(self, json_path: Path):
        logger.info(f"Processing Tajweed JSON: {json_path}")
        with open(json_path, 'r', encoding='utf-8') as f:
            tajweed_data = json.load(f)

        self.cursor.execute(
            "SELECT id, surah_num, ayah_num, text_uthmani FROM quran_words ORDER BY surah_num, ayah_num, word_num")
        all_words = self.cursor.fetchall()

        ayah_map = {}
        for row in all_words:
            key = (row['surah_num'], row['ayah_num'])
            if key not in ayah_map: ayah_map[key] = []
            ayah_map[key].append({'id': row['id'], 'text': row['text_uthmani'], 'rules': []})

        BISMILLAH_FULL = "بِسْمِ ٱللَّهِ ٱلرَّحْمَـٰنِ ٱلرَّحِيمِ "
        B_OFFSET = len(BISMILLAH_FULL)

        for entry in tajweed_data:
            surah = entry.get('surah') or entry.get('s')
            ayah = entry.get('ayah') or entry.get('a')
            annotations = entry.get('annotations', [])
            words_in_ayah = ayah_map.get((surah, ayah))
            if not words_in_ayah or not annotations: continue

            offset = B_OFFSET if (surah > 1 and ayah == 1) else 0

            current_char_idx = 0
            word_ranges = []
            for w_obj in words_in_ayah:
                w_len = len(w_obj['text'])
                word_ranges.append((current_char_idx, current_char_idx + w_len, w_obj))
                current_char_idx += w_len + 1

            for rule in annotations:
                r_start, r_end = rule['start'], rule['end']
                if offset > 0:
                    if r_end <= offset: continue
                    r_start = max(0, r_start - offset)
                    r_end = max(0, r_end - offset)

                for (w_start, w_end, w_obj) in word_ranges:
                    if max(r_start, w_start) < min(r_end, w_end):
                        w_obj['rules'].append({
                            'rule': rule['rule'],
                            'start': max(0, r_start - w_start),
                            'end': min(w_end - w_start, r_end - w_start)
                        })

        updates = [(json.dumps(w['rules']), w['id']) for words in ayah_map.values() for w in words if w['rules']]
        self.cursor.executemany("UPDATE quran_words SET rules_json = ? WHERE id = ?", updates)
        self.conn.commit()
        logger.info(f"Phase 2: Mapped rules to {len(updates)} words.")


def main():
    if not DB_PATH.parent.exists(): DB_PATH.parent.mkdir(parents=True)
    parser = QuranParser(DB_PATH)
    parser.init_db(SCHEMA_PATH)
    parser.process_text_file(DATA_DIR / "quran-uthmani.txt")
    parser.process_tajweed_json(DATA_DIR / "tajweed.hafs.uthmani-pause-sajdah.json")
    logger.info("Rebuild complete.")


if __name__ == "__main__":
    main()