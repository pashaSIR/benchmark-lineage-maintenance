# Maintainer submission kit

- `cases.md`: the ranked cases, with all eleven fields for each.
- Submissions: the four objective MMLU-Pro cases (936, 6268, 6599, 3542) go to the MMLU-Pro maintainers in one Hugging Face discussion, with the 78-item re-review list; the two MMLU-Redux annotation cases (GitHub CSV rows 19 and 99) go to the MMLU-Redux maintainers separately. Both were filed on 2026-10-08: [MMLU-Pro discussion #55](https://huggingface.co/datasets/TIGER-Lab/MMLU-Pro/discussions/55) and [MMLU-Redux issue #8](https://github.com/aryopg/mmlu-redux/issues/8). The texts as filed are in `submissions/`.
- `redux_flagged_mmlu_pro_items.csv`: the 78-item **re-review queue**. Redux flags 78 parent keys, and 74 survive unchanged in the pinned MMLU-Pro snapshot. These are not confirmed errors.
- `case_ledger.csv`: the machine-readable ledger, with IDs, revisions, evidence, submission links, outcomes and timestamps. Update it as things happen.
- `tests/check_corrections.py`: one regression check per correction. Run it against any MMLU-Pro export. FAIL means the defect is still present; the guards (1932/1933) FAIL if someone applies Redux's wrong correction. Run against the Feb-2026 snapshot it gives 4 FAIL and 2 PASS.
- `queues_archive/2026-10-08T055248Z/`: the re-review queues, generated before any submission, with sha256 manifests of the outputs, the tool and the input data.

## Outcome statuses

Use only these:

- Confirmed and fixed
- Confirmed, documented (not changed in the frozen release)
- Acknowledged as ambiguous
- Rejected with reason
- No response as of DATE

Silence is never support. A confirmation validates that one correction, not the experiment.

## Status table (always give the denominator)

| Case | Submitted | Evidence | Maintainer outcome | Dataset action | Descendant action |
|---|---|---|---|---|---|
| 936 | | *Cooper v. Oklahoma* | | | |
| 6268 | | Interval logic | | | |
| 6599 | | MedlinePlus Genetics | | | |
| 3542 | | Boltzmann ratio + band ranges | | | |
| Redux international_law (row 19) | | ASIL Benchbook | | | |
| Redux college_chemistry (row 99) | | as 3542 | | | |

Sentence template: "As of DATE, maintainers had fixed X of 6 submissions, documented Y without changing the release, marked Z ambiguous, rejected R, and had not responded to N."

## Order of events

The re-review queues in `queues_archive/` and this repository's first release were committed before any submission was filed, so the queues predate any maintainer response. Each case was re-checked against the live Hugging Face revision before filing; that revision is recorded in `case_ledger.csv` (`current_revision_checked`).
