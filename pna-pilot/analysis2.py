"""Fairness checks on analysis.py: does source add anything beyond subject? Seed fixed."""
import collections, random, statistics as st
from analysis import RX, N, icc, nodes, stat, W
rng = random.Random(7)
subj = collections.defaultdict(list)
for x in RX: subj[x["subject"]].append(x["defect"])
ic_s, _ = icc(list(subj.values())); m = sum(len(v)**2 for v in subj.values())/N
print(f"[B] ICC within subject = {ic_s:.3f}, cluster size {m:.0f}, DEFF = {1+(m-1)*ic_s:.2f}")
# ICC of source node after removing subject means (residual clustering)
res = collections.defaultdict(list)
sm = {s: sum(v)/len(v) for s, v in subj.items()}
for x in RX:
    if x["sclass"] == "recovered": res[(x["subject"], x["node"])].append(x["defect"] - sm[x["subject"]])
ic_r, _ = icc(list(res.values()))
mb = sum(len(v)**2 for v in res.values())/sum(len(v) for v in res.values())
print(f"[B] ICC of subject-centred defect within source node = {ic_r:.3f}; mean cluster {mb:.1f}; residual DEFF = {1+(mb-1)*ic_r:.2f}")
# simulation with a subject-adaptive comparator
idx_node = collections.defaultdict(list); idx_subj = collections.defaultdict(list)
for i, x in enumerate(RX):
    idx_subj[x["subject"]].append(i)
    if x["sclass"] == "recovered": idx_node[(x["subject"], x["node"])].append(i)
def sim(strategy, B, k=10):
    seen=set(); found=0; q=[]; order=list(range(N)); rng.shuffle(order); it=iter(order)
    while len(seen) < B:
        if q: i=q.pop()
        else:
            i=next(it)
            while i in seen: i=next(it)
        if i in seen: continue
        seen.add(i); x=RX[i]
        if x["defect"]:
            found+=1
            if strategy=="source" and x["sclass"]=="recovered": pool=idx_node[(x["subject"],x["node"])]
            elif strategy=="subject": pool=idx_subj[x["subject"]]
            else: pool=[]
            s=[j for j in pool if j not in seen]; rng.shuffle(s); q+=s[:k]
    return found
rows=[]
for B in (50,100,200):
    r={s: st.mean(sim(s,B) for _ in range(1000)) for s in ("item","subject","source")}
    rows.append({"budget":B, **{k: round(v,2) for k,v in r.items()}, "source_vs_subject": round(r["source"]/r["subject"],2)})
    print("[SIM2]", rows[-1])
W("sim_budget_vs_subject", rows)
# F1 restricted to nodes with >=5 items
from analysis import rec
keep = {k for k, v in nodes.items() if len(v) >= 5}
rec5 = [x for x in rec if (x["subject"], x["node"]) in keep]
lab = [x["defect"] for x in rec5]; T0 = stat(rec5, lab)
by = collections.defaultdict(list)
for i, x in enumerate(rec5): by[x["subject"]].append(i)
ge=0
for _ in range(2000):
    l2=lab[:]
    for s, idx in by.items():
        v=[lab[i] for i in idx]; rng.shuffle(v)
        for i,val in zip(idx,v): l2[i]=val
    ge += stat(rec5,l2) >= T0
print(f"[F1] nodes>=5 items: {len(keep)} nodes, {len(rec5)} items, {sum(lab)} defects; within-subject permutation p = {(ge+1)/2001:.4f}")
