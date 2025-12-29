from dataclasses import dataclass
from typing import Optional
from db.model import Word


@dataclass
class WordInput:
    word: str
    meaning: str
    category: Optional[str] = None
    memo: Optional[str] = None


def build_word_entity(data: WordInput) -> Word:
    return Word(
        word=data.word.strip(),
        meaning=data.meaning.strip(),
        category=(data.category.strip() if data.category else None),
        memo=(data.memo.strip() if data.memo else None),
    )
