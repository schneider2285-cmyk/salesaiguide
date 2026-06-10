# Distribution Probe (runbook)

The single highest-value test for this site: can the content plus manual community
distribution move any money at all? This folder is the runnable harness for the 2-week
probe. Strategy and the honest diagnosis are in `docs/marketing/distribution-plan.md`;
this README is how to execute and decide.

What this is NOT: it sends no email, runs no bot, and connects no credentials. The
operator does the outreach by hand. The tooling exists to make traffic attributable and
the decision mechanical.

## The wedge
Cold-email tools only. Two of the four live affiliate programs are here (Woodpecker,
Saleshandy), so clicks can earn this week. Be THE helpful cold-email voice in 2-3
communities rather than spreading thin.

## Files
- `probe-config.json`: targets, channels, UTM scheme, and the PRE-COMMITTED decision rule.
- `answer-templates.md`: how to answer helpfully without getting banned.
- `answer-tracker.template.csv`: copy to `answer-tracker.csv` and log every reply.
- `../../scripts/distribution_probe.py`: `validate`, `links`, `score`.
- `../../scripts/test_distribution_probe.py`: tests the decision rule.

## Run it
```bash
# 1. sanity-check the config and that every target page exists
python3 scripts/distribution_probe.py validate

# 2. generate UTM links to paste (GA4 will attribute these; /go/ clicks track regardless)
python3 scripts/distribution_probe.py links

# 3. copy the tracker, then log replies daily
cp ops/distribution/answer-tracker.template.csv ops/distribution/answer-tracker.csv

# 4. at the end of week 2, fill clicks/signups from the Woodpecker + Saleshandy
#    dashboards and qualified_visits from GA4, then get the verdict
python3 scripts/distribution_probe.py score --results ops/distribution/answer-tracker.csv
```

## Daily cadence (2 weeks)
3 to 5 genuinely helpful answers per day in r/cold_email, r/Emailmarketing, r/sales, and
Quora. Disclose you run the site. Link a comparison only when it is honestly the best
answer, roughly 1 link per 5 helpful replies. Log each one.

## The decision (committed up front, do not move it)
At the end of two weeks `score` applies the rule in `probe-config.json`:
- **COMMIT**: a signup, or >= 10 clicks with >= 15 qualified visits. Real demand exists;
  build the cold-email cost calculator and run the 60-90 day push (plan Tier 1+2).
- **STOP**: ~0 clicks (<= 2) and 0 signups after honest effort. Stop investing time; sign
  up for the Tier-1 programs so any future trickle still earns, and let the site run as a
  lottery ticket.
- **CONTINUE**: some signal but below the bar. Iterate messaging/targeting once.
- **INSUFFICIENT_EFFORT**: fewer than 30 helpful answers logged. The probe was not run;
  finish it before deciding.

## Honest caveats
- This tests ONE channel (community answering) for ONE wedge. A STOP means this channel
  did not work, not that the site is hopeless; the plan's Tier 3 covers narrow/pivot/sunset.
- If a community strips UTM params, GA4 session attribution drops but the affiliate
  dashboards still capture the `/go/` clicks (the primary measure). Decision still holds.
- Effort honesty matters: the rule refuses to declare STOP on a half-run probe.
