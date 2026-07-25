from __future__ import annotations


SOURCE_LINEAGE_CATEGORIES = frozenset(
    {
        "open_text_adaptation",
        "classic_method_variant",
        "original_synthesis",
    }
)

CATEGORY_RELATIONS = {
    "open_text_adaptation": "adapted_from_open_text_topic_and_method",
    "classic_method_variant": "independently_rewritten_classic_method_variant",
    "original_synthesis": "independently_synthesized_from_standard_methods",
}

SOURCE_REFERENCES = {
    "openstax-calculus-v1-3.1": {
        "title": "OpenStax Calculus Volume 1, 3.1 Defining the Derivative",
        "url": "https://openstax.org/books/calculus-volume-1/pages/3-1-defining-the-derivative",
    },
    "openstax-calculus-v1-3.2": {
        "title": "OpenStax Calculus Volume 1, 3.2 The Derivative as a Function",
        "url": "https://openstax.org/books/calculus-volume-1/pages/3-2-the-derivative-as-a-function",
    },
    "openstax-calculus-v1-3.3": {
        "title": "OpenStax Calculus Volume 1, 3.3 Differentiation Rules",
        "url": "https://openstax.org/books/calculus-volume-1/pages/3-3-differentiation-rules",
    },
    "openstax-calculus-v1-3.4": {
        "title": "OpenStax Calculus Volume 1, 3.4 Derivatives as Rates of Change",
        "url": "https://openstax.org/books/calculus-volume-1/pages/3-4-derivatives-as-rates-of-change",
    },
    "openstax-calculus-v1-3.5": {
        "title": "OpenStax Calculus Volume 1, 3.5 Derivatives of Trigonometric Functions",
        "url": "https://openstax.org/books/calculus-volume-1/pages/3-5-derivatives-of-trigonometric-functions",
    },
    "openstax-calculus-v1-3.6": {
        "title": "OpenStax Calculus Volume 1, 3.6 The Chain Rule",
        "url": "https://openstax.org/books/calculus-volume-1/pages/3-6-the-chain-rule",
    },
    "openstax-calculus-v1-3.7": {
        "title": "OpenStax Calculus Volume 1, 3.7 Derivatives of Inverse Functions",
        "url": "https://openstax.org/books/calculus-volume-1/pages/3-7-derivatives-of-inverse-functions",
    },
    "openstax-calculus-v1-3.8": {
        "title": "OpenStax Calculus Volume 1, 3.8 Implicit Differentiation",
        "url": "https://openstax.org/books/calculus-volume-1/pages/3-8-implicit-differentiation",
    },
    "openstax-calculus-v1-3.9": {
        "title": "OpenStax Calculus Volume 1, 3.9 Derivatives of Exponential and Logarithmic Functions",
        "url": "https://openstax.org/books/calculus-volume-1/pages/3-9-derivatives-of-exponential-and-logarithmic-functions",
    },
    "openstax-calculus-v1-4.1": {
        "title": "OpenStax Calculus Volume 1, 4.1 Related Rates",
        "url": "https://openstax.org/books/calculus-volume-1/pages/4-1-related-rates",
    },
    "openstax-calculus-v1-4.2": {
        "title": "OpenStax Calculus Volume 1, 4.2 Linear Approximations and Differentials",
        "url": "https://openstax.org/books/calculus-volume-1/pages/4-2-linear-approximations-and-differentials",
    },
    "openstax-calculus-v2-7.2": {
        "title": "OpenStax Calculus Volume 2, 7.2 Calculus of Parametric Curves",
        "url": "https://openstax.org/books/calculus-volume-2/pages/7-2-calculus-of-parametric-curves",
    },
    "mit-18.01sc-differentiation": {
        "title": "MIT OpenCourseWare 18.01SC, Unit 1: Differentiation",
        "url": "https://ocw.mit.edu/courses/18-01sc-single-variable-calculus-fall-2010/pages/1.-differentiation/",
    },
    "mit-18.01sc-session-3-rate": {
        "title": "MIT OpenCourseWare 18.01SC, Session 3: Derivative as Rate of Change",
        "url": (
            "https://ocw.mit.edu/courses/18-01sc-single-variable-calculus-fall-2010/"
            "pages/1.-differentiation/part-a-definition-and-basic-rules/"
            "session-3-derivative-as-rate-of-change/"
        ),
    },
    "mit-18.01sc-applications": {
        "title": "MIT OpenCourseWare 18.01SC, Unit 2: Applications of Differentiation",
        "url": (
            "https://ocw.mit.edu/courses/18-01sc-single-variable-calculus-fall-2010/"
            "pages/unit-2-applications-of-differentiation/"
        ),
    },
}

METHOD_FAMILY_REFERENCES = {
    "derivative_definition": frozenset(
        {"openstax-calculus-v1-3.1", "mit-18.01sc-differentiation"}
    ),
    "differentiability_and_one_sided_derivatives": frozenset(
        {"openstax-calculus-v1-3.2", "mit-18.01sc-differentiation"}
    ),
    "derivative_interpretations": frozenset(
        {
            "openstax-calculus-v1-3.4",
            "mit-18.01sc-session-3-rate",
        }
    ),
    "elementary_differentiation_rules": frozenset(
        {"openstax-calculus-v1-3.3", "mit-18.01sc-differentiation"}
    ),
    "chain_rule_and_composites": frozenset(
        {"openstax-calculus-v1-3.6", "mit-18.01sc-differentiation"}
    ),
    "inverse_exponential_logarithmic_derivatives": frozenset(
        {
            "openstax-calculus-v1-3.5",
            "openstax-calculus-v1-3.7",
            "openstax-calculus-v1-3.9",
            "mit-18.01sc-differentiation",
        }
    ),
    "higher_derivatives": frozenset(
        {"openstax-calculus-v1-3.2", "mit-18.01sc-differentiation"}
    ),
    "implicit_differentiation": frozenset(
        {"openstax-calculus-v1-3.8", "mit-18.01sc-differentiation"}
    ),
    "parametric_differentiation": frozenset(
        {"openstax-calculus-v2-7.2"}
    ),
    "related_rates": frozenset(
        {"openstax-calculus-v1-4.1", "mit-18.01sc-applications"}
    ),
    "differentials_and_linear_approximation": frozenset(
        {"openstax-calculus-v1-4.2", "mit-18.01sc-applications"}
    ),
}
