# AROS Required Secrets

No real credentials live in the repo. Set these in the appropriate store. Every value shown below is a PLACEHOLDER.

| Secret | Used by | Set in | Notes |
|--------|---------|--------|-------|
| `GA4_MEASUREMENT_ID` | Revenue Analyst | client HTML (public) | Not secret. Currently `G-VRBZ6Z6885`. Public by design. |
| `GA4_API_SECRET` | Revenue Analyst | Netlify env / GitHub secret | Measurement Protocol secret for server-side events. SECRET. |
| `BEEHIIV_API_KEY` | subscribe function | Netlify env | Already referenced by `netlify/functions/subscribe.js`. SECRET. |
| `BEEHIIV_PUBLICATION_ID` | subscribe function | Netlify env | Publication id `pub_...`. |
| `BUTTONDOWN_API_KEY` | Revenue Analyst | Netlify env | Only if server-side signup mirroring is added. SECRET. |
| `NETLIFY_AUTH_TOKEN` | deploy / CI | GitHub Actions secret | Already configured for CI. SECRET. |
| `NETLIFY_SITE_ID` | deploy / CI | GitHub Actions secret | `c79f346d-...`. |
| `PARTNERSTACK_API_KEY` | Monetization adapter | Netlify env / local .env | Optional, per network adapter. SECRET. |
| `REWARDFUL_API_SECRET` | Monetization adapter | Netlify env / local .env | Optional. SECRET. |
| `FIRSTPROMOTER_API_KEY` | Monetization adapter | Netlify env / local .env | Optional. SECRET. |
| `IMPACT_ACCOUNT_SID` / `IMPACT_AUTH_TOKEN` | Monetization adapter | Netlify env / local .env | Optional. SECRET. |

## Local development

Copy the block below into a local `.env` (never commit real values). Production secrets belong in Netlify env and GitHub Actions secrets, not in `.env`.

```
GA4_MEASUREMENT_ID=G-VRBZ6Z6885
GA4_API_SECRET=__set_me__
BEEHIIV_API_KEY=__set_me__
BEEHIIV_PUBLICATION_ID=__set_me__
BUTTONDOWN_API_KEY=__set_me__
PARTNERSTACK_API_KEY=__set_me__
REWARDFUL_API_SECRET=__set_me__
FIRSTPROMOTER_API_KEY=__set_me__
IMPACT_ACCOUNT_SID=__set_me__
IMPACT_AUTH_TOKEN=__set_me__
```

Security note: `.env*` is NOT currently in `.gitignore`. Add `.env` to `.gitignore` (a Growth Engineer task) BEFORE creating any local `.env` with real values, or a secret could be committed.
