from __future__ import annotations

from collections import Counter
from pathlib import Path
import re
from typing import Callable, Iterable
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import landscape
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.platypus import (
    BaseDocTemplate,
    Flowable,
    Frame,
    KeepTogether,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

from src.styles import (
    BLUE,
    CORAL,
    DIFFICULTY_LABELS,
    GOLD,
    GRID,
    INK,
    MUTED,
    NAVY,
    PALE_BLUE,
    PALE_CORAL,
    PALE_GOLD,
    PALE_PURPLE,
    PALE_TEAL,
    PAPER,
    PURPLE,
    SECTION_INFO,
    TEAL,
    TIER_LABELS,
    TYPE_LABELS,
    build_styles,
    register_fonts,
)


EXERCISE_SIZE = (264 * mm, 198 * mm)
SOLUTION_SIZE = (198 * mm, 264 * mm)

# These glyphs are absent from the primary CJK-capable body font.  ReportLab
# does not perform automatic font fallback, so _safe() wraps them explicitly.
_MODIFIER_GLYPHS = "ʰʲˢˣᵃᵇᵏᵐᵘᵛⁱⁿ"
_SUBSCRIPT_GLYPHS = "ₘₙ"


def _braced_argument(text: str, start: int) -> tuple[str, int] | None:
    if start >= len(text) or text[start] != "{":
        return None
    depth = 0
    for index in range(start, len(text)):
        if text[index] == "{":
            depth += 1
        elif text[index] == "}":
            depth -= 1
            if depth == 0:
                return text[start + 1 : index], index + 1
    return None


def _replace_one_argument(
    text: str,
    command: str,
    formatter: Callable[[str], str],
) -> str:
    cursor = 0
    while True:
        index = text.find(command, cursor)
        if index < 0:
            return text
        argument = _braced_argument(text, index + len(command))
        if argument is None:
            cursor = index + len(command)
            continue
        inner, end = argument
        replacement = formatter(_normalize_math_markup(inner))
        text = text[:index] + replacement + text[end:]
        cursor = index + len(replacement)


def _replace_fraction(text: str) -> str:
    cursor = 0
    command = r"\frac"
    while True:
        index = text.find(command, cursor)
        if index < 0:
            return text
        numerator = _braced_argument(text, index + len(command))
        if numerator is None:
            cursor = index + len(command)
            continue
        numerator_text, after_numerator = numerator
        denominator = _braced_argument(text, after_numerator)
        if denominator is None:
            cursor = after_numerator
            continue
        denominator_text, end = denominator
        replacement = (
            f"({_normalize_math_markup(numerator_text)})/"
            f"({_normalize_math_markup(denominator_text)})"
        )
        text = text[:index] + replacement + text[end:]
        cursor = index + len(replacement)


def _normalize_math_markup(value: str) -> str:
    text = value.replace("$", "")
    text = _replace_fraction(text)
    text = _replace_one_argument(text, r"\sqrt", lambda inner: f"√({inner})")
    text = _replace_one_argument(text, r"\mathbb", lambda inner: {"R": "ℝ", "Q": "ℚ", "N": "ℕ", "Z": "ℤ"}.get(inner, inner))
    text = _replace_one_argument(text, r"\widetilde", lambda inner: f"{inner}̃")
    text = _replace_one_argument(text, r"\underline", lambda inner: "________" if not inner or "qquad" in inner else inner)
    text = _replace_one_argument(text, r"\mathrm", lambda inner: inner)
    text = _replace_one_argument(text, r"\operatorname", lambda inner: inner)
    text = _replace_one_argument(text, r"\text", lambda inner: inner)
    blackboard = {"R": "ℝ", "Q": "ℚ", "N": "ℕ", "Z": "ℤ"}
    text = re.sub(
        r"\\mathbb\s*([RQNZ])",
        lambda match: blackboard[match.group(1)],
        text,
    )
    text = re.sub(r"\\widetilde\s*([A-Za-z])", lambda match: f"{match.group(1)}̃", text)
    replacements = {
        r"\Rightarrow": "⇒",
        r"\varepsilon": "ε",
        r"\epsilon": "ε",
        r"\infty": "∞",
        r"\delta": "δ",
        r"\alpha": "α",
        r"\xi": "ξ",
        r"\mu": "μ",
        r"\pi": "π",
        r"\sqrt": "√",
        r"\sin": "sin",
        r"\cos": "cos",
        r"\tan": "tan",
        r"\cot": "cot",
        r"\sec": "sec",
        r"\csc": "csc",
        r"\arcsin": "arcsin",
        r"\arccos": "arccos",
        r"\arctan": "arctan",
        r"\exp": "exp",
        r"\log": "log",
        r"\ln": "ln",
        r"\lim": "lim",
        r"\min": "min",
        r"\prime": "′",
        r"\left": "",
        r"\right": "",
        r"\to": "→",
        r"\le": "≤",
        r"\ge": "≥",
        r"\ne": "≠",
        r"\in": "∈",
        r"\cap": "∩",
        r"\pm": "±",
        r"\cdot": "·",
        r"\equiv": "≡",
        r"\qquad": "    ",
        r"\displaystyle": "",
    }
    for source, target in replacements.items():
        text = text.replace(source, target)
    text = re.sub(r"_\{([^{}]+)\}", r"_(\1)", text)
    text = re.sub(r"\^\{([^{}]+)\}", r"^(\1)", text)
    text = text.replace(r"\{", "{").replace(r"\}", "}")
    text = text.replace(r"\ ", " ")
    text = re.sub(r"\\([A-Za-z]+)", r"\1", text)
    return text


def _safe(value: object) -> str:
    text = escape(_normalize_math_markup(str(value))).replace("\n", "<br/>")
    text = re.sub(
        f"([{re.escape(_MODIFIER_GLYPHS)}]+)",
        r'<font name="WorkbookModifier">\1</font>',
        text,
    )
    return re.sub(
        f"([{re.escape(_SUBSCRIPT_GLYPHS)}]+)",
        r'<font name="WorkbookSubscript">\1</font>',
        text,
    )


def _lang(item: dict, language: str) -> dict:
    return item[language]


def _section_name(number: int, language: str) -> str:
    return SECTION_INFO[number][0 if language == "zh" else 1]


def _difficulty(item: dict, language: str) -> tuple[str, colors.Color]:
    zh, en, color = DIFFICULTY_LABELS[item["difficulty"]]
    return (zh if language == "zh" else en, color)


def _type_name(item: dict, language: str) -> str:
    zh, en = TYPE_LABELS[item["type"]]
    return zh if language == "zh" else en


def _tier_name(tier: str, language: str) -> str:
    zh, en = TIER_LABELS[tier]
    return zh if language == "zh" else en


class DottedWorkspace(Flowable):
    def __init__(self, width: float, height: float, language: str):
        super().__init__()
        self.width = width
        self.height = height
        self.language = language

    def wrap(self, avail_width: float, avail_height: float) -> tuple[float, float]:
        return min(self.width, avail_width), min(self.height, avail_height)

    def draw(self) -> None:
        canvas = self.canv
        canvas.saveState()
        canvas.setStrokeColor(colors.HexColor("#E3E7EE"))
        canvas.setLineWidth(0.7)
        canvas.roundRect(0, 0, self.width, self.height, 5 * mm, stroke=1, fill=0)
        canvas.setFillColor(GRID)
        step = 8 * mm
        radius = 0.38
        x = step
        while x < self.width - step / 2:
            y = step
            while y < self.height - step / 2:
                canvas.circle(x, y, radius, stroke=0, fill=1)
                y += step
            x += step
        canvas.setFont("Workbook", 7.5)
        canvas.setFillColor(colors.HexColor("#A4ACB9"))
        label = "答题区 · 可继续加页" if self.language == "zh" else "WORKSPACE · add pages as needed"
        canvas.drawRightString(self.width - 4 * mm, self.height - 5 * mm, label)
        canvas.restoreState()


class CoverPanel(Flowable):
    def __init__(self, width: float, height: float, language: str, kind: str):
        super().__init__()
        self.width = width
        self.height = height
        self.language = language
        self.kind = kind

    def wrap(self, avail_width: float, avail_height: float) -> tuple[float, float]:
        return min(self.width, avail_width), min(self.height, avail_height)

    def draw(self) -> None:
        c = self.canv
        w, h = self.width, self.height
        c.saveState()
        c.setFillColor(NAVY)
        c.roundRect(0, 0, w, h, 8 * mm, stroke=0, fill=1)
        c.setFillColor(BLUE)
        c.circle(w * 0.86, h * 0.78, 29 * mm, stroke=0, fill=1)
        c.setFillColor(TEAL)
        c.circle(w * 0.82, h * 0.72, 15 * mm, stroke=0, fill=1)
        c.setStrokeColor(colors.Color(1, 1, 1, alpha=0.14))
        c.setLineWidth(1.2)
        for offset in range(0, 9):
            y = 18 * mm + offset * 12 * mm
            c.line(w * 0.55, y, w - 12 * mm, y + 18 * mm)

        c.setFillColor(colors.white)
        c.setFont("Workbook", 10)
        kicker = (
            "同济大学《高等数学》第七版 · 第二章"
            if self.language == "zh"
            else "TONGJI CALCULUS, 7TH EDITION · CHAPTER 2"
        )
        c.drawString(14 * mm, h - 20 * mm, kicker)

        c.setFont("WorkbookBold", 25 if self.language == "zh" else 22)
        if self.language == "zh":
            lines = ["导数与微分", "分层训练习题册"] if self.kind == "exercises" else ["导数与微分", "超详细解析"]
        else:
            lines = ["DERIVATIVES & DIFFERENTIALS", "EXERCISE WORKBOOK"] if self.kind == "exercises" else [
                "DERIVATIVES & DIFFERENTIALS",
                "DETAILED SOLUTIONS",
            ]
        y = h - 53 * mm
        for line in lines:
            c.drawString(14 * mm, y, line)
            y -= 13 * mm

        c.setFont("Workbook", 11)
        subtitle = (
            "100 道原创与教材经典方法变式 · 从基础到挑战"
            if self.language == "zh"
            else "100 original and textbook-method adaptations · basic to challenge"
        )
        c.drawString(14 * mm, y - 5 * mm, subtitle)
        c.setFillColor(colors.HexColor("#D7E3FF"))
        c.setFont("Workbook", 9)
        note = (
            "Goodnotes 4:3 优化版 · 2026"
            if self.language == "zh"
            else "Goodnotes-optimized 4:3 edition · 2026"
        )
        c.drawString(14 * mm, 16 * mm, note)
        c.restoreState()


class WorkbookDocTemplate(BaseDocTemplate):
    def __init__(
        self,
        filename: str,
        *,
        page_size: tuple[float, float],
        language: str,
        kind: str,
        title: str,
    ):
        self.language = language
        self.kind = kind
        self.running_title = title
        margin_x = 14 * mm
        margin_top = 17 * mm
        margin_bottom = 13 * mm
        super().__init__(
            filename,
            pagesize=page_size,
            leftMargin=margin_x,
            rightMargin=margin_x,
            topMargin=margin_top,
            bottomMargin=margin_bottom,
            title=title,
            author="Independent Study Workbook Project",
            subject="Tongji Calculus Chapter 2 bilingual exercises and solutions",
        )
        frame = Frame(
            self.leftMargin,
            self.bottomMargin,
            self.width,
            self.height,
            id="main",
            leftPadding=0,
            rightPadding=0,
            topPadding=0,
            bottomPadding=0,
        )
        self.addPageTemplates(PageTemplate(id="default", frames=[frame], onPage=self._decorate_page))

    def _decorate_page(self, canvas, doc) -> None:
        canvas.saveState()
        canvas.setFillColor(PAPER)
        canvas.rect(0, 0, doc.pagesize[0], doc.pagesize[1], stroke=0, fill=1)
        if doc.page > 1:
            canvas.setStrokeColor(colors.HexColor("#E4E8EF"))
            canvas.setLineWidth(0.7)
            canvas.line(doc.leftMargin, doc.pagesize[1] - 11 * mm, doc.pagesize[0] - doc.rightMargin, doc.pagesize[1] - 11 * mm)
            canvas.setFillColor(MUTED)
            canvas.setFont("Workbook", 7.8)
            canvas.drawString(doc.leftMargin, doc.pagesize[1] - 8.3 * mm, self.running_title)
            canvas.drawRightString(doc.pagesize[0] - doc.rightMargin, 7.2 * mm, f"{doc.page}")
        canvas.restoreState()

    def afterFlowable(self, flowable: Flowable) -> None:
        bookmark = getattr(flowable, "_bookmark_name", None)
        outline = getattr(flowable, "_outline_text", None)
        level = getattr(flowable, "_outline_level", 0)
        if bookmark and outline:
            self.canv.bookmarkPage(bookmark)
            self.canv.addOutlineEntry(outline, bookmark, level=level, closed=False)


def _bookmark_paragraph(text: str, style, name: str, outline: str, level: int = 0) -> Paragraph:
    paragraph = Paragraph(text, style)
    paragraph._bookmark_name = name
    paragraph._outline_text = outline
    paragraph._outline_level = level
    return paragraph


def _cover_story(styles: dict, width: float, language: str, kind: str) -> list[Flowable]:
    height = 146 * mm if kind == "exercises" else 194 * mm
    if language == "zh":
        disclaimer = "独立编写学习资料。非同济大学或高等教育出版社官方出版物。"
    else:
        disclaimer = "Independently authored study material. Not an official publication of Tongji University or Higher Education Press."
    return [
        Spacer(1, 7 * mm),
        CoverPanel(width, height, language, kind),
        Spacer(1, 7 * mm),
        Paragraph(_safe(disclaimer), styles["small"]),
        PageBreak(),
    ]


def _summary_table(items: list[dict], language: str, styles: dict, width: float) -> Table:
    if language == "zh":
        labels = ["题目", "章节", "难度层级", "题型"]
        values = [
            "100 道",
            "5 节全覆盖",
            "基础 → 挑战",
            "8 类混合",
        ]
    else:
        labels = ["Questions", "Sections", "Progression", "Formats"]
        values = ["100", "All 5 sections", "Basic → challenge", "8 mixed formats"]
    data = []
    for label, value in zip(labels, values):
        data.append(
            [
                Paragraph(f"<b>{_safe(value)}</b><br/><font color='#667085'>{_safe(label)}</font>", styles["center"])
            ]
        )
    table = Table([data], colWidths=[width / 4] * 4)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), PALE_BLUE),
                ("BOX", (0, 0), (-1, -1), 0.8, colors.HexColor("#D6E2FA")),
                ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#D6E2FA")),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("TOPPADDING", (0, 0), (-1, -1), 9),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 9),
            ]
        )
    )
    return table


