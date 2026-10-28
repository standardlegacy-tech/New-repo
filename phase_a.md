# PHASE A - Daily Football Analysis (before matches)

How to run me: "Run phase_a.md. Mode: A1" (morning scan) or "Mode: A2 <match>" (pre-kickoff recheck).

## USER SETTINGS (edit these, do not change anything else)

- TIMEZONE: Africa/Cairo
- LEAGUES (fixed list; ignore all others): [Premier League, La Liga, Serie A, Bundesliga, Ligue 1, Champions League, Europa League]
- MAX_MATCHES_DEEP_ANALYSIS: 8
- OUTPUT_LANGUAGE: English (short Arabic summary at the end)
- BOOKMAKER_FOR_BETTING: 1xbet (you probably cannot read its prices; see ODDS)

## STEP 0 - CAPABILITY CHECK (always first, report REAL output)

1. List the tools you actually have this session: web search, code sandbox, file access, GitHub.
2. Run `python --version` and `python -c "import json, math; print('ok')"`.
3. Check that `model.py` exists in the repo/sandbox. Run `python model.py --test`. It must print `self-test OK`.
4. Check whether the sandbox has internet access.

If `model.py` or code execution is unavailable: STOP and tell me. Do not replace it with mental arithmetic. Do not continue to picks.
If web search is unavailable: STOP and tell me.
Never claim to have used a tool or source you did not actually use.

## HONESTY RULES

- Every number comes from a source retrieved THIS session, with source name and retrieval time. No source = "no data".
- Never use statistics from memory. Never invent "similar matches", databases, or sources.
- Label every claim: FACT (from a source), CALC (output of model.py), JUDGMENT (your opinion).
- All probabilities in the report must be copied from `model.py` output. Never type a probability yourself.
- Football is high variance. Never write "sure", "safe bet", "guaranteed", or "lock".
- "No pick" is a valid answer for any match and for the whole day. Never fill a coupon to reach a number of picks.
- Source reliability for news: OFFICIAL (club/league/federation) > TRUSTED REPORTER (named, established outlet) > RUMOR (anything else). RUMOR never changes a pick; list it as a risk only.

## A1 - MORNING SCAN

### A1.1 Schedule
Find today's matches in the LEAGUES list for TIMEZONE. Verify each fixture (teams, date, kickoff time) against 2 sources. Watch for same-name teams, women's/youth teams, postponed or rescheduled matches. Table: kickoff | competition | home | away | verified (yes/no).
If more than MAX_MATCHES_DEEP_ANALYSIS, deep-analyze the matches with the best data availability and list the others as "not analyzed".

### A1.2 Exclusions (mark the match "NO MODEL - excluded from picks")
- Second legs and decisive cup ties (aggregate/qualification dynamics).
- Teams with a big match in the next 3 days where rotation is likely and unconfirmed.
- Fewer than 5 recent games of data for either team.
- Fixture not verified, or major contradictory news.
- Competition where you cannot find reliable stats.

### A1.2b DO NOT STOP EARLY
Finding fixtures is only the start. For EVERY non-excluded match you must attempt A1.3, A1.4 and A1.5 completely. Do not end the run after the schedule.
- If a source is blocked or empty, try at least 2 other named sources before writing "no data".
- If you still fail, report exactly what failed: match, field, sources tried, error or reason.
- Matches with complete inputs get a model run even if the result is "No pick". Show the model.py output for them.
- Only matches with missing inputs after those attempts are marked "not modeled: <specific reason>".
- Also state, per league in LEAGUES, either its fixtures or "no fixtures found today" with the source checked.

### A1.3 Data per remaining match (with sources)
- Last 10 matches for each team, all venues (opponent, venue, score). Use goals for/against per game (`gf_pg`, `ga_pg`) and `n`. If xG is available from a named source, use xG per game instead and label it XG.
- League season averages for home goals per game and away goals per game (`league_avg_home_goals`, `league_avg_away_goals`) from a named source.
- H2H last 5 meetings (context only; it does not feed the model).
- Injuries/suspensions with source tier (OFFICIAL / TRUSTED / RUMOR) and lineup status: confirmed / expected / unknown.
- Team news from yesterday and today (manager comments, travel, rotation, off-field issues).
- Match context ONLY if evidenced: derby, title/relegation/qualification stakes, congestion, weather.
Flag stale or contradictory data. Do not smooth over conflicts.

### A1.4 Odds
For each match get 1X2, over/under 2.5, BTTS from at least 2 sources if possible. Record bookmaker and retrieval time. Freshness is measured from YOUR retrieval time, not from the site's publication time. Record "retrieved HH:MM; site update time: shown/unknown".
Odds retrieved less than 2 hours ago are usable. If the site shows no update time, label them AGE-UNVERIFIED: they may be used for the model benchmark and for PROVISIONAL picks in A1, but a pick becomes FINAL only after the A2 recheck, with odds retrieved within 2 hours of kickoff. Odds retrieved more than 2 hours ago are STALE and excluded.
You probably cannot read 1xbet. Use what you can access as an estimate. Every pick must carry MIN ACCEPTABLE ODDS (from model.py `min_odds_fair`, rounded up). If 1xbet's price is lower than that, the pick is invalid; I check that myself.

### A1.5 Run the model
For each match create `match_<id>.json` in the format below and run `python model.py match_<id>.json`. Show the output unchanged.

