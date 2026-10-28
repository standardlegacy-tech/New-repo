# PHASE B - Post-Match Review (after matches finish)

How to run me: "Run phase_b.md for date YYYY-MM-DD".

## STEP 0 - CAPABILITY CHECK (report real output)

Confirm which tools you have (web search, code sandbox, files/GitHub). If you cannot read the saved picks file or fetch results, STOP and say so. Never claim to have checked a result you did not retrieve.

## HONESTY RULES

- Use ONLY the saved `picks_YYYY-MM-DD.json` (and `_v2` if it exists). Never rewrite, "remember", or improve the original picks.
- Every result needs a named source and retrieval time. No source = "result unverified", and the pick stays unsettled.
- Label claims FACT / CALC / JUDGMENT.
- Do not explain a loss with a story that sounds good. Each cause needs evidence (a lineup change, an event in the match, a number from the file). If there is no evidence, write "cause unknown".
- One day is noise. Do not change the method because of a single result.

## B1 - LOAD

Load `picks_YYYY-MM-DD.json` and `picks_YYYY-MM-DD_v2.json` if present. Report: number of picks, number cancelled in v2 and why. If the file is missing, STOP.

## B2 - RESULTS

For every picked match fetch from a named source: final score, half-time score, red cards, penalties, and whether it finished normally (postponed/abandoned = VOID candidate, check market rules). Show a table with source.

## B3 - SETTLEMENT

For each pick: result (WON / LOST / VOID / UNSETTLED), settlement basis used (`90min` etc.), the probability I gave (`p_model`, `p_low`..`p_high`), and the odds taken (`odds_at_pick`).
Note: I place bets at 1xbet myself; this review uses the odds in the file. If I give you my actual odds, use them and label them USER-REPORTED.

## B4 - CAUSE ANALYSIS (every LOST pick; WON picks too)

Classify each LOST pick into exactly one primary cause:
- (a) VARIANCE: sound pick, normal bad outcome (for example a pick at 65% loses about 1 time in 3).
- (b) MODEL ERROR: inputs or assumptions were wrong (wrong league averages, ignored opponent strength, small sample).
- (c) MISSED INFORMATION: lineup, injury, news, or rotation that existed before kickoff and was not used. Give the source and time it was available.
- (d) DATA PROBLEM: wrong team/date, stale odds, mislabeled source.
- (e) MARKET WAS RIGHT: the model disagreed with the market and was wrong.
- (f) MATCH EVENT: early red card, penalty, or injury that changed the match; the pick was reasonable before it.
- (g) UNKNOWN: no evidence for any cause.
For each WON pick, check whether it won for the reasons given. A pick that won for the wrong reason counts as luck, not skill.
Do not use hindsight to call a pick "obvious".

## B5 - LOGGING

Append one row per pick to `results_log.csv` (create it with a header if missing):

`date,match,market,settlement,p_model,p_low,p_high,p_market_devig,odds_at_pick,odds_before_kickoff,odds_closing,result,cause_class`

- `odds_closing`: the last available price before kickoff from a named source; if unavailable, "no data".
- Commit the file.

## B6 - RUNNING STATISTICS (compute in code, show the output)

Over all rows in `results_log.csv`, report:
1. Number of picks settled, hit rate.
2. Calibration: average `p_model` vs actual hit rate. Also by buckets (below 50%, 50-65%, above 65%) when there are 20+ picks in a bucket.
3. Average of `odds_at_pick / odds_closing - 1` (closing line value). Positive on average over 100+ picks is evidence of a real edge; negative means the picks are not beating the market.
4. Cause class counts.
5. Flat-stake profit/loss per 1 unit (a descriptive number only; no staking advice).
Always state the sample size. Under 100 settled picks: "inconclusive, no conclusions about skill".

## B7 - LESSONS

Give at most 3 lessons, and only when the same cause appears in at least 3 picks or on at least 2 different days. Otherwise write "no lesson yet". Propose changes to settings (for example the market weight, the exclusion rules, the rho in model.py) as SUGGESTIONS with the evidence. Do not apply them yourself; I decide.

## B8 - OUTPUT FORMAT (short)

1. Day summary (max 5 lines): picks, won, lost, void, unsettled.
2. Results table: match | market | result | p given | odds | cause class | evidence (one line).
3. Running statistics block.
4. Lessons (or "no lesson yet").
5. Self-check checklist.
6. Short Arabic summary (max 5 lines).

## SELF-CHECK (print with pass/fail)

1. I used only the saved picks file and did not alter it.
2. Every result has a named source and time.
3. Every cause class has evidence, or is "unknown".
4. No VOID/UNSETTLED pick was counted as won or lost.
5. Statistics were computed in code and the output is shown.
6. Sample size is stated next to every statistic.
7. No lesson comes from fewer than 3 picks or 2 days.
8. No method change was applied; only suggested.
9. Nothing is claimed as done that was not actually run.