def _coverage_table(items: list[dict], language: str, styles: dict, width: float) -> Table:
    counts = Counter(item["section"] for item in items)
    if language == "zh":
        data = [["节次", "主题", "题数", "关键覆盖"]]
        keywords = {
            1: "定义、单侧导数、几何与物理意义、连续性",
            2: "四则、复合、反函数、基本公式、参数",
            3: "二阶与 n 阶、循环规律、归纳与乘积",
            4: "隐函数、参数方程、相关变化率与单位",
            5: "微分定义、运算法则、线性近似与误差估计",
        }
    else:
        data = [["Sec.", "Topic", "Items", "Key coverage"]]
        keywords = {
            1: "definition, one-sided derivatives, geometry, rates, continuity",
            2: "algebraic, chain, inverse, basic formulas, parameters",
            3: "second and nth derivatives, cycles, induction, products",
            4: "implicit, parametric, related rates, units",
            5: "definition, rules, linear approximation, error estimates",
        }
    for section in range(1, 6):
        data.append([str(section), _section_name(section, language), str(counts[section]), keywords[section]])
    rendered = [[Paragraph(f"<b>{_safe(cell)}</b>" if row_index == 0 else _safe(cell), styles["table"]) for cell in row] for row_index, row in enumerate(data)]
    table = Table(rendered, colWidths=[width * 0.08, width * 0.28, width * 0.09, width * 0.55], repeatRows=1)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), NAVY),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F7F9FC")]),
                ("BOX", (0, 0), (-1, -1), 0.6, colors.HexColor("#D9DEE8")),
                ("INNERGRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#E2E6ED")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )
    return table


