"""Analysis for the lineage-aware review experiment. Run from this directory after adjudication:
    python3 analysis.py            -> tables/results.json, tables/results_table.md, adjudication.csv
Implements the pre-registered rules in rubric.md (sections 5-8). All gold labels are provisional (LLM adjudicators)."""
import collections, csv, json, math, os, random
from itertools import product
E = os.path.dirname(os.path.abspath(__file__)); D = os.path.join(E, "data"); T = os.path.join(E, "tables")
os.makedirs(T, exist_ok=True)
DEF = ("confirmed", "probable")
S = ["PRO-" + r["pro_qid"] for r in csv.DictReader(open(os.path.join(E, "sample100.csv")))]
L = {"PRO-" + json.loads(l)["pro_qid"]: json.loads(l) for l in open(os.path.join(D, "lineage_full.jsonl"))}
ARMS = {"A": "condition_A_item_only.csv", "B": "condition_B_lineage.csv", "C": "condition_C_extra_evidence.csv"}
R = {a: {r["item_id"]: r for r in csv.DictReader(open(os.path.join(E, f)))} for a, f in ARMS.items()}
ADJ = json.load(open(os.path.join(D, "adjudication_set.json")))
def loadj(p): return {x["item_id"]: x for x in json.load(open(p))} if os.path.exists(p) else {}
J = os.path.join(D, "adjudicator_json")
A1 = {**loadj(f"{J}/ADJ1_r1.json"), **loadj(f"{J}/ADJ2_r1.json")}
A2 = {**loadj(f"{J}/ADJ1_r2.json"), **loadj(f"{J}/ADJ2_r2.json")}
A3 = loadj(f"{J}/TIE.json")
up = lambda o: "UP" if o in ("O1", "O4") else o

# ---- gold
G = {}
for i in S:
    if i not in ADJ["order"]:
        G[i] = {"gold_defect": False, "strict": False, "origin": "", "type": "T8", "basis": "not adjudicated (all arms clean, not in random check)"}; continue
    a, b = A1[i], A2[i]
    da, db = a["severity"] in DEF, b["severity"] in DEF
    if da == db:
        gd, basis = da, "Adj-1 and Adj-2 agree"
    else:
        gd, basis = A3[i]["severity"] in DEF, "Adj-3 tiebreak"
    if gd:
        if up(a["origin"]) == up(b["origin"]) and a["severity"] in DEF and b["severity"] in DEF: o, t = a["origin"], a["defect_type"]
        elif i in A3: o, t = A3[i]["origin"], A3[i]["defect_type"]
        else: o, t = a["origin"], a["defect_type"]  # both adjudicators call defect but disagree on origin and no tiebreak run
    else: o, t = "", "T8"
    G[i] = {"gold_defect": gd, "strict": a["severity"] == "confirmed" and b["severity"] == "confirmed", "origin": o, "type": t, "basis": basis,
            "any_ambiguous": "ambiguous" in (a["severity"], b["severity"])}

det = {a: {i: R[a][i]["severity"] in DEF for i in S} for a in R}
det_amb = {a: {i: R[a][i]["severity"] in DEF + ("ambiguous",) for i in S} for a in R}
gold = [i for i in S if G[i]["gold_defect"]]; strict = [i for i in S if G[i]["strict"]]

def recall(arm, pos, d=det): return sum(d[arm][i] for i in pos) / len(pos) if pos else float("nan")
def precision(arm, d=det):
    f = [i for i in S if d[arm][i]]; return sum(G[i]["gold_defect"] for i in f) / len(f) if f else float("nan")
def loc(arm, pos): return sum(det[arm][i] and up(R[arm][i]["origin"]) == up(G[i]["origin"]) for i in pos)

def boot(a1, a2, pos_key="gold_defect", n=10000):
    rng = random.Random(1); out = []
    for _ in range(n):
        s = [S[rng.randrange(len(S))] for _ in S]; p = [i for i in s if G[i][pos_key]]
        if p: out.append(sum(det[a1][i] for i in p) / len(p) - sum(det[a2][i] for i in p) / len(p))
    out.sort(); return out[int(.025 * len(out))], out[int(.975 * len(out)) - 1]

def mcnemar(a1, a2, pos):
    b = sum(det[a1][i] and not det[a2][i] for i in pos); c = sum(det[a2][i] and not det[a1][i] for i in pos); n = b + c
    p = min(1, 2 * sum(math.comb(n, k) for k in range(0, min(b, c) + 1)) / 2 ** n) if n else 1.0
    return b, c, p

def kappa(x, y):
    n = len(x); cats = sorted(set(x) | set(y)); po = sum(a == b for a, b in zip(x, y)) / n
    pe = sum((x.count(c) / n) * (y.count(c) / n) for c in cats); return (po - pe) / (1 - pe) if pe < 1 else float("nan")

