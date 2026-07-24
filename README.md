# Tongji Calculus Chapter 2 - Bilingual Workbook

[简体中文说明](README.zh-CN.md)

A Goodnotes-ready bilingual practice set for Chapter 2, **Derivatives and Differentials**, aligned with the scope of the seventh edition of Tongji University’s *Advanced Mathematics*.

## Downloads

- [Chinese exercise workbook](dist/同济高数第七版_第二章_习题册_中文.pdf)
- [Chinese detailed solutions](dist/同济高数第七版_第二章_超详细解析_中文.pdf)
- [English exercise workbook](dist/Tongji_Calculus_7e_Chapter_2_Exercises_EN.pdf)
- [English detailed solutions](dist/Tongji_Calculus_7e_Chapter_2_Detailed_Solutions_EN.pdf)
- [SHA-256 checksums](SHA256SUMS)

The checksums verify the committed release PDFs. A local rebuild preserves the
validated content and layout, but PDF timestamps and trailer IDs can change the
byte-level hash.

## What is included

- Exactly 100 questions, from basic to challenge level.
- All five Chapter 2 sections: the derivative concept, differentiation rules, higher derivatives, implicit and parametric derivatives with related rates, and differentials.
- Eight formats: single choice, multiple choice, true/false with justification, fill-in, calculation, proof, synthesis/application, and error diagnosis.
- Detailed solutions with knowledge points, method selection, numbered derivations, pitfalls, verification, takeaway, and an extension prompt.
- Stable IDs Q001-Q100 across Chinese exercises, Chinese solutions, English exercises, and English solutions.
- Goodnotes-oriented 4:3 layouts: landscape for writing and portrait for detailed reading.

## Scope

The set deliberately uses only Chapter 2 tools. It does **not** use mean value theorems, L’Hopital’s rule, Taylor expansions, monotonicity or extremum tests, curvature, integration, or power series.

Items marked “Textbook-method adaptation” preserve a representative method while independently changing the function, parameters, rate process, or requested conclusion. No textbook exercise or example is reproduced verbatim.

## Study route

1. Complete Foundation, Methods, Synthesis, and Challenge in that order.
2. Attempt each question before opening the solution book.
3. Classify every error as conceptual, algebraic, rule-selection, domain/condition, unit, or rigor/communication.
4. Retry wrong items after 48 hours.
5. One week later, sample by knowledge tag across first principles, the chain rule, implicit differentiation, related rates, and differential approximation.

## Strengths and limitations

The set balances definitions, computation, proof, parameters, modeling, and diagnosis rather than repeating mechanical derivatives. Hard questions remain inside the Chapter 2 boundary.

One hundred questions cannot exhaust every composite-function pattern. Difficulty depends on algebra and trigonometric fluency, and a static PDF cannot adapt automatically to a learner’s error history. Differential approximations show first-order linearization without Taylor-style remainder bounds.

## Build locally

The verified build environment uses Python 3.12 or newer and currently targets macOS because
it uses bundled system fonts for CJK text and mathematical modifier glyphs.
Install the Python packages in `requirements.txt`. Full image QA also requires
Poppler's `pdftoppm`; PDF generation and structural validation do not.

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python scripts/merge_corpus.py
python scripts/validate_content.py
python scripts/build_pdfs.py
python scripts/validate_pdfs.py
python scripts/render_validate.py  # optional full rendered-page QA
pytest -q
```

The editable authoring sources are the files in [`content/parts`](content/parts).
`scripts/merge_corpus.py` combines them into the canonical generated corpus
[`content/questions.json`](content/questions.json), from which all four PDFs are built.

## Attribution and status

This is independently authored study material. It is **not** an official publication of Tongji University or Higher Education Press and is not affiliated with either organization. See [SOURCES.md](SOURCES.md) for scope references.

Original project content is shared under the terms described in [LICENSE](LICENSE).
The CC BY-NC-SA 4.0 license permits noncommercial sharing and adaptation; its
NonCommercial restriction means this repository is publicly source-available,
not OSI-approved open-source software.