def _front_matter(items: list[dict], language: str, styles: dict, width: float, kind: str) -> list[Flowable]:
    if language == "zh":
        heading = "使用说明"
        body = (
            "建议先按“基础篇 → 方法篇 → 综合篇 → 挑战篇”完成。每题右上角给出难度、题型与建议用时。"
            "第一次作答不要查解析；订正时在解析册中记录“错因”，隔 48 小时再做一次。"
        )
        classic = "“教材经典方法变式”表示保留教材代表性方法，但题目结构、参数或问法已经重新设计。"
        scope = (
            "范围说明：只使用第二章知识；不调用中值定理、洛必达法则、泰勒公式、"
            "单调性与极值判别、曲率、积分或幂级数。"
        )
        coverage_heading = "知识覆盖矩阵"
    else:
        heading = "How to use this set"
        body = (
            "Work through Foundation, Methods, Synthesis, and Challenge in that order. "
            "Each question shows its difficulty, format, and suggested time. Attempt it before opening the solution book; "
            "record the cause of each error and retry after 48 hours."
        )
        classic = (
            "“Textbook-method adaptation” means the representative method is retained while the structure, parameters, "
            "or task have been independently redesigned."
        )
        scope = (
            "Scope: Chapter 2 tools only. Mean value theorems, L'Hopital's rule, Taylor expansions, "
            "monotonicity or extremum tests, curvature, integration, and power series are not used."
        )
        coverage_heading = "Coverage matrix"
    return [
        _bookmark_paragraph(_safe(heading), styles["h1"], "front-matter", heading, 0),
        _summary_table(items, language, styles, width),
        Spacer(1, 8 * mm),
        Paragraph(_safe(body), styles["body"]),
        Paragraph(_safe(classic), styles["body"]),
        Paragraph(_safe(scope), styles["body"]),
        Spacer(1, 5 * mm),
        Paragraph(_safe(coverage_heading), styles["h2"]),
        _coverage_table(items, language, styles, width),
        PageBreak(),
    ]


