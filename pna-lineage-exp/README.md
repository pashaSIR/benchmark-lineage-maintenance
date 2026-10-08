# Lineage-aware vs item-only benchmark review (MMLU → MMLU-Redux → MMLU-Pro), 2026-10-07

Question: does item-level lineage improve benchmark-defect detection and localization compared with reviewing the derived item alone?
Results: `results_summary.md` (PROVISIONAL: LLM reviewers and adjudicators). Frozen rubric and pre-registration: `rubric.md`.

## Files
- `rubric.md` defect types, severity, origin codes, thresholds, decision rule (frozen before sampling)
- `sample100.csv` the 100 items (stable id `PRO-<question_id>`), seed 20261008, pilot's 50 excluded
- `condition_A_item_only.csv`, `condition_B_lineage.csv`, `condition_C_extra_evidence.csv` per-item verdicts (`batch` = reviewer agent)
- `adjudication.csv` 32 adjudicated items: both adjudicators, tiebreak, gold labels (all provisional)
- `analysis.py` all metrics -> `tables/results.json`
- `src/build_lineage.py` lineage for all 6,808 MMLU-derived items -> `data/lineage_full.jsonl`
- `src/draw_sample.py`, `src/make_packets.py` (order seeds A 101, B 102, C 103), `src/build_adjudication.py` (random clean seed 20261009, order 20261010), `src/build_tiebreak.py`, `src/build_blind_gold.py`
- `data/packets/` exact text each reviewer/adjudicator saw; `data/reviewer_json/`, `data/adjudicator_json/` raw outputs; `data/agent_timing.csv`

## Data (Hugging Face blocked from the sandbox; all from GitHub)
- MMLU-Pro (under review): TIGER-AI-Lab/MMLU-Pro @ f418b116db00b065c2aea046518d8fcf74d39872, `eval_results/model_outputs_gemini-3.1-pro_5-shots.zip` (Feb 2026). Prior version: `model_outputs_claude-3-5-sonnet-20241022_5shots.json.zip` (late 2024).
- MMLU test: FranxYao/chain-of-thought-hub @ 461e2d551f3f12d54caee75fa1e915fdbc3e9d12, MMLU/data/test
- MMLU-Redux: aryopg/mmlu-redux @ 4563cfa79b659d76716e5b6019f46bba85fa02db, mmlu_redux/*.csv

## Reproduce
Clone the three repos into `$PNA_DL` (default ./dl; chain-of-thought-hub as `cot`). Loaders are reused from `../pna-pilot/` (load.py, link.py).
    cd src && python3 build_lineage.py && python3 draw_sample.py && python3 make_packets.py
    # reviewers write data/reviewer_json/{A,B,C}{1-4}.json, then:
    python3 build_adjudication.py ../data/reviewer_json
    # adjudicators write data/adjudicator_json/ADJ{1,2}_r{1,2}.json, then:
    python3 build_tiebreak.py && python3 build_blind_gold.py
    cd .. && python3 analysis.py
Reviewer and adjudicator instructions are in `data/prompts/`.
