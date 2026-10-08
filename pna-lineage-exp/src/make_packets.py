"""Render per-condition review packets (randomized order, fixed seeds) for the 100 sampled items."""
import csv, difflib, json, os, random, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "pna-pilot"))
from load import norm
from link import same
H = os.path.dirname(os.path.abspath(__file__)); D = os.path.join(H, "..", "data")
LET = "ABCDEFGHIJ"; ORDER_SEED = {"A": 101, "B": 102, "C": 103}; BATCHES = 4
L = {json.loads(l)["pro_qid"]: json.loads(l) for l in open(os.path.join(D, "lineage_full.jsonl"))}
S = [r["pro_qid"] for r in csv.DictReader(open(os.path.join(H, "..", "sample100.csv")))]

def item_block(r):
    s = [f"### Item {'PRO-'+r['pro_qid']}  (subject area: {r['category']})", "Question:", r["question"], "Options:"]
    s += [f"  {LET[i]}. {o}" for i, o in enumerate(r["options"])]
    s.append(f"Answer key: {r['key']}")
    return "\n".join(s)

def match(o, pool):
    for j, c in enumerate(pool):
        if norm(o) == norm(c) or same(o, c): return j
    return None

def lineage(r):
    p = r["parent"]; s = ["LINEAGE:"]
    if p is None: return "LINEAGE: no MMLU parent could be matched for this item."
    s.append(f"- MMLU parent: {p['id']} (MMLU test split, Hendrycks et al. 2021)")
    s.append("  Parent question: " + p["question"])
    for i, c in enumerate(p["choices"]): s.append(f"    {'ABCD'[i]}. {c}")
    s.append(f"  Parent key: {p['key']} ({p['key_text']})")
    if norm(p["question"]) == norm(r["question"]): s.append("- Stem: identical to parent (after whitespace/punctuation normalisation).")
    else:
        sm = difflib.SequenceMatcher(None, p["question"], r["question"])
        ed = [f"{t}: parent[{p['question'][i1:i2]!r}] -> pro[{r['question'][j1:j2]!r}]" for t, i1, i2, j1, j2 in sm.get_opcodes() if t != "equal"]
        s.append("- Stem EDITED relative to parent. Edits: " + " | ".join(ed[:12]))
    tags, kept = [], {}
    for i, o in enumerate(r["options"]):  # exact (normalised) matches first, one-to-one
        for j, c in enumerate(p["choices"]):
            if j not in kept.values() and norm(o) == norm(c): kept[i] = j; break
    for i, o in enumerate(r["options"]):
        if i in kept: tags.append(f"{LET[i]}=parent {'ABCD'[kept[i]]}"); continue
        best = max(range(4), key=lambda j: difflib.SequenceMatcher(None, norm(o), norm(p["choices"][j])).ratio())
        rt = difflib.SequenceMatcher(None, norm(o), norm(p["choices"][best])).ratio()
        tags.append(f"{LET[i]}=NEW" + (f" (closest parent option {'ABCD'[best]}, similarity {rt:.2f}: possibly an edited copy)" if rt >= 0.85 and best not in kept.values() else ""))
    s.append("- Option provenance (MMLU-Pro option -> origin; exact text match after normalising case/punctuation): " + ", ".join(tags))
    dropped = [f"{'ABCD'[j]} ({p['choices'][j]})" for j in range(4) if j not in kept.values()]
    s.append("- Parent options with no exact copy in MMLU-Pro (dropped or edited): " + (", ".join(dropped) if dropped else "none"))
    order = [kept[i] for i in sorted(kept)]
    s.append("- Retained parent options keep their relative order: " + ("yes" if order == sorted(order) else "NO (reordered)"))
    if norm(p["key_text"]) == norm(r["key_text"]): s.append("- MMLU-Pro key is the same text as the parent key.")
    else: s.append(f"- MMLU-Pro key text DIFFERS from the parent key text (parent key: {p['key_text']!r}; MMLU-Pro key: {r['key_text']!r}).")
    x = r.get("redux")
    if x is None: s.append("- MMLU-Redux: parent was NOT in the MMLU-Redux annotated subset (no human re-annotation available).")
    else:
        s.append(f"- MMLU-Redux annotation of the parent: label = {x['label']!r}" + (f"; proposed correct answer = {x['correct']!r}" if x["correct"] else "")
                 + (f"; annotator reason = {x['reason']!r}" if x["reason"] else "") + f"; upstream source recorded = {x['source'] or 'none'!r}")
    v = r["prev_version"]
    if v is None: s.append("- MMLU-Pro version history: item absent from the late-2024 snapshot.")
    else:
        ch = []
        if v["question"] != r["question"]: ch.append("stem changed")
        if v["options"] != r["options"]: ch.append("options changed (late-2024 options: " + "; ".join(f"{LET[i]}. {o}" for i, o in enumerate(v["options"])) + ")")
        if v["key"] != r["key"]: ch.append(f"key changed from {v['key']} ({v['options'][LET.index(v['key'])]!r}) in late 2024 to {r['key']} now")
        s.append("- MMLU-Pro version history (late-2024 snapshot vs Feb-2026 snapshot under review): " + ("; ".join(ch) if ch else "no change."))
    return "\n".join(s)

FAMILY = """BENCHMARK FAMILY (background for lineage-aware review):
MMLU (2021) is 4-option multiple choice; questions were copied by students from online exams/textbooks. MMLU-Redux (2024) re-annotated 5,700 MMLU test items (100 per subject) for errors: labels ok / wrong groundtruth / no correct answer / multiple correct answers / bad question clarity / bad options clarity, with an upstream-source field. MMLU-Pro (2024) took MMLU items, filtered some, had GPT-4 generate extra distractors to reach up to 10 options, sometimes dropped or edited original options, and ran an expert review; its maintainers have since issued errata (some keys/options changed between the late-2024 and Feb-2026 snapshots). Known failure modes in this family: wrong keys inherited from MMLU, GPT-4-added distractors that are themselves correct (especially in 'which is NOT/incorrect' stems), meaning changes from edits, truncated stems."""

def main():
    os.makedirs(os.path.join(D, "packets"), exist_ok=True)
    for cond, seed in ORDER_SEED.items():
        o = S[:]; random.Random(seed).shuffle(o)
        for b in range(BATCHES):
            ids = o[b::BATCHES]
            txt = []
            if cond == "B": txt.append(FAMILY)
            for q in ids:
                r = L[q]; txt.append(item_block(r) + ("\n" + lineage(r) if cond == "B" else ""))
            open(os.path.join(D, "packets", f"{cond}{b+1}.txt"), "w").write("\n\n".join(txt) + "\n")
            json.dump(["PRO-" + q for q in ids], open(os.path.join(D, "packets", f"{cond}{b+1}.ids.json"), "w"))
    print("ok")
main()