def _meta_table(item: dict, language: str, styles: dict, width: float) -> Table:
    diff_label, diff_color = _difficulty(item, language)
    type_label = _type_name(item, language)
    section_label = f"§{item['section']} · {_section_name(item['section'], language)}"
    time_label = f"{item['minutes']} 分钟" if language == "zh" else f"{item['minutes']} min"
    classic = (
        "教材经典方法变式"
        if language == "zh"
        else "Textbook-method adaptation"
    )
    cells = [
        (section_label, PALE_BLUE, NAVY),
        (diff_label, colors.Color(diff_color.red, diff_color.green, diff_color.blue, alpha=0.12), diff_color),
        (type_label, PALE_PURPLE, PURPLE),
        (time_label, PALE_GOLD, GOLD),
    ]
    if item["classic_method"]:
        cells.append((classic, PALE_TEAL, TEAL))
    rendered = [
        Paragraph(f"<font color='{text.hexval()}'><b>{_safe(label)}</b></font>", styles["meta"])
        for label, _, text in cells
    ]
    table = Table([rendered], colWidths=[width / len(cells)] * len(cells))
    commands = [
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#D8DEE9")),
        ("INNERGRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#D8DEE9")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]
    for index, (_, background, _) in enumerate(cells):
        commands.append(("BACKGROUND", (index, 0), (index, 0), background))
    table.setStyle(TableStyle(commands))
    return table


