# SalesAIGuide NerdWallet Redesign Spec

## Design Tokens

### Fonts
- Font: Inter (Google Fonts) — weights 400, 500, 600, 700, 800
- Preconnect to fonts.googleapis.com and fonts.gstatic.com

### Colors (Light Mode)
- Background: #ffffff
- Surface: #f8fafb
- Surface 2: #f0f4f6
- Text primary: #1a1a2e
- Text muted: #6b7280
- Text faint: #9ca3af
- Accent (utility green): #0d7c66
- Accent hover: #0a6352
- Accent active: #084f41
- Accent highlight: #d1fae5
- Border: #e5e7eb
- Star yellow: #f59e0b
- Success badge bg: #dcfce7 / text: #166534
- Warning badge bg: #fef3c7 / text: #92400e

### Colors (Dark Mode)
- Background: #0f1117
- Surface: #161b22
- Surface 2: #1c2128
- Text: #e6edf3
- Text muted: #8b949e
- Accent: #2dd4a8
- Border: #2d333b

### Type Scale (clamp-based, fluid)
- --text-xs: clamp(0.75rem, 0.7rem + 0.25vw, 0.8125rem)
- --text-sm: clamp(0.8125rem, 0.75rem + 0.3vw, 0.9375rem)
- --text-base: clamp(0.9375rem, 0.85rem + 0.4vw, 1.0625rem)
- --text-lg: clamp(1.125rem, 0.95rem + 0.85vw, 1.4rem)
- --text-xl: clamp(1.4rem, 1rem + 1.4vw, 2rem)
- --text-2xl: clamp(1.8rem, 1.1rem + 2.2vw, 3rem)

### Spacing (4px grid)
- --space-1: 0.25rem through --space-24: 6rem

### Radius
- sm: 0.375rem, md: 0.5rem, lg: 0.75rem, xl: 1rem, full: 9999px

### Shadows
- sm: 0 1px 3px rgba(26,26,46,0.06)
- md: 0 4px 12px rgba(26,26,46,0.08)
- lg: 0 12px 32px rgba(26,26,46,0.10)

### Transitions
- Interactive: 180ms cubic-bezier(0.16, 1, 0.3, 1)

## Component Patterns

### Navbar
- White bg, sticky, blur backdrop on scroll
- Logo: SVG icon (green rounded rect with signal path) + "SalesAIGuide" in Inter 700
- Nav: Tools, Compare, Categories, About — Inter 500, 13px
- Right: search input (pill-shaped) + dark mode toggle
- Mobile: hamburger → slide-out drawer

### Tool Card (Homepage)
- 3-column grid on desktop, 1-column on mobile
- Each card: rank badge (#1/#2/#3), "Best For" colored tag, tool name, star rating, price prominent, 3 bullet features, green "Try Free →" CTA, "Read Full Review →" text link
- Compare checkbox on each card
- Hover: shadow increase (180ms ease)

### Category Tabs (Homepage Hero)
- Horizontal row of pill buttons with emoji icons
- Active: green fill, white text
- Inactive: outlined, gray border
- JS tab switching shows/hides tool panels below

### Comparison Card
- Tool A | VS | Tool B layout
- One-line verdict
- "See Full Comparison →" link
- 3x2 grid on desktop, 1-column on mobile

### Tool Review Page Template
- Left sidebar TOC (sticky)
- Main content: hero with tool name, verdict, rating, price
- Sections: Overview, Key Features, Pricing, Pros & Cons, Who It's For, Verdict
- Right sidebar: quick specs card (sticky)
- Affiliate CTA buttons throughout

### Comparison Page Template
- Side-by-side layout (2-column on desktop)
- Header: Tool A vs Tool B with ratings
- Comparison table: Feature rows with check/x marks
- Verdict section at bottom with recommendation
- Affiliate CTAs for both tools

### Category Page Template
- Category name + description
- Ranked list of tools (same card format as homepage)
- Methodology sidebar

### Footer
- Dark surface, 4-column layout
- Logo + tagline, Top Tools links, Categories links, Site links
- Disclosure text, copyright

### Sticky Compare Bar
- Fixed bottom bar, shows when tools are checked
- 3 slots, "Compare Now →" button
