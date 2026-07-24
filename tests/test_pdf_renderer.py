from pathlib import Path

import pdfplumber
from pypdf import PdfReader

from src.corpus import load_questions, validate_questions
from src.pdf_renderer import (
    EXERCISE_SIZE,
    SOLUTION_SIZE,
    _normalize_math_markup,
    _safe,
    build_exercises,
    build_solutions,
)


ROOT = Path(__file__).resolve().parents[1]


def test_chapter_two_math_markup_normalization() -> None:
    rendered = _normalize_math_markup(
        r"\left(\arctan x+\sec x+\csc x+\mathrm{d}y\right)^\prime"
    )
    assert rendered == "(arctan x+sec x+csc x+dy)^′"
    assert "\\" not in rendered


def test_missing_math_glyphs_receive_font_fallbacks() -> None:
    rendered = _safe("eᵃˣ, y⁽ᵏ⁾, Hₘ, Hₙ")
    assert '<font name="WorkbookModifier">ᵃˣ</font>' in rendered
    assert '<font name="WorkbookModifier">ᵏ</font>' in rendered
    assert '<font name="WorkbookSubscript">ₘ</font>' in rendered
    assert '<font name="WorkbookSubscript">ₙ</font>' in rendered


def _assert_size(reader: PdfReader, expected: tuple[float, float]) -> None:
    page = reader.pages[0]
    actual = (float(page.mediabox.width), float(page.mediabox.height))
    assert abs(actual[0] - expected[0]) < 1
    assert abs(actual[1] - expected[1]) < 1


def test_smoke_build_first_two_questions(tmp_path: Path) -> None:
    corpus = ROOT / "content" / "questions.json"
    assert corpus.exists()
    questions = load_questions(corpus)
    assert validate_questions(questions) == []
    sample = questions[:2]

    exercises = tmp_path / "exercises.pdf"
    solutions = tmp_path / "solutions.pdf"
    build_exercises(sample, "zh", exercises)
    build_solutions(sample, "en", solutions)

    exercise_reader = PdfReader(exercises)
    solution_reader = PdfReader(solutions)
    _assert_size(exercise_reader, EXERCISE_SIZE)
    _assert_size(solution_reader, SOLUTION_SIZE)
    assert len(exercise_reader.pages) >= 5
    assert len(solution_reader.pages) >= 5

    with pdfplumber.open(exercises) as pdf:
        text = "\n".join(page.extract_text() or "" for page in pdf.pages)
    assert "Q001" in text and "Q002" in text
    assert "\x00" not in text

    with pdfplumber.open(solutions) as pdf:
        solution_text = "\n".join(page.extract_text() or "" for page in pdf.pages)
    assert "Q001" in solution_text and "Q002" in solution_text
    assert "\x00" not in solution_text
