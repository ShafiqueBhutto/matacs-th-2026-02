# MATACS-TH-2026-02: AI Proposal Triage Design

- **Full name:** Shafique Bhutto
- **Reference:** MATACS-TH-2026-02
- **Role:** Associate Software Developer
- **Time actually spent:** 2 hours (the brief suggests about 60 minutes; I spent longer because I wanted to check the scoring formulas and test the prototype script)

## Files

| File | What it contains |
|---|---|
| [diagram/process-flow.png](diagram/process-flow.png) | Process flow from upload to ranked output, showing AI steps, rule-based steps and human checkpoints |
| [WRITEUP.md](WRITEUP.md) | Answers to the five questions |
| [PROMPTS.md](PROMPTS.md) | The three prompts: fact extraction, team rating, and reason writer |
| [ranking.json](ranking.json) | Expected ranking of proposals A to E |
| [prototype/score.py](prototype/score.py) | Optional: small script that applies the scoring rules and reproduces the ranking |

## Design in one line

AI reads and summarizes. Code decides, calculates and ranks. A human makes the final call.

## Result summary

A is ranked 1, E is ranked 2, C is ranked 3 (with an embedded instruction detected, ignored and flagged), D is flagged (timeline missing) and B is ineligible (bidder does not hold the licence).

## How to run the prototype

```
python prototype/score.py
```

It needs only Python 3 and no API keys. It uses the facts that the extraction step would return, so it does not call any AI service.

## How I used AI tools

I used ChatGPT to get a first draft ranking of the five proposals, and Claude to help me understand the brief, structure the design, write the prompts and check my work. I wrote the final decisions on flagging D and ranking C myself, based on the brief.

**Where I disagreed with the AI:** ChatGPT gave scores such as 99.19 for A and 85.52 for E, but could not show how they were calculated, and the large gap looked wrong because the experience criterion is a threshold ("100 kW or more in the last 5 years"), not a competition between bids. I did not use those numbers. I replaced them with simple, explainable formulas (see WRITEUP.md and `prototype/score.py`), which gave the same order but more realistic scores (72.6, 66.5, 59.9). I also corrected ChatGPT's reason for C, which did not mention the hidden instruction in that proposal, so I added that it was detected, ignored and flagged.
