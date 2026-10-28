#!/usr/bin/env python3
"""
model.py - fixed calculator for the football agent. Standard library only.

Usage:
    python model.py match.json          # one match
    python model.py acca.json --acca    # accumulator check

The agent must RUN this file, never rewrite it. All numbers in the report
must come from this script's output.

match.json example:
{
  "match": "Team A vs Team B",
  "settlement": "90min",
  "league_avg_home_goals": 1.50,
  "league_avg_away_goals": 1.20,
  "home": {"gf_pg": 1.8, "ga_pg": 1.0, "n": 10},
  "away": {"gf_pg": 1.1, "ga_pg": 1.5, "n": 10},
  "odds_1x2": [2.10, 3.40, 3.60],
  "odds_ou": {"2.5": [1.90, 1.95]},
  "odds_btts": [1.85, 1.95],
  "market_weight": 0.7,
  "rho": -0.05
}
gf_pg / ga_pg = goals (or xG) for / against per game, over the last n games.
"""
import json
import math
import sys

MAX_GOALS = 10          # grid size 0..10
SHRINK_K = 10           # pseudo-games of league average mixed into team rates
SENSITIVITY = 0.15      # lambda +/- 15% for the uncertainty range
EV_MIN = 0.03           # minimum edge required for a pick to pass
DEFAULT_RHO = -0.05     # Dixon-Coles draw adjustment (ASSUMED, not fitted)


# ---------- helpers ----------
def devig(odds):
    """Proportional de-vig within one market. Returns (probs, margin)."""
    inv = [1.0 / o for o in odds]
    s = sum(inv)
    return [x / s for x in inv], s - 1.0


def shrink(rate, n, league_rate, k=SHRINK_K):
    """Pull a small-sample rate toward the league average."""
    return (n * rate + k * league_rate) / (n + k)


def poisson_pmf(k, lam):
    return math.exp(-lam) * lam ** k / math.factorial(k)


def tau(i, j, lh, la, rho):
    """Dixon-Coles correction for low scores."""
    if i == 0 and j == 0:
        return 1 - lh * la * rho
    if i == 0 and j == 1:
        return 1 + lh * rho
    if i == 1 and j == 0:
        return 1 + la * rho
    if i == 1 and j == 1:
        return 1 - rho
    return 1.0


def grid(lh, la, rho):
    g = {}
    for i in range(MAX_GOALS + 1):
        for j in range(MAX_GOALS + 1):
            p = poisson_pmf(i, lh) * poisson_pmf(j, la) * tau(i, j, lh, la, rho)
            g[(i, j)] = max(p, 0.0)
    total = sum(g.values())
    return {k: v / total for k, v in g.items()}


def markets(g, lines):
    home = sum(p for (i, j), p in g.items() if i > j)
    draw = sum(p for (i, j), p in g.items() if i == j)
    away = sum(p for (i, j), p in g.items() if i < j)
    out = {"1x2": [home, draw, away],
           "btts": [sum(p for (i, j), p in g.items() if i > 0 and j > 0),
                    sum(p for (i, j), p in g.items() if i == 0 or j == 0)]}
    for line in lines:
        L = float(line)
        over = sum(p for (i, j), p in g.items() if i + j > L)
        out["ou_" + str(line)] = [over, 1 - over]
    return out


def lambdas(m, scale_h=1.0, scale_a=1.0):
    lh_avg = m["league_avg_home_goals"]
    la_avg = m["league_avg_away_goals"]
    team_avg = (lh_avg + la_avg) / 2.0
    h, a = m["home"], m["away"]
    att_h = shrink(h["gf_pg"], h["n"], team_avg) / team_avg
    def_h = shrink(h["ga_pg"], h["n"], team_avg) / team_avg
    att_a = shrink(a["gf_pg"], a["n"], team_avg) / team_avg
    def_a = shrink(a["ga_pg"], a["n"], team_avg) / team_avg
    lh = lh_avg * att_h * def_a * scale_h
    la = la_avg * att_a * def_h * scale_a
    return lh, la


def check_inputs(m):
    problems = []
    for key in ("league_avg_home_goals", "league_avg_away_goals", "home", "away"):
        if key not in m:
            problems.append("missing field: " + key)
    for side in ("home", "away"):
        for key in ("gf_pg", "ga_pg", "n"):
            if side in m and key not in m[side]:
                problems.append("missing %s.%s" % (side, key))
    for name in ("odds_1x2", "odds_btts"):
        for o in m.get(name, []):
            if o <= 1.0:
                problems.append("%s has odds <= 1.0" % name)
    if m.get("home", {}).get("n", 99) < 5 or m.get("away", {}).get("n", 99) < 5:
        problems.append("fewer than 5 games for a team: unreliable")
    if m.get("settlement") not in ("90min", "90min+et", "qualify"):
        problems.append("settlement must be 90min / 90min+et / qualify")
    return problems


