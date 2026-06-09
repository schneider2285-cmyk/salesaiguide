---
name: conversion-tracking-setup
description: PII-safe GA4 conversion tracking for outbound affiliate CTAs and newsletter signups, designed to coexist with the indexation gate. Use when instrumenting analytics events or fixing the GA4 PII leak.
triggers:
  - conversion tracking
  - GA4 events
  - affiliate click tracking
  - newsletter signup tracking
  - GA4 PII
---

# Conversion Tracking Setup

## When to use
Instrumenting or auditing GA4 events for monetizable actions, or removing PII from analytics.

## Constraints (from the architecture)
- The indexation gate bans `/go/` in `core-editorial`. You CANNOT route review-body CTAs through `/go/` to track them. Track DIRECT vendor links with click listeners that leave `href` unchanged.
- ButtonDown forms post cross-domain; capture the event client-side at submit.
- GA4 must never receive a raw email or other PII.

## Workflow
1. PII fix first: in `js/main.js`, change the `newsletter_signup` event to drop `email`, or send `email_sha256` only.
2. Add an `outbound_click` listener for anchors whose host is an external vendor domain (not internal, not `/go/`). Params: `dest_domain`, `page_path`, `cta_zone`. Do not modify `href`.
3. Keep the existing `affiliate_click` event for `/go/` links (the specs-cta and comparison links).
4. Add a `newsletter_signup` event to the ButtonDown form submit handlers.
5. Define the funnel and write it to `ops/data/revenue-funnel.json`.

## Guardrails
- No PII to GA4. No `/go/` added to `core-editorial`. No gate edits.

## Outputs
- A PII-safe GA4 layer that measures both direct and tracked outbound clicks and both newsletter systems.
