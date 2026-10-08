# Third-party data and licenses

This repository contains scripts, hashes, item IDs, diffs, and small excerpts of benchmark items that are needed to document specific findings: the reviewer packets for 100 + 50 sampled items, the cases, and a 78-row re-review list. It does not contain complete copies of the datasets below. The full lineage file can be rebuilt with the instructions in `pna-lineage-exp/data/lineage_full.REBUILD.md`.

| Source | Used for | License (as stated in the source repository) |
|---|---|---|
| MMLU (Hendrycks et al.), via `hendrycks/test` and its verbatim copy in `FranxYao/chain-of-thought-hub@461e2d5` | Parent items | MIT |
| MMLU-Pro (Wang et al.), `TIGER-AI-Lab/MMLU-Pro@f418b116`, records embedded in `eval_results/` | Derived items | Apache License 2.0 |
| MMLU-Redux (Gema et al.), `aryopg/mmlu-redux@4563cfa` | Annotations | CC BY 4.0 |

Excerpts remain under their original licenses and are attributed to the datasets above. Licenses were read from each repository's LICENSE file on 2026-10-08. The Hugging Face dataset cards were not checked.

Code and analysis written for this project are released under the MIT License (see `LICENSE`). That license does not cover the third-party excerpts, which keep the licenses above.
