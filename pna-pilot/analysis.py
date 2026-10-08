"""Population-level tests behind the micro-pilot. Prints results; writes tables/*.csv. Seed fixed."""
import ast, collections, csv, math, os, random, statistics as st
from load import *
from link import opts, LET, PRO_C, et, src_class
rng = random.Random(20261007)
os.makedirs("tables", exist_ok=True)
def W(name, rows):
    with open(f"tables/{name}.csv", "w", newline="") as f:
        w = csv.DictWriter(f, list(rows[0].keys())); w.writeheader(); w.writerows(rows)

RX = load_redux()
for x in RX:
    x["lab"] = et(x); x["defect"] = x["lab"] not in ("ok", "expert")
    x["node"] = re.sub(r"\s+", " ", x["source"].strip().lower())
    x["sclass"] = src_class(x["source"])
N = len(RX); D = sum(x["defect"] for x in RX)
print(f"[F1] Redux snapshot: {N} items, {D} defects (excl. 'expert'), {sum(x['lab']=='expert' for x in RX)} 'expert' labels")
print("[F1] source recoverability:", collections.Counter(x["sclass"] for x in RX))

# ---- F1: clustering by source node beyond subject (within-subject permutation test) ----
rec = [x for x in RX if x["sclass"] == "recovered"]
def stat(items, lab):
    T = 0.0
    bys = collections.defaultdict(list)
    for x, l in zip(items, lab): bys[x["subject"]].append((x["node"], l))
    for s, v in bys.items():
        p = sum(l for _, l in v) / len(v)
        if p in (0, 1): continue
        byn = collections.defaultdict(list)
        for n, l in v: byn[n].append(l)
        for n, ls in byn.items():
            e = len(ls) * p; T += (sum(ls) - e) ** 2 / e
    return T
lab = [x["defect"] for x in rec]
T0 = stat(rec, lab)
bysub = collections.defaultdict(list)
for i, x in enumerate(rec): bysub[x["subject"]].append(i)
ge = 0; R = 2000
for _ in range(R):
    l2 = lab[:]
    for s, idx in bysub.items():
        v = [lab[i] for i in idx]; rng.shuffle(v)
        for i, val in zip(idx, v): l2[i] = val
    ge += stat(rec, l2) >= T0
print(f"[F1] recovered-source items {len(rec)}, defects {sum(lab)}; within-subject permutation p = {(ge+1)/(R+1):.4f} (T0={T0:.1f}, R={R})")

nodes = collections.defaultdict(list)
for x in rec: nodes[(x["subject"], x["node"])].append(x["defect"])
big = sorted(((sum(v), len(v), k) for k, v in nodes.items()), reverse=True)
tot_def = sum(lab)
cum = 0; rows = []
for i, (d, n, k) in enumerate(big):
    cum += d
    rows.append({"rank": i + 1, "subject": k[0], "source_node": k[1][:120], "items": n, "defects": d, "rate": round(d / n, 3), "cum_share_of_defects": round(cum / tot_def, 3)})
W("f1_source_nodes", rows)
nn = len(big); k5 = max(1, round(0.05 * nn))
print(f"[F1] {nn} (subject,source) nodes; top 5% ({k5}) hold {sum(d for d,_,_ in big[:k5])}/{tot_def} defects; nodes with any defect: {sum(1 for d,_,_ in big if d)}")
hot = [(k, d, n) for d, n, k in big if n >= 10 and d / n >= 0.3]
print("[F1] hot nodes (n>=10, rate>=30%):", [(k[0], k[1][:50], f"{d}/{n}") for k, d, n in hot])
# subject averages of hot-node subjects
for k, d, n in hot:
    s = [x["defect"] for x in RX if x["subject"] == k[0]]
    print(f"      subject {k[0]}: subject-wide rate {sum(s)}/{len(s)}; this node {d}/{n}")

# ICC / design effect by source node (one-way ANOVA estimator), recovered items
g = [v for v in nodes.values()]
def icc(groups):
    k = len(groups); Nn = sum(len(v) for v in groups); mean = sum(sum(v) for v in groups) / Nn
    ssb = sum(len(v) * (sum(v) / len(v) - mean) ** 2 for v in groups); ssw = sum(sum((y - sum(v) / len(v)) ** 2 for y in v) for v in groups)
    msb = ssb / (k - 1); msw = ssw / (Nn - k); n0 = (Nn - sum(len(v) ** 2 for v in groups) / Nn) / (k - 1)
    return (msb - msw) / (msb + (n0 - 1) * msw), n0
ic, n0 = icc(g); mbar = sum(len(v) ** 2 for v in g) / sum(len(v) for v in g)
print(f"[F1/B] ICC of defect within source node = {ic:.3f}; size-weighted mean cluster size = {mbar:.1f}; DEFF = {1+(mbar-1)*ic:.2f}")

