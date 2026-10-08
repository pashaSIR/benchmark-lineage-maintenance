Title: Four high-confidence MMLU-Pro item issues, with reproducible parent–child diffs

Hello MMLU-Pro maintainers,

Thank you for maintaining MMLU-Pro and for documenting earlier corrections and duplicate-item discussions. I'm putting four high-confidence candidate corrections in one thread here rather than opening several overlapping ones.

I found these cases while reconstructing item-level lineage from the original MMLU questions into MMLU-Pro. I deliberately left out cases that depend mainly on subjective or specialist judgment. The four below are:

* an inherited answer key contradicted by a controlling primary source;
* two items where an added option makes the published answer non-unique;
* one underspecified numerical question where, under the cited frequency convention, the supplied information does not match any listed answer.

Each report gives:

* the MMLU-Pro `question_id` and the dataset revision;
* the matched MMLU parent;
* the exact parent–child option diff;
* the published key;
* authoritative evidence or a reproducible calculation;
* one requested maintenance action;
* a regression check.

Before posting, I re-checked all four records against the live Hugging Face dataset at revision `b189ec765aa7ed75c8acfea42df31fdae71f97be` on 2026-10-08. They were first observed in the test records embedded in `eval_results/model_outputs_gemini-3.1-pro_5-shots.zip` at GitHub commit `f418b116`.

The repository holds the frozen case ledger, scripts, hashes and archived tool output: https://github.com/pashaSIR/benchmark-lineage-maintenance (release v1.0.1). The archived release is at https://doi.org/10.5281/zenodo.23231363.

This is an AI-assisted audit with reproducible evidence, not a claim of independent domain-expert certification. I would appreciate confirmation, correction or disagreement on each case. I know from #31 and #36 that you keep dataset contents stable for comparability, so a documented note would be just as useful as a change.

I've also put a separate re-review queue derived from MMLU-Redux metadata in the repository: https://github.com/pashaSIR/benchmark-lineage-maintenance/blob/v1.0.1/maintainer/redux_flagged_mmlu_pro_items.csv. Redux flags 78 parent keys as wrong or as lacking a correct answer, and 74 of those keys survive unchanged in the pinned February 2026 MMLU-Pro snapshot. I am not asserting these are 74 confirmed errors, since Redux itself can be wrong (for 1932/1933 the published key is right and Redux's correction is not). They may still be useful candidates for targeted review.

One operational question motivated this work: **could you share whether there is currently a process for identifying downstream benchmarks or items affected by an upstream correction?**

The four detailed cases follow.

---

### 1. question_id 936: inherited key gives the wrong legal ground

- **Parent:** MMLU `professional_law`, test row 841. Stem unchanged.
- **Diff:** all 4 parent options kept, 6 added. The key text is unchanged (parent A → MMLU-Pro D).
- **Published key:** D, "granted, because the prosecution has the burden to prove the defendant's competency by a preponderance of evidence."
- **Issue:** The stem challenges a statute requiring the defendant "to prove mental incompetency by clear and convincing evidence." These are the facts of *Cooper v. Oklahoma*, 517 U.S. 348 (1996). The Court held that rule violates due process, and it reaffirmed that a State "may presume that the defendant is competent and require him to prove incompetence by a preponderance of the evidence" (*Medina v. California*). The burden need not fall on the prosecution, so D's ground is wrong. Option A states the correct ground: "granted, because the defendant has the burden to prove mental incompetency by a preponderance of the evidence, not by clear and convincing evidence."
- **Evidence:** official opinion, https://www.govinfo.gov/content/pkg/USREPORTS-517/pdf/USREPORTS-517-348.pdf
- **Requested action:** change the key from D to A.
- **Regression check:** the key text contains "not by clear and convincing evidence".

### 2. question_id 6268: added option duplicates the key

- **Parent:** MMLU `nutrition`, test row 124. "Fats normally contain triacylglycerols at concentrations of:"
- **Diff:** parent options are "75-95%", "50- 75%", "> 95%" (key) and "< 50%". MMLU-Pro adds "95-100%", "50-60%", "60-75%", "25-50%", "10-25%" and "< 10%".
- **Published key:** A, "> 95%".
- **Issue:** Option B, "95-100%", denotes the same interval as "> 95%", because a percentage cannot exceed 100. A and B are both correct.
- **Requested action:** replace option B with a non-overlapping distractor.
- **Regression check:** the options do not contain both "> 95%" and "95-100%".

### 3. question_id 6599: added option is correct by definition

- **Parent:** MMLU `medical_genetics`, test row 64. "Male to male transmission is a key feature of which pattern of inheritance?"
- **Diff:** parent options are autosomal dominant (key), autosomal recessive, X-linked dominant and X-linked recessive. MMLU-Pro adds six, including G, "Y-linked inheritance".
- **Published key:** I, "Autosomal dominant".
- **Issue:** Y-linked inheritance is defined by father-to-son transmission. Among the parent's four options, male-to-male transmission singled out autosomal dominant. With G added, the item has two defensible answers.
- **Evidence:** MedlinePlus Genetics: "Because only males have a Y chromosome, in Y-linked inheritance, a variant can only be passed from father to son." https://medlineplus.gov/genetics/understanding/inheritance/inheritancepatterns/
- **Requested action:** replace option G with a distractor incompatible with male-to-male transmission.
- **Regression check:** the options do not contain both "Autosomal dominant" and "Y-linked inheritance".

### 4. question_id 3542: underspecified; no option matches under standard band conventions

- **Parent:** MMLU `college_chemistry`, test row 86. Stem unchanged: relative occupancies of the α and β levels, g = 2.05, at L- and W-band, T = 300 K.
- **Diff:** all 4 parent options kept, 6 added. The key text is unchanged (parent D → MMLU-Pro A).
- **Published key:** A, "Nα/Nβ = 0.9850 at L-band; Nα/Nβ = 0.9809 at W-band".
- **Issue:** The item gives band names rather than frequencies, so strictly it is underspecified. MMLU-Redux flags the parent as `bad_question_clarity` for the missing band information. At a fixed frequency, Nα/Nβ = exp(−hν/kT), independent of g. Under the standard band ranges (L-band 1–2 GHz, W-band ≈94–95 GHz; e.g. LibreTexts, "EPR Instrumentation"):

  | ν | Nα/Nβ at 300 K |
  |---|---|
  | 1.0 GHz | 0.99984 |
  | 2.0 GHz | 0.99968 |
  | 94 GHz | 0.98507 |
  | 95 GHz | 0.98492 |

  The keyed "0.9850 at L-band" is the W-band value, and the keyed "0.9809 at W-band" corresponds to ≈120 GHz. No option gives an L-band value near 0.9998.
- **Requested action:** clarify the frequencies in the stem (e.g. "L-band, 1.0 GHz; W-band, 94 GHz") and rekey to an option that matches them.
- **Regression check:** the key no longer gives 0.9850 as the L-band value.

---

Each case comes with a re-review queue of known descendants, generated and archived before this post: the MMLU-Redux row, MMLU-Pro copies, and documented translations. The regression checks are in `maintainer/tests/check_corrections.py` in the repository. Thank you for taking a look.