def _exercise_item(item: dict, language: str, styles: dict, width: float) -> list[Flowable]:
    localized = _lang(item, language)
    title = f"{item['id']} · {localized['title']}"
    question = _bookmark_paragraph(
        _safe(title),
        styles["question"],
        item["id"],
        title,
        1,
    )
    content: list[Flowable] = [
        _meta_table(item, language, styles, width),
        Spacer(1, 5 * mm),
        question,
        Paragraph(_safe(localized["prompt"]), styles["prompt"]),
    ]
    for index, choice in enumerate(localized.get("choices", [])):
        label = chr(ord("A") + index)
        content.append(Paragraph(f"<b>{label}.</b> {_safe(choice)}", styles["choice"]))
    content.append(Spacer(1, 3 * mm))
    heights = {"S": 68 * mm, "M": 86 * mm, "L": 101 * mm, "XL": 111 * mm}
    content.append(DottedWorkspace(width, heights[item["space"]], language))
    return [KeepTogether(content)]


def _box(
    title: str,
    body: str | Iterable[str],
    *,
    styles: dict,
    width: float,
    background: colors.Color,
    accent: colors.Color,
) -> Table:
    if isinstance(body, str):
        lines = [body]
    else:
        lines = list(body)
    paragraphs: list[Flowable] = [
        Paragraph(f"<font color='{accent.hexval()}'><b>{_safe(title)}</b></font>", styles["box_title"])
    ]
    for line in lines:
        paragraphs.append(Paragraph(_safe(line), styles["box_body"]))
    table = Table([[paragraphs]], colWidths=[width])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), background),
                ("BOX", (0, 0), (-1, -1), 0.7, accent),
                ("LEFTPADDING", (0, 0), (-1, -1), 10),
                ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
            ]
        )
    )
    return table


