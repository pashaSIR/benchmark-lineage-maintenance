# Does item-level lineage improve benchmark-defect detection? Results (PROVISIONAL)

Run 2026-10-07. MMLU → MMLU-Redux → MMLU-Pro, 100 fresh MMLU-derived MMLU-Pro items, three review conditions, LLM reviewers and LLM adjudicators. All rates are provisional: no human domain experts were involved, and every reviewer and adjudicator was an instance of the same model family working in an isolated session. Isolation was enforced by instruction (separate agents, separate packets), not by access control.

## Data and sample

- MMLU-Pro under review: Feb-2026 snapshot embedded in `TIGER-AI-Lab/MMLU-Pro@f418b116` `eval_results/model_outputs_gemini-3.1-pro_5-shots.zip` (newest revision reachable; Hugging Face is blocked from this sandbox, so the current HF revision was not checked). Version history compared against the late-2024 snapshot used in the pilot (claude-3-5-sonnet-20241022 outputs in the same commit).
- MMLU: `FranxYao/chain-of-thought-hub@461e2d55` MMLU/data/test. MMLU-Redux: `aryopg/mmlu-redux@4563cfa7` (repo HEAD, Nov 2024).
- Population: 6,808 MMLU-derived items in the Feb-2026 snapshot, minus the 50 pilot items → 6,758. Uniform random draw of 100, seed **20261008**, no stratification. sha256 of the ordered qid list: `2e318852cfa8837d2072fd21b06ad2b19ce2492c80eb2b5dc502b53811ab6156`.
- Rubric and thresholds frozen in `rubric.md` before the draw.

## Design

| Arm | Sees | Reviewers |
|---|---|---|
| A item-only | MMLU-Pro stem, options, key | 4 isolated agents × 25 items |
| B lineage-aware | A + MMLU parent, option provenance (copied/NEW/dropped), key diff, Redux label/correction/source, MMLU-Pro version history, family background | 4 isolated agents × 25 items |
| C extra-evidence control | A + mandatory protocol: solve before reading key, check every option, external lookup for every fact-dependent item | 4 isolated agents × 25 items |

Item order randomized per arm (seeds 101/102/103). Adjudication set: 20 items any arm flagged (confirmed/probable/ambiguous) + 12 random all-clean items (15%, seed 20261009). Two independent adjudicators saw item + lineage + pooled, unlabeled claims; a third broke 4 splits.

## Results table

| Metric | Item-only (A) | Lineage-aware (B) | Difference (B−A) | Extra-evidence (C) |
|---|---:|---:|---:|---:|
| Gold defects found (of 14) | 8 | 12 | +4 | 9 |
| Recall | 57.1% | 85.7% | **+28.6 pp** (95% CI +6.3 to +54.5) | 64.3% |
| Precision | 100% (8/8) | 85.7% (12/14) | −14.3 pp | 100% (9/9) |
| Correct origin localization (of 14) | 3 (21%) | 12 (86%) | +64 pp | 4 (29%) |
| Avg agent-minutes/item | 0.044 | 0.056 | +0.012 | 0.105 |
| Avg agent-minutes/gold defect found | 0.55 | 0.47 | −0.09 | 1.17 |
| Ambiguous cases | 7 | 5 | −2 | 6 |
| External lookups | 0 | 0 | 0 | 79 |

Minutes are LLM agent wall-clock (batch duration ÷ items), not human time; they show relative cost only.

