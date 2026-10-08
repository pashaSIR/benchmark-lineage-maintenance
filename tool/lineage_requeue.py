#!/usr/bin/env python3
"""lineage_requeue: "If this parent item is corrected today, what else must a maintainer inspect?"

Given a corrected or disputed MMLU parent item (or an MMLU-Pro item, which is resolved to its parent), list every
known derived item, classify what happened to the questioned content on each edge, and print a ranked re-review queue.

Coverage (read before trusting the output):
- Lineage is reconstructed, not published. MMLU-Pro items are linked to MMLU parents by normalized exact stem match,
  falling back to a fuzzy stem match (similarity >= 0.85, same subject). Heavily rewritten stems are missed.
- Joined datasets: MMLU test (FranxYao/chain-of-thought-hub@461e2d5), MMLU-Redux (aryopg/mmlu-redux@4563cfa),
  MMLU-Pro Feb-2026 and late-2024 snapshots (TIGER-AI-Lab/MMLU-Pro@f418b116 eval_results). Hugging Face revisions
  were not reachable and were not checked.
- Translations (MMMLU, Global-MMLU, MMLU-ProX) are listed from their documentation only. They are NOT joined
  item by item, so they are "re-review if present", never "affected".

Usage:
  python3 lineage_requeue.py --parent college_chemistry#86 --type no_correct_answer
  python3 lineage_requeue.py --pro 3542 --type no_correct_answer --evidence "exp(-h nu/kT) at 1.5 GHz = 0.99976"
  python3 lineage_requeue.py --pro 6268 --type option_defect --option "95-100%"
  python3 lineage_requeue.py --pro 1932 --type disputed_correction --csv out.csv
"""
import argparse, csv, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = next((r for r in (os.path.normpath(os.path.join(HERE, "..")), os.path.normpath(os.path.join(HERE, "..", "..")))
             if os.path.isdir(os.path.join(r, "pna-lineage-exp"))), os.path.normpath(os.path.join(HERE, "..")))
LINEAGE = os.environ.get("PNA_LINEAGE", os.path.join(ROOT, "pna-lineage-exp", "data", "lineage_full.jsonl"))
LATE2024 = os.environ.get("PNA_LATE2024", os.path.join(ROOT, "pna-pilot", "lineage_all.csv"))

REPOS = {"MMLU": "hendrycks/test (archived; corrections usually go to derivatives)",
         "MMLU-Redux": "aryopg/mmlu-redux (GitHub); edinburgh-dawg/mmlu-redux-2.0 (Hugging Face)",
         "MMLU-Pro": "TIGER-AI-Lab/MMLU-Pro (GitHub); TIGER-Lab/MMLU-Pro (Hugging Face)",
         "MMMLU": "openai/MMMLU (Hugging Face)",
         "Global-MMLU": "CohereForAI/Global-MMLU (Hugging Face)",
         "MMLU-ProX": "li-lab/MMLU-ProX (Hugging Face)"}
# Documented coverage only (dataset cards / papers), not item-level joins.
DOCUMENTED = [("MMMLU", "parent", "MMLU test set translated into 14 languages"),
              ("Global-MMLU", "parent", "MMLU translated into 41 non-English languages (42 incl. English)"),
              ("MMLU-ProX", "child", "MMLU-Pro (de-duplicated, 11,829 items) translated into 29 languages")]
TYPES = ["wrong_key", "no_correct_answer", "multiple_correct", "option_defect", "stale", "disputed_correction", "other"]


def norm(s):
    return re.sub(r"[^a-z0-9]+", " ", str(s).lower()).strip()


def load():
    L = [json.loads(l) for l in open(LINEAGE, encoding="utf-8")]
    late = {}
    if os.path.exists(LATE2024):
        late = {r["pro_qid"]: r for r in csv.DictReader(open(LATE2024, encoding="utf-8"))}
    return L, late


def content_status(questioned, parent_opts, child_opts):
    """Where the questioned option text sits on the parent -> child edge."""
    q = norm(questioned)
    in_p = any(norm(o) == q for o in parent_opts)
    in_c = any(norm(o) == q for o in child_opts)
    if in_p and in_c: return "inherited"
    if in_p and not in_c:
        near = [o for o in child_opts if q and (q in norm(o) or norm(o) in q)]
        return "rewritten" if near else "removed"
    if in_c and not in_p: return "added"
    return "absent"