def _solution_item(item: dict, language: str, styles: dict, width: float) -> list[Flowable]:
    localized = _lang(item, language)
    solution = localized["solution"]
    title = f"{item['id']} · {localized['title']}"
    if language == "zh":
        labels = {
            "question": "题目回顾",
            "answer": "结论先行",
            "knowledge": "本题知识点",
            "analysis": "审题与方法选择",
            "steps": "逐步推导",
            "pitfalls": "易错点",
            "verification": "检验与核对",
            "takeaway": "方法总结",
            "extension": "变式提示",
        }
    else:
        labels = {
            "question": "Question",
            "answer": "Answer first",
            "knowledge": "Knowledge points",
            "analysis": "Reading the problem and choosing a method",
            "steps": "Step-by-step derivation",
            "pitfalls": "Common pitfalls",
            "verification": "Verification",
            "takeaway": "Method summary",
            "extension": "Extension prompt",
        }
    story: list[Flowable] = [
        _meta_table(item, language, styles, width),
        Spacer(1, 5 * mm),
        _bookmark_paragraph(_safe(title), styles["question"], f"S-{item['id']}", title, 1),
        _box(
            labels["question"],
            localized["prompt"],
            styles=styles,
            width=width,
            background=PALE_BLUE,
            accent=BLUE,
        ),
        Spacer(1, 4 * mm),
        _box(
            labels["answer"],
            localized["answer"],
            styles=styles,
            width=width,
            background=PALE_GOLD,
            accent=GOLD,
        ),
        Spacer(1, 4 * mm),
        _box(
            labels["knowledge"],
            [f"• {item_text}" for item_text in solution["knowledge"]],
            styles=styles,
            width=width,
            background=PALE_TEAL,
            accent=TEAL,
        ),
        Spacer(1, 4 * mm),
        _box(
            labels["analysis"],
            solution["analysis"],
            styles=styles,
            width=width,
            background=colors.HexColor("#F7F9FC"),
            accent=NAVY,
        ),
        Spacer(1, 5 * mm),
        Paragraph(_safe(labels["steps"]), styles["h2"]),
    ]
    for index, step in enumerate(solution["steps"], start=1):
        step_label = f"第 {index} 步" if language == "zh" else f"Step {index}"
        story.append(Paragraph(f"<b>{_safe(step_label)}.</b> {_safe(step)}", styles["step"]))
    story.extend(
        [
            Spacer(1, 2 * mm),
            _box(
                labels["pitfalls"],
                [f"• {item_text}" for item_text in solution["pitfalls"]],
                styles=styles,
                width=width,
                background=PALE_CORAL,
                accent=CORAL,
            ),
            Spacer(1, 4 * mm),
            _box(
                labels["verification"],
                solution["verification"],
                styles=styles,
                width=width,
                background=PALE_BLUE,
                accent=BLUE,
            ),
            Spacer(1, 4 * mm),
            _box(
                labels["takeaway"],
                solution["takeaway"],
                styles=styles,
                width=width,
                background=PALE_PURPLE,
                accent=PURPLE,
            ),
        ]
    )
    if solution.get("extension"):
        story.extend(
            [
                Spacer(1, 4 * mm),
                _box(
                    labels["extension"],
                    solution["extension"],
                    styles=styles,
                    width=width,
                    background=PALE_GOLD,
                    accent=GOLD,
                ),
            ]
        )
    return story


