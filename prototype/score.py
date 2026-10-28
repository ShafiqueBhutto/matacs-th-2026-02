"""
Scoring rules for MATACS-TH-2026-02 (Commercial Solar Installation).

This script is the "plain code" part of the design: AI extracts the facts,
this code applies the admin's weights and formulas. Same input -> same output.
Facts below are what the extraction step (Prompt 1) would return for each
proposal. Team ratings are what Prompt 2 would return (0-5).
"""
import json

# ---- Admin criteria (in the real tool these come from the admin database) ----
CRITERIA = {
    "budget_ceiling": 260000,
    "max_weeks": 16,
    "weights": {"experience": 30, "price": 25, "timeline": 15, "warranty": 15, "team": 15},
    "experience_full_marks_at": 10,   # 10+ qualifying installs = full marks
    "price_full_marks_pct_under": 0.20,  # 20% under ceiling = full marks
    "timeline_full_marks_weeks": 8,   # 8 weeks or less = full marks
    "panel_warranty_cap": 25,
    "workmanship_warranty_cap": 15,
}

# ---- Facts extracted per proposal (None = not stated) ----
PROPOSALS = {
    "A": dict(licence_held=True, wsib_and_insurance=True, installs=14, price=238000,
              weeks=12, panel_yrs=25, work_yrs=10, team_rating=4, injection=False),
    "B": dict(licence_held=False, wsib_and_insurance=True, installs=6, price=189500,
              weeks=10, panel_yrs=25, work_yrs=5, team_rating=1, injection=False),
    "C": dict(licence_held=True, wsib_and_insurance=True, installs=9, price=244000,
              weeks=14, panel_yrs=25, work_yrs=10, team_rating=3, injection=True),
    "D": dict(licence_held=True, wsib_and_insurance=True, installs=11, price=231000,
              weeks=None, panel_yrs=25, work_yrs=10, team_rating=3, injection=False),
    "E": dict(licence_held=True, wsib_and_insurance=True, installs=8, price=242500,
              weeks=13, panel_yrs=25, work_yrs=12, team_rating=5, injection=False),
}

def clamp(x):
    return max(0.0, min(1.0, x))

def score(p, c=CRITERIA):
    w = c["weights"]
    exp = clamp(p["installs"] / c["experience_full_marks_at"])
    full_price = c["budget_ceiling"] * (1 - c["price_full_marks_pct_under"])
    price = clamp((c["budget_ceiling"] - p["price"]) / (c["budget_ceiling"] - full_price))
    timeline = clamp((c["max_weeks"] - p["weeks"]) / (c["max_weeks"] - c["timeline_full_marks_weeks"]))
    warranty = (clamp(p["panel_yrs"] / c["panel_warranty_cap"]) +
                clamp(p["work_yrs"] / c["workmanship_warranty_cap"])) / 2
    team = p["team_rating"] / 5
    parts = {"experience": exp, "price": price, "timeline": timeline,
             "warranty": warranty, "team": team}
    points = {k: round(w[k] * v, 2) for k, v in parts.items()}
    return round(sum(w[k] * v for k, v in parts.items()), 1), points

def main():
    ranked, others = [], []
    for name, p in PROPOSALS.items():
        if not (p["licence_held"] and p["wsib_and_insurance"]):
            others.append(dict(proposal=name, rank=None, status="ineligible", score=None,
                reason="Bidder does not hold the Ontario electrical licence; work is subcontracted and unconfirmed."))
        elif p["weeks"] is None:
            others.append(dict(proposal=name, rank=None, status="flagged", score=None,
                reason="Timeline not stated (depends on a later site assessment); human must confirm before scoring."))
        else:
            total, pts = score(p)
            ranked.append((total, p["price"], name, pts))
    ranked.sort(key=lambda r: (-r[0], r[1]))  # higher score first, tie -> lower price

    out = []
    for i, (total, _, name, pts) in enumerate(ranked, 1):
        print(name, total, pts)
        out.append(dict(proposal=name, rank=i, status="ranked", score=total, reason=""))
    out += others
    return out

if __name__ == "__main__":
    print(json.dumps(main(), indent=1))
