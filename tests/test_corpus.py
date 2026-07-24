from pathlib import Path

from src.corpus import (
    DIFFICULTY_QUOTAS,
    SECTION_QUOTAS,
    TYPE_QUOTAS,
    load_questions,
    validate_questions,
)


ROOT = Path(__file__).resolve().parents[1]
CORPUS = ROOT / "content" / "questions.json"


def test_quota_totals_are_one_hundred() -> None:
    assert SECTION_QUOTAS == {1: 24, 2: 28, 3: 16, 4: 20, 5: 12}
    assert sum(SECTION_QUOTAS.values()) == 100
    assert sum(TYPE_QUOTAS.values()) == 100
    assert sum(DIFFICULTY_QUOTAS.values()) == 100


def test_final_corpus_is_complete_and_valid() -> None:
    assert CORPUS.exists(), "Run scripts/merge_corpus.py after authoring all three parts."
    questions = load_questions(CORPUS)
    assert validate_questions(questions, enforce_quotas=True) == []
