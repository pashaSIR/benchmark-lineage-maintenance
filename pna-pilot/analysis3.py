"""Transformation-node test (option augmentation x negated stems) and ranking-uncertainty test, using MMLU-Pro model outputs."""
import collections, csv, math, random
from load import *
from link import opts, LET, PRO_C
A = load_all_pro()
L = {r["pro_qid"]: r for r in csv.DictReader(open("lineage_all.csv"))}
M = {f'{x["subject"]}#{x["row"]}': x for x in load_mmlu()}
STRONG = ["claude-3-5-sonnet-20241022_5shots", "gpt-4o-2024-08-06_5shots", "gemini-1.5-pro-002_5shots"]
P = {m: {str(x["question_id"]): x for x in A[m]} for m in STRONG}
NEG = re.compile(r"\b(not|except|least|false|cannot|incorrect|untrue|never)\b|\bNOT\b", re.I)
stats = collections.defaultdict(lambda: collections.Counter()); cand = []
for qid, r in L.items():
    if not r["mmlu_parent"]: continue
    p = P[STRONG[0]][qid]; o = opts(p); mn = {norm(c) for c in M[r["mmlu_parent"]]["choices"]}
    new = {LET[i] for i, x in enumerate(o) if norm(x) not in mn}
    if not new: continue
    neg = bool(NEG.search(p["question"].split("\n")[-1] if "\n" in p["question"] else p["question"]))
    preds = [P[m].get(qid, {}).get("pred") for m in STRONG]
    s = stats["negated" if neg else "plain"]; s["items"] += 1
    if all(x == preds[0] for x in preds) and preds[0] and preds[0] != p["answer"]:
        s["consensus_wrong"] += 1
        if preds[0] in new: s["consensus_on_NEW_option"] += 1; cand.append({"pro_qid": qid, "negated": neg, "key": p["answer"], "consensus": preds[0], "redux": r.get("redux_label", "")})
for k, s in stats.items():
    print(f"[T2] {k}: items={s['items']}, 3-model consensus against key={s['consensus_wrong']} ({s['consensus_wrong']/s['items']:.1%}), of which on a NEW (GPT-4-added) option={s['consensus_on_NEW_option']} ({s['consensus_on_NEW_option']/s['items']:.1%})")
with open("tables/t2_consensus_new_option.csv", "w", newline="") as f:
    w = csv.DictWriter(f, list(cand[0].keys())); w.writeheader(); w.writerows(cand)

# ranking uncertainty: iid vs cluster-robust SE for paired accuracy differences on MMLU-Pro (all 12,032 items, V_c snapshot models)
ALL = ["claude-3-5-sonnet-20241022_5shots", "gpt-4o-2024-08-06_5shots", "gemini-1.5-pro-002_5shots", "deepseek-chat-v2_5_5shots", "jamba-1.5-large_5shots", "claude-3-5-haiku-20241022_5shots", "gemini-1.5-flash-002_5shots"]
R = {m: {str(x["question_id"]): x for x in A[m]} for m in ALL}
ids = sorted(set.intersection(*[set(v) for v in R.values()]), key=int)
acc = {m: [int(R[m][q]["pred"] == R[m][q]["answer"]) for q in ids] for m in ALL}
src = [R[ALL[0]][q]["src"] for q in ids]
def se_iid(d): n=len(d); mu=sum(d)/n; return math.sqrt(sum((x-mu)**2 for x in d)/(n-1)/n)
def se_cl(d, cl):
    n=len(d); mu=sum(d)/n; g=collections.defaultdict(float)
    for x,c in zip(d,cl): g[c]+=x-mu
    G=len(g); return math.sqrt(G/(G-1)*sum(v*v for v in g.values()))/n
rows=[]
for i in range(len(ALL)):
    for j in range(i+1,len(ALL)):
        d=[a-b for a,b in zip(acc[ALL[i]],acc[ALL[j]])]; mu=sum(d)/len(d)
        s0, s1 = se_iid(d), se_cl(d, src)
        rows.append({"a":ALL[i],"b":ALL[j],"diff_pts":round(100*mu,2),"se_iid":round(100*s0,3),"se_cluster_src":round(100*s1,3),"ratio":round(s1/s0,2),"z_iid":round(mu/s0,2),"z_cluster":round(mu/s1,2)})
rows.sort(key=lambda r: abs(r["diff_pts"]))
for r in rows[:8]: print("[RANK]", r)
print(f"[RANK] items={len(ids)}, clusters(src)={len(set(src))}; pairs where |z| crosses 1.96 when clustering: {sum((abs(r['z_iid'])>=1.96) != (abs(r['z_cluster'])>=1.96) for r in rows)} of {len(rows)}")
with open("tables/rank_se.csv","w",newline="") as f:
    w=csv.DictWriter(f,list(rows[0].keys())); w.writeheader(); w.writerows(rows)
