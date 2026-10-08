# data/lineage_full.jsonl (not included)

This file holds the full question and option text of all 6,808 MMLU-derived MMLU-Pro items and their MMLU parents. It is left out to avoid redistributing a near-complete copy of third-party datasets. To rebuild it:

1. Clone into `$PNA_DL` (default `./dl`):
   - `git clone https://github.com/TIGER-AI-Lab/MMLU-Pro`, then `git -C MMLU-Pro checkout f418b116db00b065c2aea046518d8fcf74d39872`
   - `git clone https://github.com/FranxYao/chain-of-thought-hub cot`, then `git -C cot checkout 461e2d551f3f12d54caee75fa1e915fdbc3e9d12`
   - `git clone https://github.com/aryopg/mmlu-redux`, then `git -C mmlu-redux checkout 4563cfa79b659d76716e5b6019f46bba85fa02db`
2. Run `cd pna-lineage-exp/src && python3 build_lineage.py`.
3. Verify: `sha256sum ../data/lineage_full.jsonl` should print
   `3bcec9638489644a1cef851d17253a160bc17bbc2bee28429d94d72d2e91f720`

`tool/lineage_requeue.py` and `maintainer/tests/check_corrections.py` read this file.
