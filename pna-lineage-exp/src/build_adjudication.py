"""Assemble condition CSVs from reviewer JSON, build the adjudication set (all items any arm flagged at
confirmed/probable/ambiguous + random 15% of all-clean items, seed 20261009) and render blinded adjudication packets."""
import csv, glob, json, math, os, random, sys
H = os.path.dirname(os.path.abspath(__file__)); E = os.path.join(H, ".."); D = os.path.join(E, "data")
OUT = sys.argv[1]  # dir with reviewer JSON (A1..C4.json)
sys.path.insert(0, H)
import importlib.util
spec = importlib.util.spec_from_file_location("mp", os.path.join(H, "make_packets.py"))
src = open(os.path.join(H, "make_packets.py")).read().replace("\nmain()\n", "\n")
mp = {"__file__": os.path.join(H, "make_packets.py")}; exec(compile(src, "make_packets.py", "exec"), mp)
S = ["PRO-" + r["pro_qid"] for r in csv.DictReader(open(os.path.join(E, "sample100.csv")))]
FN = {"A": "condition_A_item_only.csv", "B": "condition_B_lineage.csv", "C": "condition_C_extra_evidence.csv"}
R = {}
for c in "ABC":
    rows = []
    for b in range(1, 5):
        f = os.path.join(OUT, f"{c}{b}.json")
        if not os.path.exists(f): continue
        ids = json.load(open(os.path.join(D, "packets", f"{c}{b}.ids.json")))
        got = json.load(open(f)); assert sorted(x["item_id"] for x in got) == sorted(ids), (c, b)
        for x in got: x["batch"] = f"{c}{b}"; rows.append(x)
    R[c] = {x["item_id"]: x for x in rows}
    if rows:
        keys = list(dict.fromkeys(k for x in rows for k in x))
        with open(os.path.join(E, FN[c]), "w", newline="") as fh:
            w = csv.DictWriter(fh, keys); w.writeheader(); w.writerows(sorted(rows, key=lambda x: S.index(x["item_id"])))
flag = lambda x: x["severity"] in ("confirmed", "probable", "ambiguous")
flagged = [i for i in S if any(i in R[c] and flag(R[c][i]) for c in "ABC")]
clean = [i for i in S if i not in flagged]
rand = sorted(random.Random(20261009).sample(clean, math.ceil(0.15 * len(clean))), key=S.index)
adj = flagged + rand
random.Random(20261010).shuffle(adj)
json.dump({"flagged": flagged, "random_clean": rand, "order": adj}, open(os.path.join(D, "adjudication_set.json"), "w"), indent=1)
L = mp["L"]
blocks = []
for i in adj:
    r = L[i[4:]]
    cl = [R[c][i] for c in "ABC" if i in R[c] and flag(R[c][i])]
    random.Random(int(i[4:])).shuffle(cl)
    seen, claims = set(), []
    for x in cl:
        k = (x["defect_type"], x.get("suggested_key"))
        if k in seen: continue
        seen.add(k); claims.append(f"  - claim: type {x['defect_type']}, severity {x['severity']}, suggested key {x.get('suggested_key')}; {x['reason']} [evidence: {x['evidence']}]")
    blocks.append(mp["item_block"](r) + "\n" + mp["lineage"](r) + "\nREVIEWER CLAIMS (pooled from several anonymous reviewers, deduplicated, unordered; verify each, do not count votes):\n" + ("\n".join(claims) if claims else "  (no reviewer flagged this item)"))
half = (len(blocks) + 1) // 2
for k, part in enumerate([blocks[:half], blocks[half:]], 1):
    open(os.path.join(D, "packets", f"ADJ{k}.txt"), "w").write(mp["FAMILY"] + "\n\n" + "\n\n".join(part) + "\n")
    json.dump(adj[:half] if k == 1 else adj[half:], open(os.path.join(D, "packets", f"ADJ{k}.ids.json"), "w"))
print("flagged", len(flagged), "random clean", len(rand), "total", len(adj))