- **Δ recall(B−A) = +28.6 pp** → pre-registered "meaningful win" (≥ +10). Exact McNemar on discordant gold defects: B-only 4, A-only 0, p = 0.125.
- **Δ recall(B−C) = +21.4 pp** (95% CI 0 to +45.5; B-only 3, C-only 0, p = 0.25). C − A = +7.1 pp.
- Localization among the 8 defects both A and B detected: A 3/8, B 8/8.
- Adjudicator agreement: κ = 0.80 defect/no-defect, 0.86 type, 0.82 origin (11 agreed defects). 3 of 32 items needed a tiebreak.
- Random clean check: 0 of 12 all-clean items turned out defective.
- Gold defects: 14 (14%); 3 rated confirmed by both adjudicators, the rest probable. By origin: 9 introduced by MMLU-Pro's added options (O2), 4 inherited from MMLU (O1), 1 upstream stale fact (O4). By type: 9 added-option second correct answer, 2 no unique answer, 2 wrong key, 1 stale.
- B changed the binary verdict relative to A on 6 items and the severity on 11.
- Redux: only 1 sampled parent was Redux-flagged (PRO-3542, "bad question clarity"); all arms caught it. 4 gold defects had a Redux "ok" parent; for 3 the defect entered downstream (added options), so Redux was right about the parent. Only PRO-4933 (stale dating of Australian settlement) overturns a Redux "ok" at the parent level.

### Sensitivity analyses

| Gold / detection rule | n gold | A | B | C | B−A | B−C |
|---|---:|---:|---:|---:|---:|---:|
| Primary (pre-registered) | 14 | 57% | 86% | 64% | +28.6 | +21.4 |
| Strict gold (both adjudicators "confirmed") | 3 | 100% | 100% | 100% | 0 | 0 |
| Arms count "ambiguous" as a flag | 14 | 79% | 93% | 86% | +14.3 | +7.1 |
| Lineage-blind gold, both blind adjudicators agree (post hoc) | 9 | 78% | 89% | 89% | +11.1 | 0 |
| Lineage-blind gold, either blind adjudicator (post hoc) | 15 | 53% | 87% | 60% | +33.3 | +26.7 |

B beats A under every rule except the 3-item strict set. B's margin over C is fragile: it disappears when the gold standard is built without lineage under the conservative rule, and drops below +10 pp when "ambiguous" counts as a flag. Blind-adjudicator agreement was lower (κ = 0.60) and blind gold agreed with primary gold at κ = 0.54.

## B-only catches (missed by A, found by B)

| Item | Defect | Lineage fact that exposed it | Authoritative evidence (adjudicator) | A's verdict |
|---|---|---|---|---|
| PRO-940 (law) | "Which will NOT terminate a contract by operation of law?" Added options "fulfillment of contract" and "expiration of the term" also do not operate by law (discharge by performance / by agreement). T3, O2 | Options C and G are NEW; all parent options except the key were operation-of-law events | Contract-law treatment of modes of discharge (performance, agreement, breach, impossibility, operation of law) | none (noted "minor ambiguity") |
| PRO-5155 (sociology) | "Which is NOT a level of society?" Added "the church" and "the school" are organizations like the keyed "the office". T3, O2 | church, school, continent, city, region are NEW; parent had household, office, global village, nation state | Fulcher & Scott, *Sociology*, ch. 1 levels of society | ambiguous |
| PRO-1063 (law) | Adverse possession: tenant's possession is permissive during the lease, so only 17 of 20 years had run; added option "statutory period not yet reached" is also correct. T3, O2 (decided by tiebreak) | Option G is NEW; parent had no statutory-period option | Adverse-possession doctrine (Powell on Real Property; Restatement): no hostility during lease absent repudiation | ambiguous |
| PRO-6154 (aging) | "Senescence refers to…" key "increased vulnerability"; "biological aging" is the standard definition. T2, O1 | Competing options D and E are copied from the MMLU parent, so the problem is inherited, not added | Standard definition: senescence = biological aging, gradual functional deterioration | ambiguous |

Three of the four B-only catches were items A had already marked "ambiguous". Lineage mostly did not reveal an invisible problem; it told the reviewer that the competing option was a GPT-4-added distractor (or, for PRO-6154, an original option), which turned suspicion into a committed flag with a named origin. A found nothing that B missed. Both A and B missed PRO-1361 and PRO-1271 (law items with added near-paraphrase options, decided by tiebreak).

## Propagation

