# Strongest defect cases for maintainer submission (Run G)

All cases were found by LLM reviewers and adjudicators in the Run G experiment, except case 5, which came up during review. None has been confirmed by a maintainer or a human expert yet. The "Evidence" lines say what was checked and by whom.

**Pinned data.** MMLU-Pro records come from the snapshot embedded in `TIGER-AI-Lab/MMLU-Pro@f418b116db00b065c2aea046518d8fcf74d39872`, in `eval_results/model_outputs_gemini-3.1-pro_5-shots.zip` (added 2026-02-20). The late-2024 comparison snapshot is `model_outputs_claude-3-5-sonnet-20241022_5shots.json.zip` in the same commit. MMLU comes from `FranxYao/chain-of-thought-hub@461e2d5` (a verbatim copy of the Hendrycks test CSVs; parent IDs are `subject#0-based row`). MMLU-Redux comes from `aryopg/mmlu-redux@4563cfa`. The current Hugging Face revisions were not reachable from here, so **before filing, check each item in the Hugging Face dataset viewer** (`TIGER-Lab/MMLU-Pro`, test split, filter by `question_id`) and search the existing HF discussions. Pasha reports all four still present in the current pinned Hugging Face revision; record that revision hash in `case_ledger.csv`.

**Maintainer policy.** In HF discussions #31 and #36 the maintainers say they keep dataset contents stable and add documentation notes, though they did fix a flagged wrong answer there. Expect "confirmed, documented" as often as "fixed".

**Re-review queues.** Archived, timestamped outputs are in `queues_archive/`. For any case: `python3 tool/lineage_requeue.py --pro <question_id> --type <type>`.

## Ranking

| Rank | MMLU-Pro ID | Defect | Origin | Why it ranks here | File? |
|---|---|---|---|---|---|
| 1 | 936 | Wrong key (wrong ground) | Inherited from MMLU | The stem's facts are *Cooper v. Oklahoma*; the Supreme Court's holding decides it | Yes: MMLU-Pro |
| 2 | 6268 | Added option duplicates the key's range | MMLU-Pro option augmentation | ">95%" and "95-100%" denote the same interval; no domain judgment needed | Yes: MMLU-Pro |
| 3 | 6599 | Added option is correct by definition | MMLU-Pro option augmentation | Y-linked inheritance is defined by father-to-son transmission (MedlinePlus) | Yes: MMLU-Pro |
| 4 | 3542 | Underspecified; no option matches under standard band conventions | Inherited from MMLU | Needs a stated band convention (Redux already flags clarity) | Yes: MMLU-Pro (narrow wording) and Redux note |
| 5 | 1932, 1933 | Redux correction is wrong; key is right | Annotation layer | Standard definition (ASIL benchbook). The duplicate pair is already reported in HF discussion #33 | Yes: Redux (contest label) |
| 6 | 4933 | Stale fact | Upstream source | Consensus has moved (about 50 ka or earlier), but dating is contested | Optional, framed as a question |
| 7 | 6169 | Two correct options (one inherited, one added) | Both | Anatomy; needs an oral-surgery expert | No, not without an expert |
| 8 | 5155 | Added options equally correct under a "NOT" stem | MMLU-Pro option augmentation | Depends on the source textbook's definition of "levels" | No, not without an expert |
| – | 2530, 940, 11130, 6154, 1361, 1271, 1063 | Various | Various | Expert-judgment or legally arguable | No |

Batch item: `redux_flagged_mmlu_pro_items.csv` lists the 78 MMLU-Pro items whose MMLU parent MMLU-Redux labels "wrong groundtruth" or "no correct answer". In the Feb-2026 snapshot, 74 still carry the parent's flagged key, and for 54 of the 78 Redux's proposed answer is already one of MMLU-Pro's ten options. Redux labels are evidence, not truth (case 5 is a counterexample), so this is a triage list, not a list of errors.

---

## Case 1: MMLU-Pro 936, wrong key