def _assessment(
    items: list[dict],
    language: str,
    styles: dict,
    width: float,
    kind: str,
) -> list[Flowable]:
    if language == "zh":
        heading = "训练价值、局限与二刷路线"
        strengths_title = "这套题的优点"
        strengths = [
            "五节完整覆盖，并用知识点标签建立可回查索引。",
            "定义、计算、证明、参数、应用和错解诊断并重，能暴露“会套公式但不懂可导条件”的问题。",
            "难题仍严格使用第二章工具，重点训练定义求导、复合规则选择、参数分类与变化率建模。",
            "中英文题号与数学内容一一对应，可同时积累微积分英语表达。",
        ]
        limits_title = "需要知道的局限"
        limits = [
            "100 题无法穷尽所有复合函数与代数结构；薄弱类型仍需追加同类专项训练。",
            "教材内容均为经典方法变式，不是教材原题的逐字复刻。",
            "难度标记具有一定主观性；三角恒等变形和代数基础不同，实际耗时会明显不同。",
            "微分近似只体现一阶线性化，不给出第三章泰勒公式中的余项界。",
            "为守住第二章边界，本套题不使用中值定理、洛必达、泰勒、单调性或极值判别。",
        ]
        route_title = "建议二刷路线"
        route = [
            "第一遍：按难度顺序限时完成，只标记信心等级，不查答案。",
            "订正：在解析册中写下错因，区分概念、代数、方法选择和书写不严谨。",
            "48 小时后：只重做错题及其前后相邻题，要求不用提示独立复现。",
            "一周后：按知识点交叉抽题，重点回练定义求导、链式法则、隐函数条件、相关变化率单位和微分近似。",
        ]
    else:
        heading = "Training value, limitations, and second-pass route"
        strengths_title = "Strengths"
        strengths = [
            "All five sections are covered and indexed by knowledge point.",
            "Definition, computation, proof, parameter, application, and error-diagnosis tasks expose more than formula substitution.",
            "Even the hard questions stay within Chapter 2 tools and emphasize first principles, rule selection, parameter classification, and rate models.",
            "Chinese and English identifiers and mathematics match one-to-one, supporting calculus vocabulary development.",
        ]
        limits_title = "Limitations"
        limits = [
            "One hundred questions cannot exhaust every composite-function pattern; weak categories may need extra drills.",
            "Textbook material is represented by independently rewritten method adaptations, not verbatim textbook questions.",
            "Difficulty is partly subjective and depends on algebra and trigonometric fluency.",
            "Differential approximations show first-order linearization without Taylor-style remainder bounds.",
            "To respect the Chapter 2 boundary, mean value theorems, L'Hopital, Taylor, and monotonicity or extremum tests are not used.",
        ]
        route_title = "Recommended second pass"
        route = [
            "First pass: work under time limits, record confidence, and do not open the solutions.",
            "Correction: classify each error as conceptual, algebraic, method-selection, or rigor/communication.",
            "After 48 hours: redo wrong items and their neighbors without prompts.",
            "After one week: sample by knowledge tag, emphasizing first principles, the chain rule, implicit conditions, rate units, and differential approximation.",
        ]
    gap = 3 * mm if kind == "exercises" else 6 * mm
    return [
        PageBreak(),
        _bookmark_paragraph(_safe(heading), styles["h1"], "assessment", heading, 0),
        _box(strengths_title, [f"• {text}" for text in strengths], styles=styles, width=width, background=PALE_TEAL, accent=TEAL),
        Spacer(1, gap),
        _box(limits_title, [f"• {text}" for text in limits], styles=styles, width=width, background=PALE_CORAL, accent=CORAL),
        Spacer(1, gap),
        _box(route_title, [f"{index}. {text}" for index, text in enumerate(route, start=1)], styles=styles, width=width, background=PALE_BLUE, accent=BLUE),
    ]


