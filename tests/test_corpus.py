from copy import deepcopy
import json
from pathlib import Path

from src.corpus import (
    DIFFICULTY_QUOTAS,
    SECTION_QUOTAS,
    TYPE_QUOTAS,
    load_questions,
    validate_questions,
)
from src.source_lineage import (
    CATEGORY_RELATIONS,
    METHOD_FAMILY_REFERENCES,
    SOURCE_LINEAGE_CATEGORIES,
    SOURCE_REFERENCES,
)


ROOT = Path(__file__).resolve().parents[1]
CORPUS = ROOT / "content" / "questions.json"
SCHEMA = ROOT / "content" / "schema.json"
SOURCES = ROOT / "SOURCES.md"


def test_quota_totals_are_one_hundred() -> None:
    assert SECTION_QUOTAS == {1: 24, 2: 28, 3: 16, 4: 20, 5: 12}
    assert sum(SECTION_QUOTAS.values()) == 100
    assert sum(TYPE_QUOTAS.values()) == 100
    assert sum(DIFFICULTY_QUOTAS.values()) == 100


def test_final_corpus_is_complete_and_valid() -> None:
    assert CORPUS.exists(), "Run scripts/merge_corpus.py after authoring all three parts."
    questions = load_questions(CORPUS)
    assert validate_questions(questions, enforce_quotas=True) == []


def test_every_question_has_verifiable_source_lineage() -> None:
    questions = load_questions(CORPUS)
    assert len(questions) == 100
    assert {item["source_lineage"]["category"] for item in questions} == (
        SOURCE_LINEAGE_CATEGORIES
    )
    for item in questions:
        lineage = item["source_lineage"]
        assert lineage["category"] in SOURCE_LINEAGE_CATEGORIES
        assert lineage["relation"] == CATEGORY_RELATIONS[lineage["category"]]
        assert lineage["method_family"] in METHOD_FAMILY_REFERENCES
        assert lineage["references"]
        assert len(lineage["references"]) == len(set(lineage["references"]))
        assert set(lineage["references"]) <= set(SOURCE_REFERENCES)
        assert set(lineage["references"]) <= METHOD_FAMILY_REFERENCES[lineage["method_family"]]


def test_source_lineage_validation_rejects_false_or_unverifiable_claims() -> None:
    questions = load_questions(CORPUS)

    missing = deepcopy(questions)
    del missing[0]["source_lineage"]
    assert any("missing fields ['source_lineage']" in error for error in validate_questions(missing))

    unknown_reference = deepcopy(questions)
    unknown_reference[0]["source_lineage"]["references"] = ["copyrighted-textbook-unspecified"]
    assert any("unknown source reference" in error for error in validate_questions(unknown_reference))

    inconsistent_relation = deepcopy(questions)
    inconsistent_relation[0]["source_lineage"]["relation"] = (
        "independently_synthesized_from_standard_methods"
    )
    assert any("relation must be" in error for error in validate_questions(inconsistent_relation))


def test_source_lineage_schema_matches_runtime_registry() -> None:
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    lineage = schema["$defs"]["source_lineage"]["properties"]
    assert set(lineage["category"]["enum"]) == SOURCE_LINEAGE_CATEGORIES
    assert set(lineage["method_family"]["enum"]) == set(METHOD_FAMILY_REFERENCES)
    assert set(lineage["relation"]["enum"]) == set(CATEGORY_RELATIONS.values())
    assert set(lineage["references"]["items"]["enum"]) == set(SOURCE_REFERENCES)


def test_source_registry_is_documented_and_uses_official_open_hosts() -> None:
    documentation = SOURCES.read_text(encoding="utf-8")
    allowed_hosts = ("https://openstax.org/", "https://ocw.mit.edu/")
    for source_id, source in SOURCE_REFERENCES.items():
        assert f"`{source_id}`" in documentation
        assert source["url"].startswith(allowed_hosts)
        assert source["url"] in documentation


def test_formula_migration_golden_cases_preserve_semantics() -> None:
    questions = {item["id"]: item for item in load_questions(CORPUS)}

    assert questions["Q033"]["en"]["choices"][1].endswith(r"$(g\ne 0)$")
    assert r"\sqrt{4.04}" in questions["Q054"]["zh"]["prompt"]
    assert r"\sqrt{0.98}" in questions["Q081"]["zh"]["prompt"]
    assert r"\sqrt{25.5}" in questions["Q094"]["en"]["prompt"]

    q066 = questions["Q066"]
    assert r"e^{\sin(x^{2})}" in q066["zh"]["prompt"]
    assert r"\frac{2x e^{\sin(x^{2})}\cos(x^{2})}{1+e^{2\sin(x^{2})}}" in (
        q066["en"]["answer"]
    )

    assert r"\frac{d}{dt}\!\left(\frac{dy}{dx}\right)" in (
        questions["Q075"]["zh"]["solution"]["steps"][2]
    )
    assert r"\frac{1}{x'(t)}\frac{d}{dt}" in questions["Q091"]["en"]["answer"]
    assert r"(-1+h^{2})\,\mathrm{m}\,\mathrm{s}^{-1}" in (
        questions["Q063"]["en"]["answer"]
    )

    assert r"\mathrm{cm}^{3}\,\mathrm{min}^{-1}" in (
        questions["Q077"]["zh"]["answer"]
    )
    assert r"dA=2\pi r\,dr" in questions["Q080"]["en"]["solution"]["steps"][0]
    assert r"\mathrm{m}^{3}\,\mathrm{min}^{-1}" in (
        questions["Q092"]["en"]["answer"]
    )

    assert r"\sum_{k=0}^{n}" in questions["Q072"]["zh"]["solution"]["steps"][0]
    assert r"\sum_{j=0}^{n+1}" in questions["Q088"]["en"]["solution"]["steps"][5]
    assert r"y''=-\frac{\varphi''(x)}{\psi'(y)}" in (
        questions["Q099"]["en"]["prompt"]
    )
    for qid in ("Q059", "Q083", "Q097"):
        serialized = json.dumps(questions[qid], ensure_ascii=False)
        assert r"\\operatorname{sgn}" in serialized
        assert r"\\operatorname{\\operatorname" not in serialized

    serialized = json.dumps(list(questions.values()), ensure_ascii=False)
    assert "______" not in serialized
    assert r"\\Sigma" not in serialized