1. **Datasets.** MMLU-Pro; MMLU parent (not in the Redux sample).
2. **IDs.** MMLU-Pro 936 (src `ori_mmlu-professional_law`); MMLU `professional_law#841`.
3. **Stem (abridged).** A defendant is convicted. The appeal challenges "a state statute that placed the burden of proof on the defendant by requiring him to prove mental incompetency by clear and convincing evidence", and also claims a communication breakdown with counsel. "The appeal will most likely be…"
4. **Diff.** Stem unchanged; the 4 parent options are kept; the key text is unchanged (parent A, MMLU-Pro D).
5. **Published key.** D: "granted, because the prosecution has the burden to prove the defendant's competency by a preponderance of evidence."
6. **Defect.** The result ("granted") is right, but the keyed reason is wrong. *Cooper v. Oklahoma*, 517 U.S. 348 (1996), struck down exactly this rule (incompetence must be proved by clear and convincing evidence). *Medina v. California* (cited in *Cooper*) lets a state put the burden on the defendant by a preponderance, so the burden need not be on the prosecution. Option A states the correct ground: "granted, because the defendant has the burden to prove mental incompetency by a preponderance of the evidence, not by clear and convincing evidence."
7. **Origin.** Inherited from MMLU.
8. **Evidence.** *Cooper v. Oklahoma*, official opinion at https://www.govinfo.gov/content/pkg/USREPORTS-517/pdf/USREPORTS-517-348.pdf (syllabus also on Cornell LII): a rule that "allows the State to try a defendant who is more likely than not incompetent" violates due process; "a State may presume that the defendant is competent and require him to prove incompetence by a preponderance of the evidence" (*Medina*). This is a legal case, but the holding is on point. It still deserves a lawyer's read before it is used as a headline.
9. **Descendants.** MMLU-Pro 936; MMMLU and Global-MMLU translations of the parent (documented); MMLU-ProX.
10. **Action.** Rekey to A.

## Case 2: MMLU-Pro 6268, duplicate range

1. **Datasets.** MMLU-Pro; MMLU parent (not in the Redux sample).
2. **IDs.** MMLU-Pro 6268 (src `ori_mmlu-nutrition`); MMLU `nutrition#124`.
3. **Stem.** "Fats normally contain triacylglycerols at concentrations of:"
4. **Diff.** Parent options: "75-95%", "50- 75%", "> 95%", "< 50%" (key "> 95%"). MMLU-Pro adds "95-100%" (B), "50-60%", "60-75%", "25-50%", "10-25%" and "< 10%".
5. **Published key.** A: "> 95%".
6. **Defect.** A percentage above 95% is the interval (95, 100]. The added option B, "95-100%", denotes the same interval (differing only at exactly 95%), so A and B are equally correct.
7. **Origin.** MMLU-Pro option augmentation. The parent was fine.
8. **Evidence.** Interval logic; no domain source needed. Both LLM adjudicators rated it confirmed.
9. **Descendants.** MMLU-Pro 6268; MMLU-ProX versions of it (documented, not joined). The parent's translations are unaffected, because the defect entered downstream.
10. **Action.** MMLU-Pro: replace option B with a non-overlapping distractor.

## Case 3: MMLU-Pro 6599, added Y-linked option

1. **Datasets.** MMLU-Pro; MMLU parent; Redux "ok" (correct for the parent).
2. **IDs.** MMLU-Pro 6599 (src `ori_mmlu-medical_genetics`); MMLU `medical_genetics#64`.
3. **Stem.** "Male to male transmission is a key feature of which pattern of inheritance?"
4. **Diff.** Parent options: autosomal dominant (key), autosomal recessive, X-linked dominant, X-linked recessive. MMLU-Pro adds, among others, G: "Y-linked inheritance".
5. **Published key.** I: "Autosomal dominant".
6. **Defect.** Y-linked inheritance is defined by father-to-son transmission, so G answers the question at least as well as the key. Male-to-male transmission is diagnostic for autosomal dominant inheritance only *among the parent's four options*, because it rules out X-linkage.
7. **Origin.** MMLU-Pro option augmentation.
8. **Evidence.** MedlinePlus Genetics, "What are the different ways a genetic condition can be inherited?": "Because only males have a Y chromosome, in Y-linked inheritance, a variant can only be passed from father to son." The same page says X-linked patterns have "no male-to-male transmission".
9. **Descendants.** MMLU-Pro 6599; MMLU-ProX (documented). Parent translations are unaffected.
10. **Action.** Replace option G.

## Case 4 (filed with narrower wording): MMLU-Pro 3542, underspecified, no option matches under standard band conventions

