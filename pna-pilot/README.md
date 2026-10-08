# PNA micro-pilot (2026-10-07)
Data (Hugging Face blocked from the sandbox; all from GitHub):
- MMLU test: github.com/FranxYao/chain-of-thought-hub @461e2d5 MMLU/data/test (verbatim Hendrycks CSVs, 14,042 items)
- MMLU-Redux (5,700 items, 57 subjects): github.com/aryopg/mmlu-redux @4563cfa mmlu_redux/*.csv
- MMLU-Pro test (12,032 items): records embedded in github.com/TIGER-AI-Lab/MMLU-Pro @f418b11 eval_results/*.zip.
  V_c = claude-3-5-sonnet-20241022 outputs (late-2024 snapshot, used throughout); V_b = Llama-3.1 outputs; V_a = Llama-2 outputs.
  Not checked against the current Hugging Face revision (the card logs errata to Jan 2026).
Clone those three repos into $PNA_DL (default ./dl; chain-of-thought-hub cloned as `cot`), then:
  python3 link.py        -> lineage_all.csv (6,810 MMLU-derived Pro items, parent, Redux label, outcome)
  python3 sample50.py    -> sample50.csv (seed 20261007)
  python3 analysis.py; python3 analysis2.py; python3 analysis3.py -> tables/
Manual audit (Claude as auditor, not a domain expert panel): sample50_audit.csv, checks_t2_f2.md