# ---- Inspection-budget simulation (Redux labels as oracle) ----
idx_node = collections.defaultdict(list)
for i, x in enumerate(RX):
    if x["sclass"] == "recovered": idx_node[(x["subject"], x["node"])].append(i)
def sim(strategy, B, k_sib=10):
    seen = set(); found = 0; queue = []
    order = list(range(N)); rng.shuffle(order); it = iter(order)
    while len(seen) < B:
        if strategy == "provenance" and queue: i = queue.pop()
        else:
            i = next(it)
            while i in seen: i = next(it)
        if i in seen: continue
        seen.add(i); x = RX[i]
        if x["defect"]:
            found += 1
            if strategy == "provenance" and x["sclass"] == "recovered":
                sib = [j for j in idx_node[(x["subject"], x["node"])] if j not in seen]; rng.shuffle(sib); queue += sib[:k_sib]
    return found
simrows = []
for B in (50, 100, 200, 400):
    a = [sim("item", B) for _ in range(1000)]; b = [sim("provenance", B) for _ in range(1000)]
    simrows.append({"budget": B, "item_only_mean": round(st.mean(a), 2), "provenance_mean": round(st.mean(b), 2), "lift": round(st.mean(b) / st.mean(a), 2),
                    "item_only_p_zero": round(sum(v == 0 for v in a) / 1000, 3), "prov_p_zero": round(sum(v == 0 for v in b) / 1000, 3)})
    print("[SIM]", simrows[-1])
W("sim_budget", simrows)

# ---- F2 / F4: inheritance into MMLU-Pro and selection ----
L = list(csv.DictReader(open("lineage_all.csv")))
in_pro = {(r["mmlu_parent"]) for r in L}
M = load_mmlu(); mi = collections.defaultdict(list)
for x in M: mi[norm(x["question"])].append(x)
sel = collections.Counter()
for x in RX:
    c = [m for m in mi.get(norm(x["question"]), []) if m["subject"] == x["subject"]]
    if not c: continue
    kept = any(f'{m["subject"]}#{m["row"]}' in in_pro for m in c)
    sel[(kept, x["defect"])] += 1
    sel[(kept, "wrongkey" if x["lab"] in ("wrong groundtruth", "no correct answer") else "other")] += 1
for kept in (True, False):
    n = sel[(kept, True)] + sel[(kept, False)]
    print(f"[F4] Redux parents {'kept in' if kept else 'dropped from'} MMLU-Pro: n={n}, any-defect rate={sel[(kept,True)]/n:.3%}, wrong/no-correct-key rate={sel[(kept,'wrongkey')]/n:.3%}")
a, b = sel[(True, True)], sel[(True, False)]; c_, d_ = sel[(False, True)], sel[(False, False)]
orr = (a * d_) / (b * c_); se = math.sqrt(1/a + 1/b + 1/c_ + 1/d_)
print(f"[F4] odds ratio kept-vs-dropped (any defect) = {orr:.2f} [95% CI {math.exp(math.log(orr)-1.96*se):.2f}, {math.exp(math.log(orr)+1.96*se):.2f}]")
oc = collections.Counter((r["redux_label"], r["outcome"]) for r in L if r.get("redux_label") in ("wrong groundtruth", "no correct answer"))
print("[F2] flagged-key parents present in Pro, by outcome:", dict(oc))
kc = [r for r in L if r["key_changed_across_versions"] == "True"]
print(f"[F2] MMLU-derived Pro items whose key changed across Pro snapshots: {len(kc)}; of those Redux-audited: {sum(r['in_redux']=='True' for r in kc)}, Redux-flagged: {sum(r.get('redux_label') not in ('ok','expert','') for r in kc if r['in_redux']=='True')}")
W("pro_key_changes", [{k: r[k] for k in ("pro_qid","mmlu_parent","key_vA","key_vB","pro_key_text","mmlu_key_text","redux_label")} for r in kc] or [{"none": ""}])

# dropped-option transformation
dr = [r for r in L if r["mmlu_choices_retained"] and int(r["mmlu_choices_retained"]) < 4]
dra = [r for r in dr if r["in_redux"] == "True"]
print(f"[T] Pro items that dropped >=1 MMLU option: {len(dr)}/{len(L)}; Redux-audited {len(dra)}, Redux-defect rate {sum(r['redux_label'] not in ('ok','expert') for r in dra)/max(1,len(dra)):.1%} vs all audited Pro parents {sum(r.get('redux_label') not in ('ok','expert') for r in L if r['in_redux']=='True')/sum(r['in_redux']=='True' for r in L):.1%}")