| Gold defect origin | n | In-data descendants (MMLU-Pro items with same parent + MMLU-Redux copy) | Documented public descendants |
|---|---:|---:|---:|
| Upstream (O1/O4) | 5 | 1.4 per defect (1 MMLU-Pro item each, Redux copy for 2) | ~85 per defect: MMMLU 14 translations + Global-MMLU 41 non-English translations of the parent + MMLU-ProX 29 language versions of the MMLU-Pro item |
| Transformation (O2) | 9 | 0 | ~29 per defect (MMLU-ProX language versions) |

Each MMLU parent maps to exactly one MMLU-Pro item in this sample, so inside the MMLU → Redux → Pro family a parent correction flags only one or two items. The large numbers come from translated derivatives, counted from their documentation (Global-MMLU: "all 14K samples… across 42 languages"; MMMLU: MMLU test set in 14 languages; MMLU-ProX: 11,829 items × 29 languages after de-duplicating MMLU-Pro). Per-item membership in those datasets was **not verified** because Hugging Face is blocked here. The claim is "requires re-review", not "is wrong". Lineage also tells a maintainer that 9 of 14 defects (the O2 ones) do not need an upstream fix at all.

Provenance reconstruction cost: `src/build_lineage.py` rebuilds the full lineage for 6,808 items in seconds; parent matching failed for 1 item.

## Pre-registered decision checks

| Kill condition | Result |
|---|---|
| Δ recall(B−A) < +10 pp | No: +28.6 pp |
| B rarely changes origin localization | No: 12/14 vs 3/14 |
| Propagation finds almost no actionable descendants | Within the family yes (≈1 per defect); across public translations no (≈29–85 per defect, documented, not item-verified) |
| Provenance reconstruction too costly | No |
| Adjudicator κ < 0.4 | No: 0.80 (blind pair 0.60) |

Publication rule A (Δ B−A ≥ 10, Δ B−C ≥ 10, localization lift ≥ 20, κ ≥ 0.4): **met on the primary pre-registered analysis.**

## Publication decision

**A. PUBLISHABLE AUDIT RESULT**, provisional on human replication.

Basis: the pre-registered rule is met. The limits are stated, not rescued: n = 14 gold defects; McNemar p = 0.125 (B vs A) and 0.25 (B vs C); the lineage-over-effort margin (B vs C) vanishes under a lineage-blind conservative gold and under the ambiguous-as-flag rule; the mechanism is mostly confidence/commitment on added-option defects that A half-saw, plus localization, which lineage supplies almost by construction. Rates must not be published as final until two human domain reviewers redo A and B and a human adjudicator settles gold.

## Revised thesis sentence (for the "Research note draft" thread; draft not edited here)

> **Derived benchmarks should preserve item-level lineage because lineage-aware review catches and localizes defects that item-only review misses.**

## Final question

Does lineage give an auditor enough incremental value to justify parent IDs, transformation logs, and correction propagation as a standard part of benchmark review? **Yes for parent IDs and transformation logs (option-level provenance):** in this pilot they raised recall from 57% to 86%, cost about a quarter more review time than item-only review, and beat a reviewer given twice the time and 79 web lookups. They also localized 12 of 14 defects versus 3. **Correction propagation is justified mainly across translated derivatives:** within MMLU → Redux → MMLU-Pro a fix touches about one item, while public translations multiply each upstream fix into dozens of items to re-review. The lineage-versus-more-effort comparison is the weakest link and is the first thing a human replication must test.

## Deviations and limitations

1. Hugging Face blocked; newest GitHub-embedded MMLU-Pro snapshot (Feb 2026) used. 12 late-2024 items are absent from it.
2. Packet rendering bug (fuzzy option matching mislabeled edited/near-duplicate options) found and fixed before any reviewer ran; checking it, the experimenter viewed two B-packet items.
3. Reviewers in A and B made 0 external lookups though allowed; C made 79 by protocol.
4. Primary adjudicators saw lineage, which could bias gold toward B. The lineage-blind robustness check was added after the primary analysis (not pre-registered).
5. All reviewers and adjudicators are the same model family; agreement between them is not independent human agreement. LLM memory of benchmark items cannot be excluded.
6. Time is agent wall-clock for 25-item batches, not human minutes.
7. Propagation counts for translated derivatives come from dataset documentation, not item-level joins.