1. **Datasets.** MMLU-Pro (snapshot above); parent in MMLU; annotation in MMLU-Redux.
2. **IDs.** MMLU-Pro `question_id` 3542 (src `ori_mmlu-college_chemistry`); MMLU `college_chemistry#86`.
3. **Parent and derived item.** Stem (unchanged): "Calculate the relative occupancies of the α and β spin energy levels for a radical species with g = 2.05, at L- and W-band frequencies (take TS = 300 K)."
4. **Diff.** Stem unchanged; the 4 parent options are kept and 6 are added; the key text is unchanged (parent D, MMLU-Pro A).
5. **Published key.** A: "Nα/Nβ = 0.9850 at L-band; Nα/Nβ = 0.9809 at W-band".
6. **Defect.** At a fixed microwave frequency, Nα/Nβ = exp(−hν/kT), independent of g. At 300 K, L-band (1 to 2 GHz) gives 0.99968 to 0.99984, and W-band (94 to 95 GHz) gives 0.98507 to 0.98492. The key's "L-band" value, 0.9850, is the W-band value; its "W-band" value, 0.9809, corresponds to about 120 GHz. No option gives an L-band value near 0.9998. Strictly, the item is **underspecified** (it names bands, not frequencies), as Redux noted. Under any standard band convention, though, no option matches. File it with that narrower wording, and do not call it a one-line proof.
7. **Origin.** Inherited from MMLU. MMLU-Redux labels the parent "bad question clarity" ("Missing information about L- and W- bands"). On this calculation, "no correct answer" is the more accurate label.
8. **Evidence.** The calculation (h = 6.62607015e−34 J s, k = 1.380649e−23 J/K, T = 300 K; reproduced in this review). Band frequencies: LibreTexts, "EPR Instrumentation" (UC Davis Chem 205): L-band 1 to 2 GHz, W-band 95 GHz.
9. **Known descendants.** MMLU-Pro 3542 (key unchanged since late 2024); the Redux row. Documented but not joined: MMMLU (14 languages) and Global-MMLU (41 non-English) translations of the parent; MMLU-ProX (29 languages) of the MMLU-Pro item. The parent comes from the "Electron Paramagnetic Resonance" source, where Redux flags 16 of 19 items, so siblings from that source deserve a look.
10. **Action.** MMLU-Pro: replace the key with a correct option (for example, L-band ≈ 0.9998 and W-band ≈ 0.9851), or drop the item. Redux: relabel to "no correct answer". Translation maintainers: re-review if present.

## Case 5: MMLU-Pro 1932 and 1933, Redux correction contested

1. **Datasets.** MMLU-Redux (GitHub `aryopg/mmlu-redux@4563cfa`; the Redux 2.0 Hugging Face row at `edinburgh-dawg/mmlu-redux-2.0@372ea42` has the same label, as reported by the separate Run H). MMLU-Pro.
2. **IDs.** MMLU `international_law#61`; MMLU-Pro 1932 and 1933, two copies with identical options.
3. **Stem.** "What is passive personality jurisdiction?"
4. **Diff.** 4 options to 10 options; key text unchanged.
5. **Published key.** "It is jurisdiction based on the nationality of the victims".
6. **Defect claimed by Redux.** "wrong groundtruth", proposing "where the offence was committed" (territorial jurisdiction). That correction is wrong: passive personality jurisdiction is jurisdiction based on the victim's nationality.
7. **Origin.** Annotation layer. The benchmark items are correct.
8. **Evidence.** ASIL Benchbook on International Law, jurisdiction chapter: "What matters in this second instance is the nationality of the victim or person at whom the conduct at issue was directed."
9. **Descendants of the bad label.** Any pipeline that applies Redux corrections downstream would break MMLU-Pro 1932 and 1933 and the parent's translations.
10. **Action.** Redux: relabel the parent as "ok". MMLU-Pro: no key change. Duplicates are **not a new finding**: HF discussion #26 (Jan 2025, 316 duplicate rows, closed as resolved in Apr 2025) and #33 (Sep 2025, 158 exact duplicate pairs including 1932/1933, closed Oct 2025 with a pointer to #31/#36). Our 157 identical-option pairs among MMLU-derived items, on the Feb-2026 GitHub snapshot, is a reproduction. Don't file it.

## Case 6 (optional): MMLU-Pro 4933, stale occupation date

- MMLU `prehistory#169`. Stem: "What occupation date do most archaeologists agree on for Australia?" The key is H, "soon after 40,000 years ago" (inherited; Redux "ok"; source is an OUP quiz page). Current work puts initial occupation at about 47 to 50 ka (O'Connell & Allen) and possibly about 65 ka (Clarkson et al. 2017, *Nature* 547:306, contested). The added option B, "approximately 50,000 years ago", now fits better. This is a dating consensus, not a calculation, so file it as a question ("is the key still current?"), not as an error.

## Not to be filed without an expert

- **6169 (mandible fracture).** Parent option J was already defensible, and the added F is defensible too. Needs an oral-surgery read.
- **5155.** "Levels of society" depends on the source textbook.
- **2530, 940, 11130, 6154, 1361, 1271, 1063.** These rest on conceptual or legal judgment. The LLM adjudicators rated them probable or split.