def _build(
    items: list[dict],
    language: str,
    output_path: Path,
    kind: str,
) -> None:
    register_fonts()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if kind == "exercises":
        page_size = EXERCISE_SIZE
        title = "同济高数第二章·习题册" if language == "zh" else "Tongji Calculus Chapter 2 · Exercises"
    else:
        page_size = SOLUTION_SIZE
        title = "同济高数第二章·超详细解析" if language == "zh" else "Tongji Calculus Chapter 2 · Detailed Solutions"
    styles = build_styles(language)
    doc = WorkbookDocTemplate(
        str(output_path),
        page_size=page_size,
        language=language,
        kind=kind,
        title=title,
    )
    story: list[Flowable] = []
    story.extend(_cover_story(styles, doc.width, language, kind))
    story.extend(_front_matter(items, language, styles, doc.width, kind))

    last_tier: str | None = None
    first_item = True
    for item in items:
        if not first_item:
            story.append(PageBreak())
        if item["tier"] != last_tier:
            tier_heading = _tier_name(item["tier"], language)
            story.append(
                _bookmark_paragraph(
                    _safe(tier_heading),
                    styles["h1"],
                    f"tier-{item['tier']}",
                    tier_heading,
                    0,
                )
            )
            tier_note = (
                "请先独立完成，再对照解析。"
                if language == "zh"
                else "Attempt independently before consulting the solutions."
            )
            story.append(Paragraph(_safe(tier_note), styles["body"]))
            story.append(PageBreak())
            last_tier = item["tier"]

        if kind == "exercises":
            story.extend(_exercise_item(item, language, styles, doc.width))
        else:
            story.extend(_solution_item(item, language, styles, doc.width))
        first_item = False
    story.extend(_assessment(items, language, styles, doc.width, kind))
    doc.build(story)


def build_exercises(items: list[dict], language: str, output_path: Path) -> None:
    _build(items, language, output_path, "exercises")


def build_solutions(items: list[dict], language: str, output_path: Path) -> None:
    _build(items, language, output_path, "solutions")
