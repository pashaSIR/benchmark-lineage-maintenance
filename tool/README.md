# lineage_requeue: which items need re-review after a correction?

This tool answers one question: **if this parent item is corrected today, what else must a benchmark maintainer inspect?**

    python3 lineage_requeue.py --pro 3542 --type no_correct_answer --evidence "..." --csv queue.csv
    python3 lineage_requeue.py --parent international_law#61 --type disputed_correction
    python3 lineage_requeue.py --pro 6268 --type option_defect --option "95-100%"

It needs only the Python 3 standard library. It reads `pna-lineage-exp/data/lineage_full.jsonl` (rebuild it first: see `pna-lineage-exp/data/lineage_full.REBUILD.md`) and `pna-pilot/lineage_all.csv`, or the paths in the env vars `PNA_LINEAGE` and `PNA_LATE2024`. Worked outputs are in `examples/`.

## Specification

**Input**
- A corrected or disputed item: an MMLU parent (`subject#row`) or an MMLU-Pro `question_id`, which is resolved to its parent.
- A correction type: `wrong_key`, `no_correct_answer`, `multiple_correct`, `option_defect`, `stale`, `disputed_correction` or `other`.
- Optionally, the questioned option text (default: the parent's key) and the evidence.

**Output: one row per known descendant**
- Dataset and item ID, and its relation: Redux re-annotation, MMLU-Pro child, duplicate stem inside MMLU, or documented translation.
- Edge type: a copy, or option expansion (4→10, with the count of added options), with stem edits flagged.
- What happened to the questioned content on that edge: `inherited`, `added`, `removed`, `rewritten`, or `not inherited`.
- The child's key relative to the parent, and whether it changed between the late-2024 and Feb-2026 MMLU-Pro snapshots, which shows whether someone already fixed it.
- A rank:
  - 0: the annotation layer.
  - 1: the item carries the questioned content.
  - 2: needs a check.
  - 3: documented derivative, membership not verified.
  - `-`: unaffected, because the content entered downstream.
- The proposed repository and a status (`not filed` until updated from `maintainer/OUTCOMES.csv`).

## What it covers, and what it does not

- **Lineage is reconstructed, not published.** MMLU-Pro items are linked to MMLU parents by normalized exact stem match, falling back to a fuzzy stem match (similarity ≥ 0.85, same subject). 6,807 of 6,808 MMLU-derived items in the Feb-2026 snapshot got a parent. Heavily rewritten stems would be missed, and items whose stems MMLU-Pro edited beyond the fuzzy threshold do not appear.
- **Data are GitHub snapshots** (commit f418b116 eval_results), not the current Hugging Face revision.
- **Translations are not joined.** MMMLU, Global-MMLU and MMLU-ProX are listed from their documentation only, so the tool says "re-review if present", never "affected". Hugging Face was unreachable from the environment that built this, so no translation descendant was spot-checked.
- **Duplicates.** When MMLU contains identical rows, all their MMLU-Pro children attach to one parent ID. That is why 1932 and 1933 both appear under `international_law#61`. 157 parents have two MMLU-Pro children with identical option sets. MMLU-Pro duplicates were already reported in Hugging Face discussions #26 and #33, so this count is a reproduction, not a finding.
- **Nothing here is a verdict.** The tool says where to look. Whether an item is wrong is for the evidence and the maintainer.

## Smallest next steps (no budget needed)

1. Join MMMLU, Global-MMLU and MMLU-ProX by item ID or stem from a machine that can reach Hugging Face, so rank-3 rows become real rows.
2. Read statuses from `maintainer/OUTCOMES.csv`, so the queue shows confirmed, rejected or fixed.
3. Emit each edge as PROV-O / Croissant `prov:wasDerivedFrom` records, so the output is in a standard format rather than a new one.