tim = {r["batch"]: r for r in csv.DictReader(open(os.path.join(D, "agent_timing.csv")))}
mins = {a: sum(int(tim[f"{a}{b}"]["duration_ms"]) for b in range(1, 5)) / 60000 for a in R}
res = {"n_items": len(S), "n_gold_defects": len(gold), "n_gold_strict": len(strict), "gold_items": gold, "arms": {}}
for a in R:
    found = [i for i in gold if det[a][i]]
    res["arms"][a] = {"flags": sum(det[a].values()), "gold_found": len(found), "recall": recall(a, gold), "precision": precision(a),
        "recall_strict": recall(a, strict), "recall_incl_ambiguous": recall(a, gold, det_amb), "precision_incl_ambiguous": precision(a, det_amb),
        "correct_origin_all_gold": loc(a, gold), "ambiguous_cases": sum(R[a][i]["severity"] == "ambiguous" for i in S),
        "lookups": sum(int(R[a][i]["n_lookups"] or 0) for i in S), "agent_minutes_total": mins[a], "minutes_per_item": mins[a] / len(S),
        "minutes_per_gold_defect_found": mins[a] / len(found) if found else None}
both = [i for i in gold if det["A"][i] and det["B"][i]]
res["localization_detected_by_both_AB"] = {"n": len(both), "A": loc("A", both), "B": loc("B", both)}
for a1, a2 in (("B", "A"), ("B", "C"), ("C", "A")):
    res[f"delta_recall_{a1}{a2}_pp"] = 100 * (recall(a1, gold) - recall(a2, gold))
    lo, hi = boot(a1, a2); res[f"delta_recall_{a1}{a2}_ci95_pp"] = [100 * lo, 100 * hi]
    res[f"mcnemar_{a1}{a2}"] = dict(zip((f"{a1}_only", f"{a2}_only", "p_exact"), mcnemar(a1, a2, gold)))
res["overlap_AB"] = {"both": len(both), "A_only": [i for i in gold if det["A"][i] and not det["B"][i]], "B_only": [i for i in gold if det["B"][i] and not det["A"][i]],
                     "neither": [i for i in gold if not det["A"][i] and not det["B"][i]]}
res["C_only_vs_B"] = [i for i in gold if det["C"][i] and not det["B"][i]]
res["verdicts_changed_B_vs_A"] = sum(det["A"][i] != det["B"][i] for i in S)
res["severity_changed_B_vs_A"] = sum(R["A"][i]["severity"] != R["B"][i]["severity"] for i in S)
res["gold_origin_counts"] = dict(collections.Counter(G[i]["origin"] for i in gold))
res["gold_type_counts"] = dict(collections.Counter(G[i]["type"] for i in gold))
res["random_clean_check"] = {"n": len(ADJ["random_clean"]), "gold_defects_found": [i for i in ADJ["random_clean"] if G[i]["gold_defect"]]}
res["redux_ok_overturned"] = [i for i in gold if (L[i].get("redux") or {}).get("label") == "ok"]
res["redux_flagged_in_sample"] = {i: L[i]["redux"]["label"] for i in S if L[i].get("redux") and L[i]["redux"]["label"] != "ok"}
res["redux_flagged_found"] = {a: [i for i in res["redux_flagged_in_sample"] if det[a][i]] for a in R}
res["adjudicator_ambiguous_items"] = [i for i in ADJ["order"] if G[i].get("any_ambiguous")]
res["tiebreaks"] = [i for i in ADJ["order"] if G[i]["basis"] == "Adj-3 tiebreak"]
X = [i for i in ADJ["order"]]
res["kappa_adj_defect"] = kappa([A1[i]["severity"] in DEF for i in X], [A2[i]["severity"] in DEF for i in X])
res["kappa_adj_type"] = kappa([A1[i]["defect_type"] for i in X], [A2[i]["defect_type"] for i in X])
dd = [i for i in X if A1[i]["severity"] in DEF and A2[i]["severity"] in DEF]
res["kappa_adj_origin_on_agreed_defects"] = {"n": len(dd), "kappa": kappa([up(A1[i]["origin"]) for i in dd], [up(A2[i]["origin"]) for i in dd]) if len(dd) > 1 else None,
                                             "raw_agreement": sum(up(A1[i]["origin"]) == up(A2[i]["origin"]) for i in dd) / len(dd) if dd else None}
res["kappa_arms_defect"] = {f"{x}{y}": kappa([det[x][i] for i in S], [det[y][i] for i in S]) for x, y in (("A", "B"), ("A", "C"), ("B", "C"))}
res["lineage_decisive_B"] = [i for i in S if str(R["B"][i].get("lineage_decisive")).lower() == "true"]

# ---- propagation (descendants requiring re-review per upstream gold defect)
par_children = collections.defaultdict(list)
for q, r in L.items():
    if r["parent"]: par_children[r["parent"]["id"]].append(q)
