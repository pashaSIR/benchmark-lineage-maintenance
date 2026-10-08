"""Build the full MMLU -> MMLU-Redux -> MMLU-Pro lineage for every MMLU-derived item in the newest accessible MMLU-Pro snapshot.
Current revision used (V_d): records embedded in TIGER-AI-Lab/MMLU-Pro @ f418b116 eval_results/model_outputs_gemini-3.1-pro_5-shots.zip
(added 2026-02-20; Hugging Face is blocked from this sandbox). Previous revision (V_c): claude-3-5-sonnet-20241022 outputs (late 2024), as in the pilot.
Writes ../data/lineage_full.jsonl (one record per item, full text)."""
import ast, collections, json, os, sys, zipfile
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "pna-pilot"))
from load import DL, load_mmlu, load_redux, norm
from link import et, same, redux_correct_text, src_class, LET

def opts(o): return o if isinstance(o, list) else ast.literal_eval(o)

def load_vd():
    z = zipfile.ZipFile(f"{DL}/MMLU-Pro/eval_results/model_outputs_gemini-3.1-pro_5-shots.zip")
    D = {}
    for n in z.namelist():
        if n.endswith("_result.json") and "MACOSX" not in n:
            for x in json.loads(z.read(n)): D[str(x["question_id"])] = x
    return D

def load_vc():
    z = zipfile.ZipFile(f"{DL}/MMLU-Pro/eval_results/model_outputs_claude-3-5-sonnet-20241022_5shots.json.zip")
    return {str(x["question_id"]): x for x in json.loads(z.read(z.namelist()[0]))}

def build():
    D, C = load_vd(), load_vc()
    mm, rx = load_mmlu(), load_redux()
    mi = collections.defaultdict(list)
    for x in mm: mi[norm(x["question"])].append(x)
    ri, rq = {}, collections.defaultdict(list)
    for x in rx:
        ch = ast.literal_eval(x["choices"]) if x["choices"].startswith("[") else []
        ri[(norm(x["question"]), tuple(sorted(norm(c) for c in ch)))] = x
        rq[norm(x["question"])].append(x)
    out = []
    for qid in sorted(D, key=int):
        p = D[qid]
        if not p["src"].startswith("ori_mmlu"): continue
        po = opts(p["options"]); pn = [norm(o) for o in po]
        rec = {"pro_qid": qid, "src": p["src"], "category": p["category"], "question": p["question"], "options": po,
               "key": p["answer"], "key_text": po[LET.index(p["answer"])]}
        c = C.get(qid)
        rec["prev_version"] = None if c is None else {"question": c["question"], "options": opts(c["options"]), "key": c["answer"]}
        # parent: exact-normalized stem match first, else best fuzzy match within subject on stem
        cands = mi.get(norm(p["question"]), [])
        if not cands:
            subj = p["src"].replace("ori_mmlu-", "")
            import difflib
            pool = [m for m in mm if m["subject"] == subj]
            sc = [(difflib.SequenceMatcher(None, norm(m["question"]), norm(p["question"])).ratio() + 0.1 * sum(norm(o) in pn for o in m["choices"]), m) for m in pool]
            sc = [s for s in sc if s[0] >= 0.85]
            cands = [max(sc, key=lambda s: s[0])[1]] if sc else []
        par = max(cands, key=lambda m: sum(norm(o) in pn for o in m["choices"]), default=None)
        rec["parent"] = None
        if par:
            r = ri.get((norm(par["question"]), tuple(sorted(norm(o) for o in par["choices"]))))
            if r is None:
                c2 = [x for x in rq.get(norm(par["question"]), []) if x["subject"] == par["subject"]]
                r = c2[0] if len(c2) == 1 else None
            rec["parent"] = {"id": f'{par["subject"]}#{par["row"]}', "question": par["question"], "choices": par["choices"],
                             "key": "ABCD"[par["answer"]], "key_text": par["choices"][par["answer"]]}
            rec["redux"] = None if r is None else {"label": et(r), "source": r["source"], "source_class": src_class(r["source"]),
                             "correct": redux_correct_text(r, par["choices"]), "reason": r.get("potential_reason", "")}
        out.append(rec)
    return out

if __name__ == "__main__":
    rows = build()
    os.makedirs(os.path.join(os.path.dirname(__file__), "..", "data"), exist_ok=True)
    with open(os.path.join(os.path.dirname(__file__), "..", "data", "lineage_full.jsonl"), "w") as f:
        for r in rows: f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(len(rows), "MMLU-derived items in V_d; parent found", sum(r["parent"] is not None for r in rows),
          "; in Redux", sum(bool(r.get("redux")) for r in rows), "; present in V_c", sum(r["prev_version"] is not None for r in rows))
