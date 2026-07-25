# Sources, method lineage, and attribution boundaries

## What `source_lineage` means

Every question has a machine-validated `source_lineage` object with:

- `category`: the editorial relationship to the method tradition;
- `method_family`: the calculus topic or technique being trained;
- `relation`: a fixed, auditable description of that relationship;
- `references`: identifiers for open educational pages that document the topic or method.

These references verify **topic and method lineage only**. They do not claim
that a question, sentence, numerical parameter, diagram, or worked solution was
copied from a referenced page.

The three categories have deliberately narrow meanings:

| Category | Required relation | Meaning |
|---|---|---|
| `open_text_adaptation` | `adapted_from_open_text_topic_and_method` | An independently written exercise uses a conventional method or applied archetype documented by an open educational source. |
| `classic_method_variant` | `independently_rewritten_classic_method_variant` | An independently written variant trains a standard calculus method; the reference verifies the method, not a particular source problem. |
| `original_synthesis` | `independently_synthesized_from_standard_methods` | The question combines, diagnoses, classifies, or extends standard methods in an independently designed structure. |

No item metadata attributes wording to the Tongji textbook, Stewart,
Thomas, or another commercial calculus textbook. The `classic_method` flag is
an editorial training label, not a claim of textual provenance.

## Open educational reference registry

Question metadata stores the stable identifier in the first column. The
validator rejects unknown identifiers and references that are not registered
for the selected method family.

| Identifier | Open educational page |
|---|---|
| `openstax-calculus-v1-3.1` | [OpenStax Calculus Volume 1, 3.1 Defining the Derivative](https://openstax.org/books/calculus-volume-1/pages/3-1-defining-the-derivative) |
| `openstax-calculus-v1-3.2` | [OpenStax Calculus Volume 1, 3.2 The Derivative as a Function](https://openstax.org/books/calculus-volume-1/pages/3-2-the-derivative-as-a-function) |
| `openstax-calculus-v1-3.3` | [OpenStax Calculus Volume 1, 3.3 Differentiation Rules](https://openstax.org/books/calculus-volume-1/pages/3-3-differentiation-rules) |
| `openstax-calculus-v1-3.4` | [OpenStax Calculus Volume 1, 3.4 Derivatives as Rates of Change](https://openstax.org/books/calculus-volume-1/pages/3-4-derivatives-as-rates-of-change) |
| `openstax-calculus-v1-3.5` | [OpenStax Calculus Volume 1, 3.5 Derivatives of Trigonometric Functions](https://openstax.org/books/calculus-volume-1/pages/3-5-derivatives-of-trigonometric-functions) |
| `openstax-calculus-v1-3.6` | [OpenStax Calculus Volume 1, 3.6 The Chain Rule](https://openstax.org/books/calculus-volume-1/pages/3-6-the-chain-rule) |
| `openstax-calculus-v1-3.7` | [OpenStax Calculus Volume 1, 3.7 Derivatives of Inverse Functions](https://openstax.org/books/calculus-volume-1/pages/3-7-derivatives-of-inverse-functions) |
| `openstax-calculus-v1-3.8` | [OpenStax Calculus Volume 1, 3.8 Implicit Differentiation](https://openstax.org/books/calculus-volume-1/pages/3-8-implicit-differentiation) |
| `openstax-calculus-v1-3.9` | [OpenStax Calculus Volume 1, 3.9 Derivatives of Exponential and Logarithmic Functions](https://openstax.org/books/calculus-volume-1/pages/3-9-derivatives-of-exponential-and-logarithmic-functions) |
| `openstax-calculus-v1-4.1` | [OpenStax Calculus Volume 1, 4.1 Related Rates](https://openstax.org/books/calculus-volume-1/pages/4-1-related-rates) |
| `openstax-calculus-v1-4.2` | [OpenStax Calculus Volume 1, 4.2 Linear Approximations and Differentials](https://openstax.org/books/calculus-volume-1/pages/4-2-linear-approximations-and-differentials) |
| `openstax-calculus-v2-7.2` | [OpenStax Calculus Volume 2, 7.2 Calculus of Parametric Curves](https://openstax.org/books/calculus-volume-2/pages/7-2-calculus-of-parametric-curves) |
| `mit-18.01sc-differentiation` | [MIT OpenCourseWare 18.01SC, Unit 1: Differentiation](https://ocw.mit.edu/courses/18-01sc-single-variable-calculus-fall-2010/pages/1.-differentiation/) |
| `mit-18.01sc-session-3-rate` | [MIT OpenCourseWare 18.01SC, Session 3: Derivative as Rate of Change](https://ocw.mit.edu/courses/18-01sc-single-variable-calculus-fall-2010/pages/1.-differentiation/part-a-definition-and-basic-rules/session-3-derivative-as-rate-of-change/) |
| `mit-18.01sc-applications` | [MIT OpenCourseWare 18.01SC, Unit 2: Applications of Differentiation](https://ocw.mit.edu/courses/18-01sc-single-variable-calculus-fall-2010/pages/unit-2-applications-of-differentiation/) |

OpenStax and MIT OpenCourseWare publish their own license and attribution
terms on their sites. This repository links to those pages and does not
incorporate their problem statements or worked solutions.

## Tongji scope references

The following public pages are used only to verify edition metadata,
Chapter 2 structure, and course scope:

- Higher Education Press, *Advanced Mathematics (7th edition), Volume I*
  product page and complete contents:
  <https://xuanshu.hep.com.cn/front/h5Mobile/bookDetails?bookId=59cfa123ba9eb884cf8241de>
- Higher Education Press, seventh-edition Volume I product information:
  <https://www.hep.com.cn/book/show/f9a5ba29-e58e-4a42-9c1b-830a0e28f1f3>
- Tongji University Mathematics School, Advanced Mathematics synchronous
  course preview:
  <https://gaoshutongbu.tongji.edu.cn/kcyx.htm>
- Tongji University Mathematics School, exercise-solution index containing
  the Chapter 2 topics:
  <https://gaoshutongbu.tongji.edu.cn/xtxj/1.htm>

No problem statement or worked example from the Tongji textbook is reproduced
verbatim. “Tongji University,” “Higher Education Press,” and the textbook
title are used descriptively to identify the study scope. This repository is
unofficial and unaffiliated.
