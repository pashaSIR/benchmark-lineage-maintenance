"""Within-subject test: does source-node-guided inspection beat random item inspection at equal budget?
Oracle = MMLU-Redux labels (defect = not ok/expert). 2,000 simulated audits per subject per strategy. Seed 20261008."""
import collections, csv, random, statistics as st
from load import *
from link import et, src_class
rng = random.Random(20261008)
RX = load_redux()
by = collections.defaultdict(list)
for x in RX:
    x["defect"] = et(x) not in ("ok", "expert")
    x["node"] = re.sub(r"\s+", " ", x["source"].strip().lower()) if src_class(x["source"]) == "recovered" else None
    by[x["subject"]].append(x)

def run(items, B, strat):
    idx = list(range(len(items))); rng.shuffle(idx)
    nodes = collections.defaultdict(list)
    for i in idx:
        if items[i]["node"]: nodes[items[i]["node"]].append(i)
    seen, found, q = set(), 0, []
    if strat == "node_screen":  # probe one item from each source node (random order), then unsourced/random
        order = [v[0] for v in sorted(nodes.values(), key=lambda v: rng.random())] + idx
    else:
        order = idx
    it = iter(order)
    while len(seen) < B:
        i = q.pop() if q else next(it)
        if i in seen: continue
        seen.add(i)
        if items[i]["defect"]:
            found += 1
            if strat != "random" and items[i]["node"]:
                q += [j for j in nodes[items[i]["node"]] if j not in seen]
    return found

rows = []
for s, items in sorted(by.items()):
    n_def = sum(x["defect"] for x in items)
    multi = [v for v in collections.Counter(x["node"] for x in items if x["node"]).values() if v >= 5]
    r = {"subject": s, "items": len(items), "defects": n_def, "sourced": sum(1 for x in items if x["node"]), "nodes_5plus": len(multi)}
    for B in (20, 40):
        for strat in ("random", "adaptive_sibling", "node_screen"):
            r[f"{strat}_B{B}"] = round(st.mean(run(items, B, strat) for _ in range(2000)), 2)
        r[f"lift_adaptive_B{B}"] = round(r[f"adaptive_sibling_B{B}"] / r[f"random_B{B}"], 2) if r[f"random_B{B}"] else ""
        r[f"lift_screen_B{B}"] = round(r[f"node_screen_B{B}"] / r[f"random_B{B}"], 2) if r[f"random_B{B}"] else ""
    rows.append(r)
with open("tables/within_subject_sampling.csv", "w", newline="") as f:
    w = csv.DictWriter(f, list(rows[0].keys())); w.writeheader(); w.writerows(rows)
el = [r for r in rows if r["defects"] >= 5 and r["nodes_5plus"] >= 2]
print("eligible subjects (>=5 defects, >=2 source nodes of 5+ items):", len(el))
for r in sorted(el, key=lambda r: -r["defects"]):
    print(f"{r['subject'][:28]:28s} def={r['defects']:2d} sourced={r['sourced']:3d} nodes5+={r['nodes_5plus']:2d} | B20 rand {r['random_B20']:5.2f} adapt {r['adaptive_sibling_B20']:5.2f} ({r['lift_adaptive_B20']}) screen {r['node_screen_B20']:5.2f} ({r['lift_screen_B20']}) | B40 rand {r['random_B40']:5.2f} adapt {r['adaptive_sibling_B40']:5.2f} ({r['lift_adaptive_B40']})")
tot = lambda k, R: sum(r[k] for r in R)
for B in (20, 40):
    print(f"ALL 57 subjects B{B}: random {tot(f'random_B{B}',rows):.1f}, adaptive {tot(f'adaptive_sibling_B{B}',rows):.1f}, screen {tot(f'node_screen_B{B}',rows):.1f}; eligible only: random {tot(f'random_B{B}',el):.1f}, adaptive {tot(f'adaptive_sibling_B{B}',el):.1f}, screen {tot(f'node_screen_B{B}',el):.1f}")