# ---------- main per-match report ----------
def analyze(m):
    problems = check_inputs(m)
    if any(p.startswith("missing") for p in problems):
        return {"error": "bad input", "problems": problems}

    rho = m.get("rho", DEFAULT_RHO)
    w = m.get("market_weight", 0.7)
    lines = list(m.get("odds_ou", {}).keys())

    lh, la = lambdas(m)
    base = markets(grid(lh, la, rho), lines)

    # sensitivity: min / max of each probability under lambda +/- SENSITIVITY
    variants = []
    for sh in (1 - SENSITIVITY, 1.0, 1 + SENSITIVITY):
        for sa in (1 - SENSITIVITY, 1.0, 1 + SENSITIVITY):
            l1, l2 = lambdas(m, sh, sa)
            variants.append(markets(grid(l1, l2, rho), lines))

    def rng(key, idx):
        vals = [v[key][idx] for v in variants]
        return min(vals), max(vals)

    g = grid(lh, la, rho)
    top = sorted(g.items(), key=lambda kv: -kv[1])[:5]

    labels = {"1x2": ["home", "draw", "away"], "btts": ["yes", "no"]}
    for line in lines:
        labels["ou_" + line] = ["over", "under"]

    market_odds = {"1x2": m.get("odds_1x2"), "btts": m.get("odds_btts")}
    for line, o in m.get("odds_ou", {}).items():
        market_odds["ou_" + line] = o

    report = {"match": m.get("match"), "settlement": m.get("settlement"),
              "lambda_home": round(lh, 3), "lambda_away": round(la, 3),
              "rho_assumed": rho, "market_weight": w,
              "input_warnings": problems,
              "top_scorelines": [{"score": "%d-%d" % k, "p": round(v, 4)} for k, v in top],
              "markets": {}}

    for key, names in labels.items():
        odds = market_odds.get(key)
        mkt = None
        margin = None
        if odds:
            mkt, margin = devig(odds)
        rows = []
        for idx, name in enumerate(names):
            p_model = base[key][idx]
            lo, hi = rng(key, idx)
            row = {"outcome": name,
                   "p_model": round(p_model, 4),
                   "p_model_low": round(lo, 4),
                   "p_model_high": round(hi, 4),
                   "min_odds_fair": round(1.0 / p_model, 2)}
            if mkt:
                p_mkt = mkt[idx]
                p_blend = w * p_mkt + (1 - w) * p_model
                o = odds[idx]
                ev_low = lo * o - 1          # conservative model edge
                ev_blend = p_blend * o - 1   # market-anchored edge
                row.update({"odds": o,
                            "p_market_devig": round(p_mkt, 4),
                            "p_blend": round(p_blend, 4),
                            "gap_model_vs_market": round(p_model - p_mkt, 4),
                            "ev_conservative": round(ev_low, 4),
                            "ev_blend": round(ev_blend, 4),
                            "passes": bool(ev_low >= EV_MIN and ev_blend >= 0
                                           and abs(p_model - p_mkt) <= 0.10)})
            rows.append(row)
        report["markets"][key] = {"margin": None if margin is None else round(margin, 4),
                                  "rows": rows}
    return report


def acca(legs):
    """legs: list of {"match","market","p","odds"}. Independence assumed ONLY across different matches."""
    seen = set()
    for leg in legs:
        if leg["match"] in seen:
            return {"error": "two legs from the same match are correlated; not allowed"}
        seen.add(leg["match"])
    p = 1.0
    o = 1.0
    for leg in legs:
        p *= leg["p"]
        o *= leg["odds"]
    return {"legs": len(legs), "combined_probability": round(p, 4),
            "combined_odds": round(o, 2), "ev": round(p * o - 1, 4),
            "note": "Each added leg multiplies the bookmaker margin."}


def self_test():
    """Sanity checks. Run: python model.py --test"""
    p, mg = devig([2.0, 3.5, 4.0])
    assert abs(sum(p) - 1) < 1e-9 and abs(mg - 0.0357) < 1e-3
    g = grid(1.5, 1.1, -0.05)
    assert abs(sum(g.values()) - 1) < 1e-9
    mk = markets(g, ["2.5"])
    assert abs(sum(mk["1x2"]) - 1) < 1e-9
    assert abs(sum(mk["btts"]) - 1) < 1e-9
    assert abs(sum(mk["ou_2.5"]) - 1) < 1e-9
    print("self-test OK")


if __name__ == "__main__":
    if "--test" in sys.argv:
        self_test()
        sys.exit(0)
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    with open(sys.argv[1]) as f:
        data = json.load(f)
    if "--acca" in sys.argv:
        print(json.dumps(acca(data), indent=2))
    else:
        print(json.dumps(analyze(data), indent=2))
