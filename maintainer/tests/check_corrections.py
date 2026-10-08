#!/usr/bin/env python3
"""Regression checks for the submitted MMLU-Pro corrections.

Each check states the corrected condition. FAIL means the defect is still present in the records you pass in.
PASS means it is fixed, or (for guards) that a known-good key has not been "corrected" into an error.
MISSING means the item is absent (for example, removed or filtered).

Usage:
  python3 check_corrections.py RECORDS
RECORDS may be:
  - our lineage JSONL (fields pro_qid, options, key);
  - a JSONL / JSON / CSV export of the Hugging Face test split (fields question_id, options, answer or answer_index).
Exit code is the number of FAILs.
"""
import csv, json, re, sys, ast

def norm(s): return re.sub(r"\s+", " ", str(s)).strip().lower()

def load(path):
    rows = []
    if path.endswith(".csv"):
        rows = list(csv.DictReader(open(path, encoding="utf-8")))
    else:
        txt = open(path, encoding="utf-8").read().strip()
        rows = json.loads(txt) if txt.startswith("[") else [json.loads(l) for l in txt.split("\n") if l.strip()]
    out = {}
    for r in rows:
        qid = str(r.get("question_id", r.get("pro_qid")))
        opts = r["options"]; opts = ast.literal_eval(opts) if isinstance(opts, str) else opts
        if "answer_index" in r and str(r["answer_index"]).strip() not in ("", "None"):
            k = int(r["answer_index"])
        else:
            k = "ABCDEFGHIJ".index(str(r.get("answer", r.get("key"))).strip())
        out[qid] = (opts, opts[k])
    return out

def has(opts, text): return any(norm(o) == norm(text) for o in opts)

CHECKS = [
    ("936", "key is the 'defendant bears preponderance burden' option (Cooper v. Oklahoma)",
     lambda o, k: "not by clear and convincing evidence" in norm(k)),
    ("6268", "options do not contain both '> 95%' and '95-100%'",
     lambda o, k: not (any(norm(x).replace(" ", "") == ">95%" for x in o) and any(norm(x).replace(" ", "") == "95-100%" for x in o))),
    ("6599", "options do not contain both 'Autosomal dominant' and 'Y-linked inheritance'",
     lambda o, k: not (has(o, "Autosomal dominant") and has(o, "Y-linked inheritance"))),
    ("3542", "key no longer gives the W-band ratio 0.9850 as the L-band value",
     lambda o, k: "0.9850 at l-band" not in norm(k)),
    ("1932", "GUARD: key stays 'nationality of the victims' (do not apply the Redux correction)",
     lambda o, k: "nationality of the victims" in norm(k)),
    ("1933", "GUARD: key stays 'nationality of the victims' (duplicate of 1932)",
     lambda o, k: "nationality of the victims" in norm(k)),
]

def main(path):
    recs = load(path); fails = 0
    for qid, desc, ok in CHECKS:
        if qid not in recs: status = "MISSING"
        else:
            o, k = recs[qid]; status = "PASS" if ok(o, k) else "FAIL"
        fails += status == "FAIL"
        print(f"{status:<8} {qid:<6} {desc}")
    return fails

if __name__ == "__main__":
    if len(sys.argv) != 2: sys.exit(__doc__)
    sys.exit(main(sys.argv[1]))
