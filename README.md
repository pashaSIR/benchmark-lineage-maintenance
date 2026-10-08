# Lineage-linked benchmark maintenance (Run G materials)

Materials for the research note "Benchmark Audits Stop at the Dataset Boundary. Corrections Should Not." (Pasha, October 2026). All reviewer and adjudicator outputs are from LLM agents; no label has been checked by a human expert.

## Contents

- `pna-lineage-exp/` is the 100-item three-arm experiment (seed 20261008). It holds the frozen rubric (`rubric.md`), sample list (`sample100.csv`), the exact packet each reviewer and adjudicator saw (`data/packets/`), prompts (`data/prompts/`), raw outputs (`data/reviewer_json/`, `data/adjudicator_json/`), per-arm verdicts, the adjudication ledger, and the analysis script with its output (`analysis.py`, `tables/results.json`). Start with its `README.md`. Note that `results_summary.md` is the run's original summary and contains claims the public note retracts, chiefly the "publishable audit result" decision and the detection thesis. The note is the current interpretation.
- `pna-pilot/` is the earlier 50-item pilot (seed 20261007). It holds lineage reconstruction for all MMLU-derived MMLU-Pro items, the sample and audit, the inheritance, clustering and sampling analyses, and `tables/`. The experiment reuses its loaders (`load.py`, `link.py`), so keep the two folders side by side.
- `pilot_sample50_ids.csv` lists the pilot's 50 MMLU-Pro question IDs, MMLU parents (subject#0-based row of the Hendrycks test CSV) and normalized-question hashes, for checking overlap with other samples.
- `tool/` holds `lineage_requeue.py`. Given a corrected or disputed item, it lists known descendants, what happened to the questioned content on each edge, and a ranked re-review queue. Its README covers scope and limits; worked outputs are in `examples/`.
- `maintainer/` holds the ranked defect cases, the 78-item re-review queue, the case ledger, the per-correction regression checks (`tests/check_corrections.py`) and the re-review queues archived before submission.
- `MANIFEST.sha256` has checksums for every file.

## Data sources

Hugging Face was unreachable from the environment where this was run, so all data come from GitHub.

- MMLU test: FranxYao/chain-of-thought-hub @461e2d551f3f12d54caee75fa1e915fdbc3e9d12, MMLU/data/test
- MMLU-Redux: aryopg/mmlu-redux @4563cfa79b659d76716e5b6019f46bba85fa02db
- MMLU-Pro: TIGER-AI-Lab/MMLU-Pro @f418b116db00b065c2aea046518d8fcf74d39872, records embedded in `eval_results/` (late-2024 snapshot for the pilot, February 2026 snapshot for the experiment)

Several files contain small excerpts of item text from these datasets, which keep their own licenses; see `THIRD_PARTY_NOTICES.md`. The full lineage file (`pna-lineage-exp/data/lineage_full.jsonl`) is not included; rebuild it with `pna-lineage-exp/data/lineage_full.REBUILD.md`. The tool and the regression checks need it.

## Reproducing

Clone the three repositories into `$PNA_DL` (chain-of-thought-hub as `cot`), then follow `pna-pilot/README.md` and `pna-lineage-exp/README.md`.

## License and citation

Code and analysis: MIT (`LICENSE`). Benchmark excerpts keep their original licenses (`THIRD_PARTY_NOTICES.md`). To cite, use `CITATION.cff` or the Zenodo DOI of the release you used.
