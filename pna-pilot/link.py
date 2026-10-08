"""Build the MMLU -> MMLU-Redux -> MMLU-Pro lineage table for every MMLU-derived MMLU-Pro item.
Writes lineage_all.csv. Pro version used: the late-2024 snapshot embedded in claude-3-5-sonnet-20241022 outputs (V_c);
earlier snapshots V_a (Llama-2-7b outputs) and V_b (Llama-3.1-70B-Instruct outputs) are diffed for key changes."""
import ast, csv, collections, difflib
from load import *

PRO_C, PRO_B, PRO_A = "claude-3-5-sonnet-20241022_5shots", "Meta-Llama-3_1-70B-Instruct_5shots", "Llama-2-7b-hf_5shots"
LET = "ABCDEFGHIJ"

def et(x):
    e = re.sub(r"[\s_]+", " ", x["error_type"].lower()).strip()
    return e

def opts(x):
    o = x["options"]
    return o if isinstance(o, list) else ast.literal_eval(o)

def same(a, b):
    a, b = norm(str(a)), norm(str(b))
    return a == b or (len(a) > 3 and difflib.SequenceMatcher(None, a, b).ratio() >= 0.92)

def redux_correct_text(r, choices):
    c = r.get("correct_answer", "").strip()
    if c == "": return ""
    if re.fullmatch(r"[0-3]", c): return choices[int(c)]
    if re.fullmatch(r"[A-D]", c): return choices["ABCD".index(c)]
    return c

def src_class(s):
    s = s.strip()
    if s in ("", "-", "Unknown", "unknown", "N/A", "n/a"): return "none"
    if s.lower() == "expert": return "expert"
    return "recovered"

def build():
    A = load_all_pro()
    mm = load_mmlu(); rx = load_redux()
    mi = collections.defaultdict(list)
    for x in mm: mi[norm(x["question"])].append(x)
    ri = {}
    for x in rx:
        ch = ast.literal_eval(x["choices"]) if x["choices"].startswith("[") else []
        x["_choices"] = ch
        ri[(norm(x["question"]), tuple(sorted(norm(c) for c in ch)))] = x
    rq = collections.defaultdict(list)
    for x in rx: rq[norm(x["question"])].append(x)
    vers = {v: {str(x["question_id"]): x for x in A[v]} for v in (PRO_A, PRO_B, PRO_C)}
    rows = []
    for qid, p in vers[PRO_C].items():
        if not p["src"].startswith("ori_mmlu"): continue
        po = opts(p); pn = [norm(o) for o in po]
        cands = mi.get(norm(p["question"]), [])
        par = max(cands, key=lambda m: sum(norm(c) in pn for c in m["choices"]), default=None)
        row = {"pro_qid": qid, "pro_src": p["src"], "pro_category": p["category"], "pro_n_options": len(po),
               "pro_key_letter": p["answer"], "pro_key_text": po[LET.index(p["answer"])]}
        if par is None:
            row["mmlu_parent"] = ""; rows.append(row); continue
        mk = par["choices"][par["answer"]]
        row.update({"mmlu_parent": f'{par["subject"]}#{par["row"]}', "mmlu_key_text": mk,
                    "mmlu_choices_retained": sum(norm(c) in pn for c in par["choices"]),
                    "question_changed": norm(par["question"]) != norm(p["question"]),
                    "key_same_as_mmlu": same(mk, row["pro_key_text"])})
        for tag, v in (("A", PRO_A), ("B", PRO_B)):
            o = vers[v].get(qid)
            row[f"key_v{tag}"] = "" if o is None else opts(o)[LET.index(o["answer"])] if o["answer"] in LET else ""
        row["key_changed_across_versions"] = any(row[f"key_v{t}"] and not same(row[f"key_v{t}"], row["pro_key_text"]) for t in "AB")
        r = ri.get((norm(par["question"]), tuple(sorted(norm(c) for c in par["choices"]))))
        if r is None:
            c2 = [x for x in rq.get(norm(par["question"]), []) if x["subject"] == par["subject"]]
            r = c2[0] if len(c2) == 1 else None
        row["in_redux"] = r is not None
        if r:
            ct = redux_correct_text(r, par["choices"])
            row.update({"redux_label": et(r), "redux_source": r["source"], "redux_source_class": src_class(r["source"]),
                        "redux_correct": ct, "redux_reason": r.get("potential_reason", "")})
            lab = row["redux_label"]
            if lab in ("wrong groundtruth", "no correct answer"):
                if row["key_same_as_mmlu"]: row["outcome"] = "survived"
                elif ct and same(ct, row["pro_key_text"]): row["outcome"] = "fixed"
                else: row["outcome"] = "mutated"
            elif lab == "multiple correct answers":
                row["outcome"] = "survived?" if row["mmlu_choices_retained"] == 4 else "options changed"
            elif lab in ("bad question clarity", "bad options clarity"):
                row["outcome"] = "survived?" if not row["question_changed"] else "question edited"
            else:
                row["outcome"] = "ok_parent" if lab == "ok" else lab
            if lab == "ok" and not row["key_same_as_mmlu"]: row["outcome"] = "key changed on OK parent"
        rows.append(row)
    return rows

if __name__ == "__main__":
    rows = build()
    keys = []
    for r in rows:
        for k in r:
            if k not in keys: keys.append(k)
    with open("lineage_all.csv", "w", newline="") as f:
        w = csv.DictWriter(f, keys); w.writeheader(); w.writerows(rows)
    print(len(rows), "rows; parent found", sum(1 for r in rows if r["mmlu_parent"]), "; in redux", sum(1 for r in rows if r.get("in_redux")))
    print(collections.Counter(r.get("outcome", "not in redux") for r in rows).most_common())