```json
{
  "match": "Home vs Away",
  "settlement": "90min",
  "league_avg_home_goals": 0.0,
  "league_avg_away_goals": 0.0,
  "home": {"gf_pg": 0.0, "ga_pg": 0.0, "n": 10},
  "away": {"gf_pg": 0.0, "ga_pg": 0.0, "n": 10},
  "odds_1x2": [0.0, 0.0, 0.0],
  "odds_ou": {"2.5": [0.0, 0.0]},
  "odds_btts": [0.0, 0.0],
  "market_weight": 0.7
}
```

Known limits of model.py (state them in the report): it ignores opponent strength and player availability; rho is assumed, not fitted; it uses small samples with shrinkage. So `passes: true` is necessary, NOT sufficient. You must still check news and lineup.
If any input is missing, write "no data" and do not run that market.

### A1.6 Pick selection
For each match choose AT MOST ONE market, or "No pick". A pick is allowed only if ALL are true:
1. model.py shows `passes: true` for that outcome.
2. Odds are retrieved under 2 hours ago from a named source. Age-unverified odds make the pick PROVISIONAL until the A2 recheck.
3. No unresolved OFFICIAL or TRUSTED news that the model cannot see (key injury, rotation, suspension). If one exists and is unconfirmed, drop the pick.
4. You can state, in one line, which concrete information the market may be missing, or the pick is based on the model/market blend alone. If the model differs from the market by more than 10 points, trust the market.
5. Settlement basis is stated (see below).

Daily limit: at most 4 picks in total. If fewer qualify, output fewer.

### A1.7 Settlement rules
- Every pick states its basis: `90min` (regular time plus stoppage, excluding extra time and penalties), `90min+et`, or `qualify`. Default is `90min`.
- 1X2, over/under and BTTS picks are valid only on `90min` unless the market name says otherwise.
- Never derive a "to qualify" pick from 90-minute probabilities.
- You cannot read 1xbet's rules. For every pick write: "VERIFY at 1xbet: exact market name, settlement basis, void rules for postponed/abandoned matches." I verify; you do not claim it.
- If the settlement basis is unknown, the pick is invalid.

### A1.8 Coupon options
Create `acca.json` (list of legs with `match`, `market`, `p`, `odds`) and run `python model.py acca.json --acca`.
- Option 1: singles list.
- Option 2: one accumulator, max 3 legs, all from different matches, using model.py output. Show combined probability and odds. State that accumulators lower the win chance and multiply the bookmaker margin.
- If no pick qualifies: "No recommended coupon today."
- Never suggest stake sizes.

### A1.9 Output format (short, easy to read)
1. Summary (max 6 lines): matches found, matches analyzed, excluded, picks count, data problems, tool failures.
2. Picks table: match | market | settlement | my probability (range) | market probability | min odds | lineup status | one-line reason.
3. Coupon options.
4. Match cards (max 5 lines each): key facts, key risks, data gaps, news tier.
5. Excluded matches with the reason.
6. Step 0 report (tools and test results) and the full 10-item self-check checklist with pass/fail for each item (see below). Do not summarize it.
7. Short Arabic summary (max 5 lines).

### A1.10 Save before kickoff
Save to `picks_YYYY-MM-DD.json` and commit it BEFORE the first kickoff. Tell me the file path and commit id. Never edit it afterwards. If you change a pick later (A2), write a new file `picks_YYYY-MM-DD_v2.json` and keep the old one.

```json
{
  "date": "YYYY-MM-DD",
  "saved_at": "ISO-8601",
  "picks": [
    {
      "match": "Home vs Away",
      "kickoff": "ISO-8601",
      "market": "1x2_home",
      "settlement": "90min",
      "p_model": 0.0, "p_low": 0.0, "p_high": 0.0,
      "p_market_devig": 0.0,
      "odds_at_pick": 0.0, "odds_source": "name", "odds_time": "ISO-8601",
      "min_odds": 0.0,
      "lineup_status": "confirmed|expected|unknown",
      "reason": "one line, data-based",
      "tier": "safer|balanced|higher_risk"
    }
  ],
  "no_pick_matches": [{"match": "", "reason": ""}]
}
```

## A2 - PRE-KICKOFF RECHECK (run about 60-75 minutes before each kickoff)

1. Re-fetch confirmed lineups, last-minute injuries, and current odds.
2. Re-run model.py only if odds or inputs changed.
3. If a key player is out or lineup is heavily rotated, or odds moved so that `passes` is false or odds fall below min odds, CANCEL the pick and say why.
4. Record the price now as `odds_before_kickoff` in a new `_v2` file. Never overwrite the first file.

## SELF-CHECK (run before every answer; print the checklist with pass/fail)

1. Every probability was copied from model.py output, not typed by me.
2. Every FACT has a source and retrieval time.
3. Every pick has settlement basis, min odds, lineup status, and the "VERIFY at 1xbet" line.
4. No two accumulator legs are from the same match.
5. Odds older than 2 hours (by my retrieval time) are marked STALE and excluded; age-unverified odds are labeled and picks using them are PROVISIONAL.
6. Fixtures verified against 2 sources (teams, date, kickoff).
7. Each reason cites data, not narrative ("they want it more", "must win").
8. No pick rests on a RUMOR or a single unverified source.
9. Pick count is at most 4 and no pick was added to fill a coupon.
10. Nothing is claimed as done that was not actually run.

If an item fails, fix it or remove the pick. If it cannot be fixed, report the failure at the top of the answer.
