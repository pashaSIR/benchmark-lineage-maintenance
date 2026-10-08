# Frozen defect rubric and pre-registration

Frozen 2026-10-07, before the 100-item sample was drawn or any sampled item was viewed.
Nothing in this file is edited after sampling. Any later deviation is logged in `results_summary.md` under "Deviations", not here.

## 1. Defect types (one primary type per flagged item)

| Code | Type | Definition |
|---|---|---|
| T1 | Wrong key | The keyed option is not the best answer, and a different listed option is. |
| T2 | No uniquely correct answer | No listed option is correct, or the item gives no basis to prefer one option (excluding T3). |
| T3 | Added option creates second correct answer | An option that is not in the item's MMLU parent is as correct as (or more correct than) the key. Requires lineage to name with certainty; an item-only reviewer who sees two defensible options records T3 if it suspects one was added, otherwise T2. |
| T4 | Underspecified / missing context | The stem lacks information needed to answer (truncated passage, missing figure/table, missing referent, assumes a source the reader lacks). |
| T5 | Transformation changes intended meaning | Editing of the stem or options (rewording, deletion, truncation, reordering, conversion of "all of the above" etc.) changed what is asked or what an option means. |
| T6 | Stale / factually obsolete | The key was defensible when written but is wrong under current authoritative knowledge, law, or statistics. |
| T7 | Scoring / option-set defect | Duplicate or near-duplicate options, malformed options, an option that refers to other options that are no longer present ("both A and B"), garbled text, key letter out of range. |
| T8 | No material defect | None of the above at a level that would change a careful expert's scoring of a model's answer. |

"Material" means: a domain expert would accept a model answer other than the key, or would refuse to score the item. Style, mild awkwardness, and typos that do not change the answer are T8.

## 2. Severity (per item, per reviewer)

- **confirmed**: the reviewer can cite decisive evidence (a calculation, an authoritative source, or a verbatim comparison) that the defect exists.
- **probable**: more likely than not a defect; evidence is strong but not decisive.
- **ambiguous**: reasonable experts could disagree; arguable.
- **none**: no material defect (T8).

## 3. Origin (where the defect entered)

| Code | Origin |
|---|---|
| O1 | Inherited from MMLU (present in the MMLU parent as written) |
| O2 | Introduced by MMLU-Pro option augmentation (added distractors) |
| O3 | Introduced by MMLU-Pro deletion / reordering / stem or option editing |
| O4 | Source problem (upstream of MMLU: the exam/textbook the parent was copied from; includes stale facts) |
| O5 | Introduced by a later MMLU-Pro revision (downstream version change) |
| OU | Unresolved |

Every reviewer, in every condition, records an origin for each flagged item, using OU when it cannot tell. O1 vs O4: use O4 only when the reviewer has evidence about the upstream source; otherwise a parent-present defect is O1. For localization scoring, O1 and O4 are both "upstream" and count as matching each other (pre-registered collapse, because MMLU copies its sources and the distinction depends on source access that no arm has reliably).

## 4. Review conditions

- **A, item-only**: MMLU-Pro question, options, key. External domain evidence allowed. No parent, no Redux, no diffs, no version history; reviewers are told not to look up the item in any benchmark dataset or annotation.
- **B, lineage-aware**: everything in A plus MMLU parent (question, 4 options, key), exact diff (options added/dropped/reordered, stem edits), MMLU-Redux label, correction, reason and upstream source when the parent was annotated, MMLU-Pro version history of this item (late-2024 vs Feb-2026 snapshot), and a short family description.
- **C, extra-evidence control**: same information as A, with a mandatory extended verification protocol (solve independently before reading the key, check every option, consult external sources for every factual claim the key depends on), intended to match or exceed B's effort without lineage.
- Each condition is run by separate, isolated LLM reviewer agents. No agent sees another condition's verdicts. Item order is randomized per condition with fixed seeds.

## 5. Adjudication and gold

- **Adjudication set**: every item that any arm marks confirmed, probable or ambiguous, plus a random 15% (fixed seed) of the remaining items that all arms call none.
- Two independent adjudicator agents (Adj-1, Adj-2) see the item, the full lineage packet, and the pooled, de-duplicated defect claims from all arms with arm labels removed and order shuffled. They verify each claim independently and may find new ones. They do not see each other's verdicts.
- **Gold defect (primary)**: both adjudicators rate confirmed or probable. **Gold clean**: both rate ambiguous or none. Disagreements on that binary split go to a third adjudicator (Adj-3) who sees both rationales without names and makes the binary call. Items not in the adjudication set are gold clean.
- **Gold strict (sensitivity)**: both adjudicators rate confirmed.
- **Gold origin**: Adj-1's origin if Adj-1 and Adj-2 agree (after the O1/O4 collapse), otherwise Adj-3's.
- All gold labels are **provisional**: LLM adjudicators, not a domain-expert panel.

## 6. Outcomes and pre-registered thresholds

- **Arm detection**: arm severity is confirmed or probable. (Sensitivity: including ambiguous.)
- **Recall** = arm detections among gold defects / gold defects. **Precision** = gold defects among arm detections.
- **Primary quantity: Δ recall = recall(B) − recall(A)**, in percentage points.
  - **meaningful win**: ≥ +10 pp
  - **weak**: +1 to +9 pp
  - **fail**: ≤ 0 pp
- **Lineage-specific test**: Δ recall(B − C). If B − C < +10 pp while B − A ≥ +10 pp, the gain is attributed to extra evidence/effort, not lineage.
- **Localization**: share of gold defects whose arm origin matches gold origin (O1≡O4), reported (i) over all gold defects (an undetected defect counts as not localized) and (ii) over gold defects detected by both A and B.
- **Propagation**: for each gold defect with upstream origin (O1/O4), count descendants: other MMLU-Pro items sharing the parent; the MMLU-Redux copy; and public derivative datasets that by their documentation contain every MMLU test item (translations) or every MMLU-Pro item. Report descendants flagged for re-review per confirmed upstream defect. The claim is "requires re-review", not "is wrong".
- **Secondary**: time per item (agent wall-clock, not human minutes), time per gold defect, ambiguous counts, verdicts changed in B relative to A (same item, different reviewer), transformation-caused vs inherited counts, Redux "ok" parents overturned, Cohen's κ between Adj-1 and Adj-2 on defect/no-defect, type, and origin.
- **Uncertainty**: paired bootstrap (items resampled, 10,000 draws, seed 1) 95% CI for Δ recall; exact McNemar on discordant gold-defect detections.

## 7. Kill conditions (from the brief, verbatim intent)

Downgrade to a maintenance recommendation if any of: Δ recall(B−A) < +10 pp; B rarely changes origin localization; propagation finds almost no actionable descendants; provenance reconstruction is too costly; adjudicator disagreement is so high that "defect" cannot be reproduced (pre-registered: κ < 0.4 on defect/no-defect).

## 8. Publication decision rule

- **A. Publishable audit result**: Δ recall(B−A) ≥ +10 pp and Δ recall(B−C) ≥ +10 pp (or C not run), localization lift ≥ +20 pp, adjudicator κ ≥ 0.4.
- **B. Useful maintenance practice**: lineage materially improves localization or propagation, but recall lift fails the A rule.
- **C. Kill**: no recall lift, no localization lift, and no actionable propagation.
