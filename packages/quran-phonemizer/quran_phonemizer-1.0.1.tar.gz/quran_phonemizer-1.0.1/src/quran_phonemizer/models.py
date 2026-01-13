from pydantic import BaseModel, Field
from typing import List, Optional, Literal, Union


# We relax the strict Literal type to 'str' in the model to handle
# all variations found in the JSON dataset (e.g., madd_munfasil, madd_lazim).
# We keep the Literal for documentation purposes if needed, or remove it.

class TajweedAnnotation(BaseModel):
    """
    Represents a specific rule applied to a specific range of characters.
    """
    # Changed from Literal[...] to str to prevent validation errors on unknown rules
    rule: str
    start_index: int
    end_index: int
    meta: Optional[str] = None


class WordUnit(BaseModel):
    """
    Represents a single word in the Quran.
    """
    location_id: str  # Format: "S:A:W" (e.g. "112:1:1")
    surah: int
    ayah: int
    word_position: int

    text_uthmani: str  # The raw text with diacritics
    text_simple: str  # Text without diacritics (for searching)

    phonemes_isolated: Optional[str] = None
    phonemes_connected: Optional[str] = None

    rules: List[TajweedAnnotation] = Field(default_factory=list)


class AyahUnit(BaseModel):
    surah: int
    ayah: int
    text_uthmani: str
    words: List[WordUnit]