PUB = {"MMMLU (OpenAI, 14 languages)": 14, "Global-MMLU (non-English, 41 languages)": 41}
PROX = 29  # MMLU-ProX full: 29 languages x 11,829 items (dedup of MMLU-Pro; per-item membership not verified here)
prop = []
for i in gold:
    r = L[i]; o = up(G[i]["origin"])
    row = {"item_id": i, "origin": G[i]["origin"], "parent": r["parent"]["id"] if r["parent"] else ""}
    if o == "UP" and r["parent"]:
        sib = [q for q in par_children[r["parent"]["id"]] if q != i]
        row.update({"in_data_mmlu_pro_items_same_parent": 1 + len(sib), "redux_copy": int(bool(r.get("redux"))),
                    "documented_translations_of_parent": sum(PUB.values()), "mmlu_prox_copies_of_pro_items": PROX * (1 + len(sib))})
    else:
        row.update({"in_data_mmlu_pro_items_same_parent": 0, "redux_copy": 0, "documented_translations_of_parent": 0, "mmlu_prox_copies_of_pro_items": PROX})
    row["in_data_total"] = row["in_data_mmlu_pro_items_same_parent"] + row["redux_copy"]
    row["documented_total"] = row["in_data_total"] + row["documented_translations_of_parent"] + row["mmlu_prox_copies_of_pro_items"]
    prop.append(row)
res["propagation"] = prop
upg = [p for p in prop if up(p["origin"]) == "UP"]
res["propagation_summary"] = {"upstream_gold_defects": len(upg),
    "in_data_descendants_per_upstream_defect": sum(p["in_data_total"] for p in upg) / len(upg) if upg else 0,
    "documented_descendants_per_upstream_defect": sum(p["documented_total"] for p in upg) / len(upg) if upg else 0,
    "documented_descendants_per_any_gold_defect": sum(p["documented_total"] for p in prop) / len(prop) if prop else 0}
json.dump(res, open(os.path.join(T, "results.json"), "w"), indent=1, default=str)

# ---- adjudication.csv
with open(os.path.join(E, "adjudication.csv"), "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["item_id", "in_set_because", "adj1_severity", "adj1_type", "adj1_origin", "adj1_key", "adj1_rationale", "adj1_evidence",
                "adj2_severity", "adj2_type", "adj2_origin", "adj2_key", "adj2_rationale", "adj2_evidence", "adj3_severity", "adj3_origin", "adj3_rationale",
                "gold_defect", "gold_strict", "gold_type", "gold_origin", "gold_basis", "A_flag", "B_flag", "C_flag", "provisional"])
    for i in S:
        if i not in ADJ["order"]: continue
        a, b, c = A1[i], A2[i], A3.get(i, {})
        w.writerow([i, "flagged" if i in ADJ["flagged"] else "random clean check", a["severity"], a["defect_type"], a["origin"], a.get("correct_key"), a["rationale"], a["evidence"],
                    b["severity"], b["defect_type"], b["origin"], b.get("correct_key"), b["rationale"], b["evidence"], c.get("severity", ""), c.get("origin", ""), c.get("rationale", ""),
                    G[i]["gold_defect"], G[i]["strict"], G[i]["type"], G[i]["origin"], G[i]["basis"], R["A"][i]["severity"], R["B"][i]["severity"], R["C"][i]["severity"], "yes"])
print(json.dumps({k: v for k, v in res.items() if k not in ("propagation",)}, indent=1, default=str))

# ---- robustness (added post hoc, see results_summary.md "Deviations"): gold from two lineage-BLIND adjudicators
B1, B2 = loadj(f"{J}/BLIND_r1.json"), loadj(f"{J}/BLIND_r2.json")
if B1 and B2:
    rob = {}
    for name, rule in (("blind_both", lambda i: B1[i]["severity"] in DEF and B2[i]["severity"] in DEF),
                       ("blind_either", lambda i: B1[i]["severity"] in DEF or B2[i]["severity"] in DEF)):
        pos = [i for i in S if i in B1 and rule(i)]
        rob[name] = {"n": len(pos), "items": pos, **{f"recall_{a}": recall(a, pos) for a in R},
                     **{f"recall_incl_amb_{a}": recall(a, pos, det_amb) for a in R},
                     "overlap_with_primary_gold": len(set(pos) & set(gold))}
        for a1, a2 in (("B", "A"), ("B", "C")): rob[name][f"delta_{a1}{a2}_pp"] = 100 * (recall(a1, pos) - recall(a2, pos))
    rob["kappa_blind_pair_defect"] = kappa([B1[i]["severity"] in DEF for i in X], [B2[i]["severity"] in DEF for i in X])
    rob["kappa_blind_vs_primary_gold"] = kappa([B1[i]["severity"] in DEF and B2[i]["severity"] in DEF for i in X], [G[i]["gold_defect"] for i in X])
    res["robustness_blind_gold"] = rob
    json.dump(res, open(os.path.join(T, "results.json"), "w"), indent=1, default=str)
    print(json.dumps(rob, indent=1, default=str))
