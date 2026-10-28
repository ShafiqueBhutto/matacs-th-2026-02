# WRITEUP.md

Reference: MATACS-TH-2026-02

Design principle: **AI reads and summarizes. Code decides, calculates and ranks. A human makes the final call.** See `diagram/process-flow.png` for the full flow and `PROMPTS.md` for the prompts.

## 1. AI vs. rules

**AI is used in three places:**
- **Fact extraction (step 4):** proposals are messy free text, so AI is good at finding price, weeks, warranties, licence statements and team details. Every value must come with an exact quote.
- **Team and approach rating (step 9):** this is the one criterion that needs judgement. AI rates it 0-5 against a fixed checklist rubric.
- **One-line reasons (step 11):** AI turns already-computed results into plain language. It cannot change any score.

**Plain code or rules are used for everything else:** PDF text extraction, loading criteria, quote validation, mandatory pass/fail checks, missing-data checks, all formulas, weighting, ranking and tie-breaks, and the audit log.

**Where I drew the line:** anything that must be identical every time, or that must follow the admin's settings exactly, is code. AI never produces a final score or rank, so even a manipulated AI step cannot move a proposal up the list.

## 2. Consistency and explainability

- **Repeatability:** all scoring is code with fixed formulas, so the same extracted facts always give the same score. The AI runs at temperature 0, with a fixed model version, JSON-only output and one proposal per call.
- **Same proposals ranked twice:** the extracted facts are stored and reused, so re-ranking gives an identical result. A fresh extraction could differ slightly, so the tool extracts twice on first run and flags any field where the two runs disagree.
- **Explainability:** for every proposal the reviewer sees points per criterion, the exact quote behind each fact, any flags, and the one-line reason. Scores depend only on that proposal's own facts, not on other bids, so adding or removing a proposal never changes anyone else's score.
- **Scoring formulas (all values configurable by admin):** experience = installs / 10, capped at 1. Price = distance below the budget ceiling, full marks at 20% under. Timeline = full marks at 8 weeks or less, zero at 16. Warranty = average of panel and workmanship years against caps. Team = AI rating / 5.

## 3. Human in the loop

**Human checkpoints:**
- Flagged proposals (missing facts, injection attempts, unreadable PDFs) must be reviewed before they can be ranked.
- The reviewer sees the full ranking with evidence, can confirm it, or override a score, status or rank. An override requires a written reason.
- The final award decision is always made by a person. The tool only recommends an order.

**What is logged for audit:** uploaded files (with hashes), extracted text, criteria version ID, prompt and model versions, raw AI outputs, validated facts, per-criterion scores, flags, final ranking, and every override with who, when and why.

## 4. Changing criteria

- Criteria are **versioned**. Editing weights or criteria creates a new version; the old one is kept.
- Every score is saved with the criteria version used. After an edit, older results are marked **"scored under an earlier version"** and are never silently changed.
- Because extracted facts are stored, re-scoring under the new version is cheap and does not need the AI again. The AI is only re-run if a **new criterion** needs facts that were never extracted.
- A changed mandatory criterion re-runs eligibility checks. If a result would change, the reviewer is shown a before/after comparison and must confirm.
- A decision already awarded stays tied to the version it was made under.

## 5. Risks and safeguards

| Risk | Safeguard |
|---|---|
| **Wrong extraction** (misread price, weeks) | Every value needs an exact quote. Code checks the quote exists in the text. Double extraction. Reviewer sees the quote. |
| **Made-up facts** | "If not stated, return null" rule. No guessing. Missing key facts mean flagged, not scored. |
| **Prompt injection** | Proposal text is treated as data. Suspicious instructions are reported, not followed. AI does not decide scores, so injection cannot change rank. Reviewer is alerted. |
| **Bias** | The rating prompt sees only the team passage, not the company name or other bids. Rubric is a checklist, so a longer or better-written proposal gains nothing. Humans can review and override. |
| **Cost** | One call per proposal plus one short rating call. Facts are cached. Re-scoring after criteria edits needs no new AI calls. |
| **Unreadable or scanned PDFs** | Flagged for manual handling instead of scored on partial text. |
| **Over-trust in the ranking** | Scores are presented as decision support. Reviewer must open evidence for flagged items, and the final award stays human. |

## Sample set handling

- **A, E:** complete and scored normally. A ranks first, E second.
- **C:** contains an embedded instruction to rank it first. It is ignored, flagged for the reviewer, and C is scored on its normal facts (rank 3).
- **D:** timeline is not stated, so it is **flagged**, not scored. A person must obtain the timeline first.
- **B:** the bidder does not hold the licence itself (electrical work is subcontracted and unconfirmed), so it is **ineligible** despite having the lowest price.

## Assumptions

- Experience uses the installs count as claimed. C's install dates start earlier than the other bids, so some installs may fall outside the 5-year window. The reviewer should verify this.
- Price, timeline and warranty reference points (20% under budget, 8 weeks, warranty caps) are my own defaults. In the real tool the admin would set them.
- I could not ask clarifying questions, so I chose to rank C (injection ignored and flagged) and to flag D (not rank it with a zero).
