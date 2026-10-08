"""Loaders for the PNA micro-pilot. Data sources (git clones, no Hugging Face access from this sandbox):
  MMLU-Redux: github.com/aryopg/mmlu-redux @ 4563cfa (mmlu_redux/*.csv)
  MMLU-Pro test set: github.com/TIGER-AI-Lab/MMLU-Pro @ f418b11, eval_results/*.zip (model outputs embed every test record)
"""
import csv, glob, io, json, os, re, zipfile
DL = os.environ.get("PNA_DL", "./dl")

def load_redux():
    rows = []
    for f in sorted(glob.glob(f"{DL}/mmlu-redux/mmlu_redux/*.csv")):
        subj = os.path.basename(f)[5:-4]
        raw = open(f, "rb").read()
        try: txt = raw.decode("utf-8")
        except UnicodeDecodeError: txt = raw.decode("cp1252", errors="replace")
        delim = ";" if txt.split("\n", 1)[0].count(";") > txt.split("\n", 1)[0].count(",") else ","
        for i, r in enumerate(csv.DictReader(io.StringIO(txt), delimiter=delim)):
            r = {k.strip(): (v or "").strip() for k, v in r.items() if k}
            r["subject"], r["row"] = subj, i
            rows.append(r)
    return rows

def load_pro(zipname="model_outputs_Meta-Llama-3_1-70B-Instruct_5shots.zip"):
    z = zipfile.ZipFile(f"{DL}/MMLU-Pro/eval_results/{zipname}")
    d = json.loads(z.read(z.namelist()[0]))
    return d

def norm(s):
    return re.sub(r"[^a-z0-9]+", " ", s.lower()).strip()

def load_mmlu():
    """Original MMLU test split (Hendrycks et al. 2021), verbatim copy in github.com/FranxYao/chain-of-thought-hub @ 461e2d5, MMLU/data/test."""
    rows = []
    for f in sorted(glob.glob(f"{DL}/cot/MMLU/data/test/*_test.csv")):
        subj = os.path.basename(f)[:-9]
        for i, r in enumerate(csv.reader(open(f, encoding="utf-8"))):
            rows.append({"subject": subj, "row": i, "question": r[0], "choices": r[1:5], "answer": "ABCD".index(r[5])})
    return rows

def load_all_pro():
    """All parseable MMLU-Pro eval-result snapshots: {name: list of record dicts}."""
    out = {}
    for f in sorted(glob.glob(f"{DL}/MMLU-Pro/eval_results/*.zip")):
        z = zipfile.ZipFile(f)
        try: d = json.loads(z.read(z.namelist()[0]))
        except Exception: continue
        if isinstance(d, list) and d and all(isinstance(x, dict) and "question_id" in x for x in d):
            out[os.path.basename(f).replace("model_outputs_", "").replace(".zip", "").replace(".json", "")] = d
    return out
