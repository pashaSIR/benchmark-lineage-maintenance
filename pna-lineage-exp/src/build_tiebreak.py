"""Tiebreak packet (rubric section 5): items where Adj-1 and Adj-2 split on defect vs not, or agree on defect but disagree on origin (O1==O4)."""
import json, os, random
H = os.path.dirname(os.path.abspath(__file__)); D = os.path.join(H, "..", "data"); J = os.path.join(D, "adjudicator_json")
mp = {"__file__": os.path.join(H, "make_packets.py")}; exec(compile(open(os.path.join(H, "make_packets.py")).read().replace("\nmain()\n", "\n"), "make_packets.py", "exec"), mp)
DEF = ("confirmed", "probable"); up = lambda o: "UP" if o in ("O1", "O4") else o
A1, A2 = {}, {}
for p in ("ADJ1", "ADJ2"):
    A1.update({x["item_id"]: x for x in json.load(open(f"{J}/{p}_r1.json"))}); A2.update({x["item_id"]: x for x in json.load(open(f"{J}/{p}_r2.json"))})
tie = [i for i in sorted(A1) if (A1[i]["severity"] in DEF) != (A2[i]["severity"] in DEF)
       or (A1[i]["severity"] in DEF and A2[i]["severity"] in DEF and up(A1[i]["origin"]) != up(A2[i]["origin"]))]
blocks = []
for i in tie:
    v = [A1[i], A2[i]]; random.Random(int(i[4:])).shuffle(v)
    txt = "\n".join(f"  - Adjudicator {k}: severity {x['severity']}, type {x['defect_type']}, origin {x['origin']}, key {x.get('correct_key')}; {x['rationale']} [evidence: {x['evidence']}]" for k, x in zip("XY", v))
    blocks.append(mp["item_block"](mp["L"][i[4:]]) + "\n" + mp["lineage"](mp["L"][i[4:]]) + "\nTWO PRIOR ADJUDICATIONS (they disagree; verify, do not split the difference):\n" + txt)
open(os.path.join(D, "packets", "TIE.txt"), "w").write(mp["FAMILY"] + "\n\n" + "\n\n".join(blocks) + "\n")
json.dump(tie, open(os.path.join(D, "packets", "TIE.ids.json"), "w")); print(tie)
