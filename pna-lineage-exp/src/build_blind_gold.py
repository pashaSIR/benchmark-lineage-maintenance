"""Robustness check added after the primary analysis (logged as a deviation in results_summary.md):
the primary adjudicators saw lineage, which could bias gold toward Condition B. Here two further adjudicators judge the same
32 items WITHOUT lineage. To direct attention equally, each item lists the option letters any arm suggested as correct (lineage-free field)."""
import csv, json, os
H = os.path.dirname(os.path.abspath(__file__)); E = os.path.join(H, ".."); D = os.path.join(E, "data")
mp = {"__file__": os.path.join(H, "make_packets.py")}; exec(compile(open(os.path.join(H, "make_packets.py")).read().replace("\nmain()\n", "\n"), "make_packets.py", "exec"), mp)
R = {a: {r["item_id"]: r for r in csv.DictReader(open(os.path.join(E, f)))} for a, f in
     (("A", "condition_A_item_only.csv"), ("B", "condition_B_lineage.csv"), ("C", "condition_C_extra_evidence.csv"))}
adj = json.load(open(os.path.join(D, "adjudication_set.json")))["order"]
blocks = []
for i in adj:
    r = mp["L"][i[4:]]
    sug = sorted({R[a][i]["suggested_key"] for a in "ABC" if R[a][i]["suggested_key"] not in ("", "None", None) and R[a][i]["suggested_key"] != r["key"]})
    blocks.append(mp["item_block"](r) + "\nOptions other reviewers suggested might be correct instead of / as well as the key: " + (", ".join(sug) if sug else "none"))
open(os.path.join(D, "packets", "BLIND.txt"), "w").write("\n\n".join(blocks) + "\n")
json.dump(adj, open(os.path.join(D, "packets", "BLIND.ids.json"), "w")); print(len(adj))
