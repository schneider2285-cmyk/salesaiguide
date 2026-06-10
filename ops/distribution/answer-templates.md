# Community answer templates (cold-email wedge)

These are scaffolds, not copy-paste scripts. Communities ban obvious self-promo. The
point is a genuinely useful answer first; the link is optional and earns its place.
Rules: lead with help, disclose you run the site, link only when it is honestly the
best answer, and keep to roughly 1 link per 5 helpful replies. Log every reply in
`answer-tracker.csv`.

Use the UTM links from `python3 scripts/distribution_probe.py links` so GA4 attributes
the visit. The affiliate dashboard tracks the `/go/` click regardless.

## Template A: "Which cold email tool should I use?"
> For [their stated need: volume / budget / deliverability], the honest split is:
> - **Low/usage-based volume:** Woodpecker now bills ~$4 per 100 prospects contacted, so it is cheap if you send in bursts.
> - **Higher steady volume:** Saleshandy or Instantly tier by volume and come out cheaper per send at scale.
>
> What actually decides it for most people is [deliverability / inbox rotation / CRM sync], not the sticker price.
>
> (Full disclosure, I run a site that compares these. If it helps, here is the side-by-side with current pricing: [LINK to /compare/saleshandy-vs-woodpecker]. Happy to answer specifics here either way.)

## Template B: "X vs Y?" (e.g. Woodpecker vs Instantly)
> Used both. Short version: [X] wins on [concrete strength], [Y] wins on [concrete strength]. If you are [their situation], I would pick [X] because [specific reason]. If [other situation], [Y].
>
> I keep a current comparison with pricing here if you want the detail: [LINK]. Disclosure: it is my site.

## Template C: pure help, no link (do this most of the time)
> Answer the question fully and specifically with no link at all. This is what keeps you
> from being flagged and makes the occasional link credible. Log it as helpful=y, link_dropped=n.

## Do not
- Drop a bare `/go/` affiliate link (instant ban). Link content pages only.
- Post the same templated reply across threads. Each answer must address the specific question.
- Argue or astroturf. If a tool is not the best answer, say so.