def requeue(L, late, parent_id=None, pro=None, ctype="other", option=None):
    if pro is not None:
        hit = [r for r in L if r["pro_qid"] == str(pro)]
        if not hit or not hit[0].get("parent"):
            sys.exit(f"MMLU-Pro item {pro} not found among MMLU-derived items with a reconstructed parent.")
        parent_id = hit[0]["parent"]["id"]
    kids = [r for r in L if r.get("parent") and r["parent"]["id"] == parent_id]
    if not kids:
        sys.exit(f"No MMLU-Pro descendant of {parent_id} in the reconstructed lineage (it may have been filtered out by MMLU-Pro).")
    par = kids[0]["parent"]
    # Other MMLU rows with the same normalized stem (duplicates inside MMLU) are siblings that need the same check.
    sib = sorted({r["parent"]["id"] for r in L if r.get("parent") and r["parent"]["id"] != parent_id
                  and norm(r["parent"]["question"]) == norm(par["question"])})
    questioned = option if option is not None else par["key_text"]
    rows = []
    redux = kids[0].get("redux")
    downstream = all(content_status(questioned, par["choices"], r["options"]) == "added" for r in kids)
    rows.append(dict(rank=None, dataset="MMLU-Redux", item=parent_id, relation="re-annotation of parent",
                     edge="copy", questioned_content="not inherited" if downstream else "inherited",
                     key_note=f"Redux label: {redux['label']}" + (f"; proposed: {redux['correct']}" if redux and redux.get('correct') else "")
                     if redux else "not in Redux sample", action="none (defect entered downstream)" if downstream else "update or contest annotation", repo=REPOS["MMLU-Redux"], status="not filed"))
    for r in kids:
        st = content_status(questioned, par["choices"], r["options"])
        edited = norm(r["question"]) != norm(par["question"])
        added = [o for o in r["options"] if norm(o) not in {norm(x) for x in par["choices"]}]
        key_same = norm(r["key_text"]) == norm(par["key_text"])
        lr = late.get(r["pro_qid"])
        hist = ""
        if r.get("prev_version"):
            pv = r["prev_version"]; pk = pv["options"]["ABCDEFGHIJ".index(pv["key"])] if pv["key"] in "ABCDEFGHIJ" else ""
            hist = "key unchanged since late-2024" if norm(pk) == norm(r["key_text"]) else f"key changed since late-2024 (was: {pk})"
        else:
            hist = "not in late-2024 snapshot"
        if ctype in ("wrong_key", "no_correct_answer", "stale", "disputed_correction"):
            prio = 1 if key_same else 2
        elif ctype in ("option_defect", "multiple_correct"):
            prio = 1 if st in ("inherited", "added") else 3
        else:
            prio = 2
        rows.append(dict(rank=prio, dataset="MMLU-Pro", item=f"question_id {r['pro_qid']}", relation="derived (child)",
                         edge=("stem edited + " if edited else "") + f"options 4->{len(r['options'])} ({len(added)} added)",
                         questioned_content=st,
                         key_note=("key same as parent" if key_same else f"key differs from parent: {r['key_text']}") + f"; {hist}",
                         action="re-review item; fix key or drop/replace option", repo=REPOS["MMLU-Pro"], status="not filed"))
    for s in sib:
        rows.append(dict(rank=2, dataset="MMLU", item=s, relation="duplicate stem inside MMLU", edge="sibling",
                         questioned_content="check", key_note="", action="apply same correction if identical",
                         repo=REPOS["MMLU"], status="not filed"))
    entered_downstream = all(content_status(questioned, par["choices"], r["options"]) == "added" for r in kids)
    for name, anchor, note in DOCUMENTED:
        if anchor == "parent" and entered_downstream:
            rows.append(dict(rank=None, dataset=name, item=f"translations of parent {parent_id}", relation="documented derivative (NOT joined)",
                             edge="translation", questioned_content="not inherited", key_note=note + "; questioned content entered downstream of MMLU, so parent translations need no change",
                             action="none", repo=REPOS[name], status="n/a"))
            continue
        rows.append(dict(rank=3, dataset=name, item=f"translations of {'parent ' + parent_id if anchor == 'parent' else 'each MMLU-Pro child'}",
                         relation="documented derivative (NOT joined)", edge="translation", questioned_content="unverified",
                         key_note=note, action="re-review if present; verify membership first", repo=REPOS[name], status="not filed"))
    rows.sort(key=lambda x: (x["rank"] if x["rank"] is not None else (9 if x["status"] == "n/a" else 0)))
    return par, questioned, rows


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--parent", help="MMLU parent id, subject#row (0-based row of the Hendrycks test CSV)")
    g.add_argument("--pro", help="MMLU-Pro question_id; resolved to its MMLU parent")
    ap.add_argument("--type", default="other", choices=TYPES, help="correction type")
    ap.add_argument("--option", help="questioned option text (default: the parent's key)")
    ap.add_argument("--evidence", default="", help="authoritative evidence, carried into the report")
    ap.add_argument("--csv", help="also write the queue to this CSV")
    a = ap.parse_args()
    L, late = load()
    par, q, rows = requeue(L, late, a.parent, a.pro, a.type, a.option)
    print(f"Correction: {a.type} on MMLU {par['id']}")
    print(f"Parent stem: {par['question'][:160]}")
    print(f"Parent key: {par['key']}  {par['key_text']}")
    print(f"Questioned content: {q}")
    if a.evidence: print(f"Evidence: {a.evidence}")
    print("\nRe-review queue (rank 0 = annotation layer, 1 = carries the questioned content, 2 = check, 3 = documented only):")
    for r in rows:
        print(f"  [{r['rank'] if r['rank'] is not None else ('-' if r['status'] == 'n/a' else 0)}] {r['dataset']:<11} {r['item']:<40} {r['relation']:<36} "
              f"edge: {r['edge']:<28} content: {r['questioned_content']:<10} | {r['key_note']} | -> {r['repo']} | {r['status']}")
    print("\nCoverage: reconstructed lineage (normalized exact or fuzzy>=0.85 stem match); HF revisions unchecked; translations not joined.")
    if a.csv:
        with open(a.csv, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, list(rows[0].keys())); w.writeheader(); w.writerows(rows)


if __name__ == "__main__":
    main()
