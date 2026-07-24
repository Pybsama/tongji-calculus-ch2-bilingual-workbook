# Mathematical cross-review

## Review routing

- Part A (Sections 1-2) was independently reviewed for one-sided derivatives, parameter classification, differentiability/continuity logic, and inverse-function assumptions.
- Part B (Sections 2-3) was independently reviewed for domains, logarithmic and inverse differentiation, piecewise differentiability, nth-derivative coefficients, cyclic signs, and induction proofs.
- Part C (Sections 4-5) was independently reviewed for implicit second derivatives, parametric second-derivative denominators, related-rate signs and units, and differential approximations.

## Confirmed corrections

- C027: changed the Chinese radius-error condition from equality to `|dr|≤0.02 cm`, matching the intended maximum-error statement.
- C020, C028, C029, and C031: replaced an unnecessary English numeric chapter reference with “this chapter” so the bilingual numerical-token check reflects the same mathematical content.
- Q022 after global ordering: expanded the English derivation so it satisfies the detailed-solution threshold without changing the mathematics.

## Targeted recalculations

- The implicit second derivatives represented by global items Q074 and its companion were independently recalculated.
- Parametric second derivatives were checked for the required `[x′(t)]³` denominator.
- All five related-rate items were checked for sign, time unit, and length/area/volume unit.
- The 2026th-derivative cycle, repeated-pole rational nth derivative, logarithmic-square harmonic-number formula, and general separable implicit second-derivative formula were independently recalculated.

## Bilingual heuristic review

The four non-blocking symbol-count warnings in `bilingual_validation.md` were manually reviewed:

- Q025 states two limiting conclusions in prose in English rather than repeating the `→` symbol.
- Q074 combines the final implicit-second-derivative algebra into one English sentence.
- Q099 refers to the already displayed formula as “the stated formula” instead of printing it twice.

The formulas, hypotheses, and answers remain mathematically equivalent in both languages.

## Result

No unresolved mathematical blocker or Chapter 3-or-later method remains in the corpus.
