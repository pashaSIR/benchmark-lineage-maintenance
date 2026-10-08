"""Draw 100 fresh MMLU-derived MMLU-Pro items (V_d), uniform random, excluding the 50 pilot items (pilot seed 20261007).
No stratification or selection on Redux label, source, negation, model disagreement or any item content."""
import csv, hashlib, json, os, random
SEED = 20261008
H = os.path.dirname(os.path.abspath(__file__))
pilot = {r["pro_qid"] for r in csv.DictReader(open(os.path.join(H, "..", "..", "pna-pilot", "sample50.csv")))}
pop = [json.loads(l)["pro_qid"] for l in open(os.path.join(H, "..", "data", "lineage_full.jsonl"))]
pop = sorted((q for q in pop if q not in pilot), key=int)
S = random.Random(SEED).sample(pop, 100)
with open(os.path.join(H, "..", "sample100.csv"), "w", newline="") as f:
    w = csv.writer(f); w.writerow(["item_id", "pro_qid", "draw_rank"])
    for i, q in enumerate(S, 1): w.writerow([f"PRO-{q}", q, i])
print("population", len(pop), "excluded pilot", len(pilot), "seed", SEED)
print("sha256(qids)", hashlib.sha256(",".join(S).encode()).hexdigest())
