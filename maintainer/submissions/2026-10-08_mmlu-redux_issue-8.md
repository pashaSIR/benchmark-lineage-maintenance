Title: Two evidence-backed candidate corrections to MMLU-Redux labels

Hello MMLU-Redux maintainers,

Thank you for creating and maintaining MMLU-Redux. Its item-level annotations make upstream benchmark problems inspectable, and they have been valuable for finding MMLU items that may need re-review.

While tracing Redux annotations into MMLU-Pro descendants, I found two cases where the Redux label or its proposed correction appears to need revision. I'm putting both in one thread to keep the noise down.

For each case, the reports below give:

* the pinned Redux revision, the subset and the row;
* the original MMLU question and published key;
* the current Redux error label and proposed answer;
* authoritative evidence for the requested change;
* known MMLU-Pro descendants;
* one requested action and a regression check.

The clearest case is the passive personality jurisdiction question in the `international_law` subset, which reaches MMLU-Pro as items 1932 and 1933. The original answer identifies jurisdiction based on the victim's nationality. Redux labels the item `wrong_groundtruth` and proposes the option based on where the offence was committed. That proposed correction describes territorial jurisdiction, not passive personality jurisdiction.

The U.S. Department of Justice states: "The passive personality principle—the victim is a citizen of the prosecuting state." (John De Pue, "Fundamental Principles Governing Extraterritorial Prosecutions–Jurisdiction and Venue," *United States Attorneys' Bulletin* 55(2), March 2007, p. 2: https://www.justice.gov/sites/default/files/usao/legacy/2007/04/20/usab5502.pdf)

I therefore suggest reviewing whether this row should retain the original victim-nationality key and have the `wrong_groundtruth` annotation removed or revised according to the project's preferred schema.

The second candidate concerns the `college_chemistry` question on the relative occupancies of the α and β spin levels at L- and W-band. It is currently labeled `bad_question_clarity`. I agree it is underspecified, and I suggest adding that no listed choice matches under standard band conventions. Details and evidence are below.

Before posting, I re-checked both records against the live MMLU-Redux dataset (`edinburgh-dawg/mmlu-redux-2.0` at revision `372ea425445d51e1ba1188c56e5e893f8138621f`, checked on 2026-10-08). The reproducible case ledger, pinned revisions, scripts, hashes and regression checks are here: https://github.com/pashaSIR/benchmark-lineage-maintenance (release v1.0.1). The archived release is at https://doi.org/10.5281/zenodo.23231363.

This is an AI-assisted audit with reproducible evidence, not a claim of independent domain-expert certification. I would appreciate confirmation, correction or disagreement on either case.

One operational question motivated this submission: **could you share whether there is currently a process for identifying downstream benchmarks affected by an upstream correction?**

The two detailed cases follow.

---

### 1. `international_law`: "What is passive personality jurisdiction?"

- **Row identification:**
  - Subset: `international_law`.
  - Exact question text: `What is passive personality jurisdiction?`
  - Pinned revisions: `edinburgh-dawg/mmlu-redux-2.0@372ea425445d51e1ba1188c56e5e893f8138621f` (Hugging Face), and `aryopg/mmlu-redux@4563cfa79b659d76716e5b6019f46bba85fa02db` (GitHub; 0-based row 19 of `mmlu_redux/mmlu_international_law.csv`).
  - Current fields: `answer = 2`, `error_type = wrong_groundtruth`, `correct_answer = 1`, `source` empty (identical in the GitHub copy and in 2.0 at the revision above).
  - Corresponding MMLU test item: `international_law`, 0-based row 61.
- **Choices:** 0 "the nationality of the offender", 1 "where the offence was committed", 2 "the nationality of the victims", 3 "the country where the legal person was Registered" (each prefixed "It is jurisdiction based on…").
- **Published key:** `answer = 2` (victim nationality).
- **Evidence:**
  - U.S. Attorneys' Bulletin (above): "the victim is a citizen of the prosecuting state."
  - ASIL Benchbook on International Law, jurisdiction chapter: "What matters in this second instance is the nationality of the victim or person at whom the conduct at issue was directed." https://www.asil.org/benchbook/jurisdiction.pdf
- **Known descendants:** MMLU-Pro question_id 1932 and 1933, two identical copies, both still keyed to victim nationality. The MMMLU and Global-MMLU translations of the MMLU item are documented but not checked item by item.
- **Requested action:** revise the annotation. Retain the original key (`answer = 2`), and remove or revise `wrong_groundtruth` and `correct_answer = 1` according to the project's preferred schema.
- **Regression check:** downstream, MMLU-Pro 1932/1933 keep "the nationality of the victims" as the key (a guard against propagating the current correction).

### 2. `college_chemistry`: relative occupancies of α and β spin levels (g = 2.05, L- and W-band, 300 K)

- **Row identification:**
  - Subset: `college_chemistry`.
  - Exact question text: `Calculate the relative occupancies of the α and β spin energy levels for a radical species with g = 2.05, at L- and W-band frequencies (take TS = 300 K).`
  - Pinned revisions: `edinburgh-dawg/mmlu-redux-2.0@372ea425445d51e1ba1188c56e5e893f8138621f` (Hugging Face), and `aryopg/mmlu-redux@4563cfa79b659d76716e5b6019f46bba85fa02db` (0-based row 99 of `mmlu_redux/mmlu_college_chemistry.csv`).
  - Current fields (identical in the GitHub copy and in 2.0 at the revision above): `answer = 3`, `error_type = bad_question_clarity`, `source = Expert`, `potential_reason = "Missing information about L- and W- bands"`.
  - Corresponding MMLU test item: `college_chemistry`, 0-based row 86.
- **Published key:** `answer = 3`, "Nα/Nβ = 0.9850 at L-band; Nα/Nβ = 0.9809 at W-band".
- **Evidence:** At a fixed frequency, Nα/Nβ = exp(−hν/kT), independent of g. Under standard band ranges (L-band 1–2 GHz, W-band ≈94–95 GHz; e.g. LibreTexts, "EPR Instrumentation"), at 300 K:

  | ν | Nα/Nβ |
  |---|---|
  | 1.0 GHz | 0.99984 |
  | 2.0 GHz | 0.99968 |
  | 94 GHz | 0.98507 |
  | 95 GHz | 0.98492 |

  The keyed "0.9850 at L-band" is the W-band value, and "0.9809 at W-band" corresponds to ≈120 GHz. None of the four choices gives an L-band value near 0.9998.
- **Known descendants:** MMLU-Pro question_id 3542, which keeps the same key among ten options and is reported separately to the MMLU-Pro maintainers (https://huggingface.co/datasets/TIGER-Lab/MMLU-Pro/discussions/55). MMMLU and Global-MMLU translations are documented but not checked item by item.
- **Requested action:** revise the annotation by adding to the existing clarity flag a note that no choice matches under standard band conventions (L ≈ 1–2 GHz, W ≈ 94–95 GHz).
- **Regression check:** downstream, MMLU-Pro 3542's key no longer gives 0.9850 as the L-band value.

---

Thank you for taking a look.
