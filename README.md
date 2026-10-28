# football-agent

Daily football analysis workflow for an agent.

- `model.py`      fixed calculator (do not edit)
- `phase_a.md`    morning scan and pre-kickoff recheck
- `phase_b.md`    post-match review
- `results_log.csv` running log (header only; the agent appends rows)
- `picks_YYYY-MM-DD.json` created by the agent each day (first one: `picks_2026-10-28.json`)

Rules: picks files are saved and committed before kickoff and never edited afterwards.
Changes go in a new `_v2` file.
