# SalesAIGuide — Standards & Quality Rules

## Output Formats

### HTML Pages
- UTF-8 encoding, `lang="en"`
- Must pass basic HTML validation (no unclosed tags)
- Every page includes: nav, main content, footer
- Mobile responsive at 768px breakpoint

### Commit Messages
```
<type>(<scope>): <description>

<optional body>

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>
```

Types: `feat`, `fix`, `docs`, `chore`, `refactor`
Scopes: `compare`, `tools`, `categories`, `blog`, `seo`, `auto`, `deploy`

### Agent Reports
All agent outputs follow this format:
```markdown
## [Agent Name] Report — [Date]

### Summary
[1-2 sentence overview]

### Details
[Specifics of what was done/found]

### Files Changed
- [file list]

### Issues
- [any problems encountered]
```

## Quality Rules

### SEO Requirements (every page)
- [ ] Unique `<title>` under 60 characters
- [ ] Unique `<meta name="description">` 150-160 characters
- [ ] `<link rel="canonical">` with full URL
- [ ] Open Graph tags (og:title, og:description, og:url, og:site_name, og:type)
- [ ] Twitter Card tags (twitter:card, twitter:title, twitter:description)
- [ ] `<link rel="icon" href="/favicon.svg" type="image/svg+xml">`
- [ ] JSON-LD structured data (Article, CollectionPage, WebPage, or WebSite)
- [ ] Entry in `sitemap.xml`

### Design Consistency
- [ ] Uses `css/main.css` (all pages) and `css/review.css` (comparison/review pages)
- [ ] Nav matches site-wide template (5 links: Home, Tools, Compare, Categories, About)
- [ ] Hamburger menu works on mobile
- [ ] Footer matches site-wide template (Quick Links + Company columns)
- [ ] Colors from design system only (no arbitrary hex values)

### Affiliate Links
- [ ] ALL tool links use `/go/[slug]` pattern
- [ ] NEVER hardcode partner URLs in HTML pages
- [ ] CTAs have `target="_blank" rel="nofollow noopener"`
- [ ] Each tool slug has a matching entry in `_redirects`

### Content Quality
- [ ] No placeholder text in published pages
- [ ] Tool data is factual (G2 ratings, pricing match public sources)
- [ ] Comparison verdicts are balanced (acknowledge both tools' strengths)
- [ ] Every comparison has actionable recommendation ("Choose X if..., Choose Y if...")
- [ ] Pricing displayed prominently
- [ ] "Updated [Month] [Year]" date badge present

### Security
- [ ] No API tokens, passwords, or secrets in committed files
- [ ] No user personal data in committed files
- [ ] `_redirects` doesn't expose internal infrastructure
- [ ] No inline `<script>` that could be XSS vectors (except structured data)

## Naming Conventions

| Entity | Format | Example |
|--------|--------|---------|
| HTML files | lowercase-kebab-case | `clay-vs-apollo.html` |
| Tool slugs | lowercase-kebab-case | `chili-piper` |
| Category slugs | lowercase-kebab-case | `conversation-intelligence` |
| CSS classes | lowercase-kebab-case | `.compare-card` |
| Commit messages | conventional commits | `feat(compare): add new comparison` |
| Agent files | lowercase-kebab-case.md | `seo-auditor.md` |
| Task IDs | TASK-NNN / DONE-NNN / PLAN-NNN | `TASK-001` |

## Definition of Done

A page is "done" when it:
1. Renders correctly at desktop (1280px) and mobile (375px)
2. Passes all SEO requirements above
3. Has working navigation (all links resolve)
4. Has at least 2 affiliate CTAs (for comparison/review pages)
5. Is listed in `sitemap.xml`
6. Is committed and pushed to `main`
