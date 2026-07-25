from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.source_lineage import CATEGORY_RELATIONS, METHOD_FAMILY_REFERENCES


# These are conventional exercise archetypes whose topic, method, or applied
# context is directly represented in the open references.  The wording and
# numerical details in this repository remain independently authored.
OPEN_TEXT_ADAPTATION_TITLES = {
    "辨认导数定义",
    "用极限表示瞬时速度",
    "在非零点由定义求导",
    "可导是否保证连续",
    "由导数写切线方程",
    "绝对值函数的左右导数",
    "由定义求切线与法线",
    "选择对数函数的导数",
    "一次函数的五次幂",
    "识别隐函数的一阶导数",
    "圆上一点的切线",
    "识别函数微分",
    "倒数函数在任意非零点的导数",
    "用无穷小余项证明可导必连续",
    "证明平移绝对值在尖点不可导",
    "膨胀球体的体积变化率",
    "用微分近似平方根",
    "滑动梯子的线速度与角速度",
    "圆面积的绝对与相对误差估计",
}


def _searchable(item: dict[str, Any]) -> str:
    return " ".join(
        [
            str(item["zh"]["title"]),
            *[str(tag) for tag in item["tags"]["zh"]],
            *[str(tag) for tag in item["tags"]["en"]],
        ]
    ).lower()


def infer_method_family(item: dict[str, Any]) -> str:
    text = _searchable(item)
    section = int(item["section"])

    if "相关变化率" in text or "related rate" in text:
        return "related_rates"
    if "参数方程" in text or "参数曲线" in text or "parametric" in text:
        return "parametric_differentiation"
    if "隐函数" in text or "隐式" in text or "implicit" in text:
        return "implicit_differentiation"
    if section == 5 or any(
        marker in text
        for marker in (
            "微分",
            "线性近似",
            "相对误差",
            "绝对误差",
            "differential",
            "linear approximation",
            "measurement error",
        )
    ):
        return "differentials_and_linear_approximation"
    if section == 3 or any(
        marker in text
        for marker in (
            "高阶导数",
            "n阶导数",
            "高阶",
            "2026 阶",
            "higher derivative",
            "nth derivative",
            "leibniz",
        )
    ):
        return "higher_derivatives"
    if any(
        marker in text
        for marker in (
            "反函数",
            "反三角",
            "对数函数",
            "指数函数",
            "实数幂",
            "幂指函数",
            "inverse function",
            "inverse trig",
            "logarithm",
            "exponential",
            "real power",
        )
    ):
        return "inverse_exponential_logarithmic_derivatives"
    if any(
        marker in text
        for marker in (
            "链式法则",
            "复合函数",
            "复合",
            "对数求导",
            "chain rule",
            "composite",
            "logarithmic differentiation",
        )
    ):
        return "chain_rule_and_composites"
    if section == 2 or any(
        marker in text
        for marker in (
            "乘积法则",
            "商法则",
            "求导法则",
            "基本求导",
            "product rule",
            "quotient rule",
            "differentiation rule",
        )
    ):
        return "elementary_differentiation_rules"
    if any(
        marker in text
        for marker in (
            "瞬时速度",
            "平均速度",
            "运动模型",
            "几何意义",
            "切线",
            "法线",
            "rate",
            "velocity",
            "tangent",
            "normal",
        )
    ):
        return "derivative_interpretations"
    if any(
        marker in text
        for marker in (
            "左右导数",
            "可导与连续",
            "可导必连续",
            "连续不必可导",
            "分段函数",
            "尖点",
            "振荡函数",
            "导函数不连续",
            "one-sided",
            "differentiability",
            "continuity",
            "piecewise",
            "cusp",
            "oscillatory",
        )
    ):
        return "differentiability_and_one_sided_derivatives"
    return "derivative_definition"


def lineage_category(item: dict[str, Any]) -> str:
    if not item["classic_method"]:
        return "original_synthesis"
    if item["zh"]["title"] in OPEN_TEXT_ADAPTATION_TITLES:
        return "open_text_adaptation"
    return "classic_method_variant"


def references_for(item: dict[str, Any], method_family: str) -> list[str]:
    references = set(METHOD_FAMILY_REFERENCES[method_family])
    if method_family != "inverse_exponential_logarithmic_derivatives":
        return sorted(references)

    text = _searchable(item)
    selected = {"mit-18.01sc-differentiation"}
    if "三角" in text or "trig" in text:
        selected.add("openstax-calculus-v1-3.5")
    if "反函数" in text or "反三角" in text or "inverse" in text:
        selected.add("openstax-calculus-v1-3.7")
    if any(marker in text for marker in ("对数", "指数", "实数幂", "幂指", "log", "exp", "real power")):
        selected.add("openstax-calculus-v1-3.9")
    return sorted(selected & references)


def build_lineage(item: dict[str, Any]) -> dict[str, Any]:
    category = lineage_category(item)
    method_family = infer_method_family(item)
    return {
        "category": category,
        "method_family": method_family,
        "relation": CATEGORY_RELATIONS[category],
        "references": references_for(item, method_family),
    }


def annotate_item(item: dict[str, Any]) -> dict[str, Any]:
    localized_before = json.dumps(
        {"zh": item["zh"], "en": item["en"]},
        ensure_ascii=False,
        sort_keys=True,
    )
    annotated: dict[str, Any] = {}
    for key, value in item.items():
        if key == "source_lineage":
            continue
        annotated[key] = value
        if key == "classic_method":
            annotated["source_lineage"] = build_lineage(item)
    localized_after = json.dumps(
        {"zh": annotated["zh"], "en": annotated["en"]},
        ensure_ascii=False,
        sort_keys=True,
    )
    if localized_before != localized_after:
        raise RuntimeError(f"{item.get('id', '<unknown>')}: localized text changed")
    return annotated


def main() -> int:
    part_paths = sorted((ROOT / "content" / "parts").glob("part_*.json"))
    if not part_paths:
        print("No content parts found.", file=sys.stderr)
        return 1

    count = 0
    categories: dict[str, int] = {}
    for path in part_paths:
        items = json.loads(path.read_text(encoding="utf-8"))
        annotated = [annotate_item(item) for item in items]
        for item in annotated:
            category = item["source_lineage"]["category"]
            categories[category] = categories.get(category, 0) + 1
        path.write_text(
            json.dumps(annotated, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        count += len(annotated)

    print(f"Annotated {count} questions across {len(part_paths)} parts.")
    print(f"Category distribution: {dict(sorted(categories.items()))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
