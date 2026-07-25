from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

from src.source_lineage import (
    CATEGORY_RELATIONS,
    METHOD_FAMILY_REFERENCES,
    SOURCE_LINEAGE_CATEGORIES,
    SOURCE_REFERENCES,
)


SECTION_QUOTAS = {1: 24, 2: 28, 3: 16, 4: 20, 5: 12}
TYPE_QUOTAS = {
    "single_choice": 10,
    "multiple_choice": 6,
    "true_false": 8,
    "fill_blank": 10,
    "calculation": 36,
    "proof": 18,
    "comprehensive": 8,
    "error_diagnosis": 4,
}
DIFFICULTY_QUOTAS = {
    "basic": 22,
    "standard": 33,
    "advanced": 27,
    "hard": 14,
    "challenge": 4,
}
VALID_TIERS = {"foundation", "methods", "synthesis", "challenge"}
VALID_SPACES = {"S", "M", "L", "XL"}
REQUIRED_LOCALIZED = {"title", "prompt", "answer", "solution"}
REQUIRED_SOLUTION = {
    "knowledge",
    "analysis",
    "steps",
    "pitfalls",
    "verification",
    "takeaway",
    "extension",
}
REQUIRED_SOURCE_LINEAGE = {
    "category",
    "method_family",
    "relation",
    "references",
}


def load_questions(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, list):
        raise ValueError("Question corpus must be a JSON array.")
    return value


def _quota_errors(label: str, actual: Counter, expected: dict) -> list[str]:
    errors: list[str] = []
    for key, count in expected.items():
        if actual[key] != count:
            errors.append(f"{label} quota {key!r}: expected {count}, got {actual[key]}")
    extra = set(actual) - set(expected)
    if extra:
        errors.append(f"{label} has unsupported values: {sorted(extra)!r}")
    return errors


def _source_lineage_errors(item_id: str, item: dict[str, Any]) -> list[str]:
    prefix = f"{item_id}: source_lineage "
    lineage = item.get("source_lineage")
    if not isinstance(lineage, dict):
        return [prefix + "must be an object"]

    errors: list[str] = []
    missing = sorted(REQUIRED_SOURCE_LINEAGE - set(lineage))
    if missing:
        errors.append(prefix + f"missing fields {missing}")
        return errors
    extra = sorted(set(lineage) - REQUIRED_SOURCE_LINEAGE)
    if extra:
        errors.append(prefix + f"has unsupported fields {extra}")

    category = lineage["category"]
    if category not in SOURCE_LINEAGE_CATEGORIES:
        errors.append(prefix + f"has unsupported category {category!r}")
    else:
        expected_relation = CATEGORY_RELATIONS[category]
        if lineage["relation"] != expected_relation:
            errors.append(prefix + f"relation must be {expected_relation!r} for category {category!r}")

    method_family = lineage["method_family"]
    if method_family not in METHOD_FAMILY_REFERENCES:
        errors.append(prefix + f"has unsupported method_family {method_family!r}")

    references = lineage["references"]
    if not isinstance(references, list) or not references:
        errors.append(prefix + "references must be a non-empty array")
    else:
        if len(references) != len(set(references)):
            errors.append(prefix + "references must not contain duplicates")
        unknown = sorted(set(references) - set(SOURCE_REFERENCES))
        if unknown:
            errors.append(prefix + f"contains unknown source reference(s) {unknown}")
        if method_family in METHOD_FAMILY_REFERENCES:
            unrelated = sorted(set(references) - METHOD_FAMILY_REFERENCES[method_family])
            if unrelated:
                errors.append(
                    prefix
                    + f"contains reference(s) not registered for {method_family!r}: {unrelated}"
                )

    if not item.get("classic_method") and category != "original_synthesis":
        errors.append(
            prefix
            + "category must be 'original_synthesis' when classic_method is false"
        )
    return errors


def validate_questions(items: list[dict[str, Any]], enforce_quotas: bool = True) -> list[str]:
    errors: list[str] = []
    if enforce_quotas and len(items) != 100:
        errors.append(f"Expected 100 questions, got {len(items)}")

    ids = [str(item.get("id", "")) for item in items]
    duplicates = sorted(item_id for item_id, count in Counter(ids).items() if count > 1)
    if duplicates:
        errors.append(f"Duplicate IDs: {duplicates}")

    if enforce_quotas:
        expected_ids = [f"Q{index:03d}" for index in range(1, 101)]
        if ids != expected_ids:
            errors.append("IDs must be ordered exactly Q001-Q100")

    for index, item in enumerate(items, start=1):
        item_id = item.get("id", f"item-{index}")
        prefix = f"{item_id}: "
        required = {
            "id",
            "section",
            "tier",
            "difficulty",
            "type",
            "tags",
            "minutes",
            "space",
            "classic_method",
            "source_lineage",
            "zh",
            "en",
        }
        missing = sorted(required - set(item))
        if missing:
            errors.append(prefix + f"missing fields {missing}")
            continue
        if item["tier"] not in VALID_TIERS:
            errors.append(prefix + f"unsupported tier {item['tier']!r}")
        if item["space"] not in VALID_SPACES:
            errors.append(prefix + f"unsupported space {item['space']!r}")
        if not isinstance(item["minutes"], int) or not 2 <= item["minutes"] <= 45:
            errors.append(prefix + "minutes must be an integer from 2 through 45")
        if not isinstance(item["classic_method"], bool):
            errors.append(prefix + "classic_method must be boolean")
        errors.extend(_source_lineage_errors(str(item_id), item))

        tags = item["tags"]
        if not isinstance(tags, dict) or not tags.get("zh") or not tags.get("en"):
            errors.append(prefix + "tags must contain non-empty zh and en arrays")

        for language in ("zh", "en"):
            localized = item[language]
            if not isinstance(localized, dict):
                errors.append(prefix + f"{language} must be an object")
                continue
            localized_missing = sorted(REQUIRED_LOCALIZED - set(localized))
            if localized_missing:
                errors.append(prefix + f"{language} missing {localized_missing}")
                continue
            if not str(localized["prompt"]).strip():
                errors.append(prefix + f"{language} prompt is empty")
            if not str(localized["answer"]).strip():
                errors.append(prefix + f"{language} answer is empty")
            solution = localized["solution"]
            if not isinstance(solution, dict):
                errors.append(prefix + f"{language}.solution must be an object")
                continue
            solution_missing = sorted(REQUIRED_SOLUTION - set(solution))
            if solution_missing:
                errors.append(prefix + f"{language}.solution missing {solution_missing}")
                continue
            if len(solution["steps"]) < 2:
                errors.append(prefix + f"{language}.solution needs at least two steps")
            if not solution["knowledge"] or not solution["pitfalls"]:
                errors.append(prefix + f"{language}.solution knowledge/pitfalls cannot be empty")

        if item["type"] in {"single_choice", "multiple_choice"}:
            for language in ("zh", "en"):
                if len(item[language].get("choices", [])) < 4:
                    errors.append(prefix + f"{language} choice question needs at least four choices")

    if enforce_quotas:
        errors.extend(_quota_errors("section", Counter(item.get("section") for item in items), SECTION_QUOTAS))
        errors.extend(_quota_errors("type", Counter(item.get("type") for item in items), TYPE_QUOTAS))
        errors.extend(
            _quota_errors(
                "difficulty",
                Counter(item.get("difficulty") for item in items),
                DIFFICULTY_QUOTAS,
            )
        )
    return errors
