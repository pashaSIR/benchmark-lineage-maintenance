"""Draw the 50-item micro-pilot sample: uniform random over all MMLU-derived MMLU-Pro test items (V_c snapshot), seed 20261007."""
import csv, random
SEED = 20261007
R = sorted(csv.DictReader(open("lineage_all.csv")), key=lambda r: int(r["pro_qid"]))
S = random.Random(SEED).sample(R, 50)
with open("sample50.csv", "w", newline="") as f:
    w = csv.DictWriter(f, list(R[0].keys())); w.writeheader(); w.writerows(S)
print(" ".join(r["pro_qid"] for r in S))
