-- Drop existing tables if they exist
DROP TABLE IF EXISTS quran_words;
DROP TABLE IF EXISTS quran_words_fts;

-- Main word table
CREATE TABLE quran_words (
    id TEXT PRIMARY KEY,
    surah_num INTEGER,
    ayah_num INTEGER,
    word_num INTEGER,
    text_uthmani TEXT,
    text_simple TEXT,
    rules_json TEXT
);

-- FTS5 Virtual Table for Ayah-level searching
-- Stores the FULL text of the ayah to allow phrase matching
CREATE VIRTUAL TABLE quran_words_fts USING fts5(
    text_simple,
    surah_num UNINDEXED,
    ayah_num UNINDEXED
);