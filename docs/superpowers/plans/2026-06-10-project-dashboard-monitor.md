# Project Dashboard, Plan A (read-only monitor) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** A private, password-protected Next.js dashboard on Vercel that shows the project's live state (AROS team report, funnel, affiliate portfolio + queue, probe status), read-only.

**Architecture:** Next.js App Router app in a NEW repo `~/Downloads/salesaiguide-dashboard`. Middleware password-gates all routes (signed JWT cookie via `jose`, Edge-safe). Server components read the salesaiguide repo's committed JSON through the GitHub Contents API and render derived view models. No writes, no actions in this plan (that is Plan B). Deployed as its own Vercel project.

**Tech Stack:** Next.js (App Router, TypeScript), `jose` (JWT sessions), Vitest (unit tests). Node 20+.

**Spec:** `docs/superpowers/specs/2026-06-10-project-dashboard-design.md` (this is Plan A = spec build-order phases 1-2).

---

## File Structure (new repo `~/Downloads/salesaiguide-dashboard`)
- `lib/auth.ts` - JWT session create/verify + constant-time password check.
- `lib/github.ts` - read a repo file's JSON via the GitHub Contents API.
- `lib/derive.ts` - pure view-model builders from the raw JSON.
- `middleware.ts` - redirect unauthenticated requests to `/login`.
- `app/login/page.tsx`, `app/api/login/route.ts`, `app/api/logout/route.ts` - auth UI + endpoints.
- `app/page.tsx` + `components/*` - the dashboard views.
- `tests/*.test.ts` - Vitest unit tests for the lib modules.
- `.env.example`, `README.md`.

---

### Task 1: Scaffold the app + test runner

**Files:**
- Create: the repo `~/Downloads/salesaiguide-dashboard` (via create-next-app)
- Create: `vitest.config.ts`, `.env.example`

- [ ] **Step 1: Scaffold Next.js (TypeScript, App Router)**

Run:
```bash
cd ~/Downloads
npx create-next-app@latest salesaiguide-dashboard --ts --app --eslint --no-tailwind --no-src-dir --import-alias "@/*" --use-npm
cd salesaiguide-dashboard
npm install jose
npm install -D vitest
git init -q && git add -A && git commit -q -m "chore: scaffold next app"
```
Expected: a runnable Next app; `npm run dev` would serve on :3000.

- [ ] **Step 2: Add Vitest config and test script**

Create `vitest.config.ts` (the `resolve.alias` is required so tests can import `@/lib/...`):
```ts
import { defineConfig } from 'vitest/config';
import path from 'path';
export default defineConfig({
  test: { environment: 'node', include: ['tests/**/*.test.ts'] },
  resolve: { alias: { '@': path.resolve(process.cwd()) } },
});
```
In `package.json` `scripts`, add: `"test": "vitest run"`.

Create `.env.example`:
```
DASHBOARD_PASSWORD=change-me
SESSION_SECRET=generate-a-long-random-string
GITHUB_REPO=schneider2285-cmyk/salesaiguide
GITHUB_REF=redesign/nerdwallet-v1
DASHBOARD_GITHUB_TOKEN=
DASHBOARD_ACTIONS_ENABLED=false
```

- [ ] **Step 3: Smoke test the runner**

Create `tests/smoke.test.ts`:
```ts
import { it, expect } from 'vitest';
it('runner works', () => { expect(1 + 1).toBe(2); });
```
Run: `npm test`
Expected: 1 passed.

- [ ] **Step 4: Commit**
```bash
git add -A && git commit -m "chore: add vitest + env example"
```

---

### Task 2: Auth (JWT session + password check)

**Files:**
- Create: `lib/auth.ts`
- Test: `tests/auth.test.ts`

- [ ] **Step 1: Write the failing test**

Create `tests/auth.test.ts`:
```ts
import { it, expect } from 'vitest';
process.env.SESSION_SECRET = 'test-secret-test-secret-32bytes!!';
process.env.DASHBOARD_PASSWORD = 'hunter2';
import { createSession, verifySession, checkPassword, SESSION_COOKIE } from '@/lib/auth';

it('round-trips a session', async () => {
  const t = await createSession();
  expect(await verifySession(t)).toBe(true);
});
it('rejects undefined/garbage', async () => {
  expect(await verifySession(undefined)).toBe(false);
  expect(await verifySession('not.a.jwt')).toBe(false);
});
it('accepts the right password, rejects wrong', () => {
  expect(checkPassword('hunter2')).toBe(true);
  expect(checkPassword('nope')).toBe(false);
  expect(checkPassword('')).toBe(false);
});
it('exposes a cookie name', () => { expect(SESSION_COOKIE).toBe('sag_session'); });
```

- [ ] **Step 2: Run to verify it fails**

Run: `npm test`
Expected: FAIL (cannot resolve `@/lib/auth`).

- [ ] **Step 3: Implement**

Create `lib/auth.ts`:
```ts
import { SignJWT, jwtVerify } from 'jose';

export const SESSION_COOKIE = 'sag_session';

function secret(): Uint8Array {
  return new TextEncoder().encode(process.env.SESSION_SECRET || '');
}

export async function createSession(): Promise<string> {
  return new SignJWT({ ok: true })
    .setProtectedHeader({ alg: 'HS256' })
    .setIssuedAt()
    .setExpirationTime('7d')
    .sign(secret());
}

export async function verifySession(token?: string): Promise<boolean> {
  if (!token || !process.env.SESSION_SECRET) return false;
  try {
    await jwtVerify(token, secret());
    return true;
  } catch {
    return false;
  }
}

export function checkPassword(input: string): boolean {
  const pw = process.env.DASHBOARD_PASSWORD || '';
  if (!pw || input.length !== pw.length) return false;
  let diff = 0;
  for (let i = 0; i < pw.length; i++) diff |= input.charCodeAt(i) ^ pw.charCodeAt(i);
  return diff === 0;
}
```

- [ ] **Step 4: Run to verify it passes**

Run: `npm test`
Expected: PASS (smoke + 4 auth assertions).

- [ ] **Step 5: Commit**
```bash
git add lib/auth.ts tests/auth.test.ts && git commit -m "feat(auth): jwt session + constant-time password check"
```

---

### Task 3: Auth gate (middleware + login)

**Files:**
- Create: `middleware.ts`, `app/login/page.tsx`, `app/api/login/route.ts`, `app/api/logout/route.ts`

- [ ] **Step 1: Middleware**

Create `middleware.ts`:
```ts
import { NextRequest, NextResponse } from 'next/server';
import { verifySession, SESSION_COOKIE } from '@/lib/auth';

export async function middleware(req: NextRequest) {
  const { pathname } = req.nextUrl;
  if (pathname.startsWith('/login') || pathname.startsWith('/api/login') || pathname.startsWith('/api/logout')) {
    return NextResponse.next();
  }
  const ok = await verifySession(req.cookies.get(SESSION_COOKIE)?.value);
  if (!ok) {
    const url = req.nextUrl.clone();
    url.pathname = '/login';
    return NextResponse.redirect(url);
  }
  return NextResponse.next();
}

export const config = { matcher: ['/((?!_next/static|_next/image|favicon.ico).*)'] };
```

- [ ] **Step 2: Login route**

Create `app/api/login/route.ts`:
```ts
import { NextRequest, NextResponse } from 'next/server';
import { checkPassword, createSession, SESSION_COOKIE } from '@/lib/auth';

export async function POST(req: NextRequest) {
  const form = await req.formData();
  const password = String(form.get('password') || '');
  if (!checkPassword(password)) {
    return NextResponse.redirect(new URL('/login?error=1', req.url), { status: 303 });
  }
  const res = NextResponse.redirect(new URL('/', req.url), { status: 303 });
  res.cookies.set(SESSION_COOKIE, await createSession(), {
    httpOnly: true, secure: true, sameSite: 'lax', path: '/', maxAge: 60 * 60 * 24 * 7,
  });
  return res;
}
```

Create `app/api/logout/route.ts`:
```ts
import { NextRequest, NextResponse } from 'next/server';
import { SESSION_COOKIE } from '@/lib/auth';

export async function POST(req: NextRequest) {
  const res = NextResponse.redirect(new URL('/login', req.url), { status: 303 });
  res.cookies.set(SESSION_COOKIE, '', { path: '/', maxAge: 0 });
  return res;
}
```

- [ ] **Step 3: Login page**

Create `app/login/page.tsx`:
```tsx
export default function Login({ searchParams }: { searchParams: { error?: string } }) {
  return (
    <main style={{ maxWidth: 360, margin: '15vh auto', fontFamily: 'system-ui' }}>
      <h1>SalesAIGuide</h1>
      <form method="post" action="/api/login">
        <input name="password" type="password" placeholder="Password" autoFocus
               style={{ width: '100%', padding: 10, fontSize: 16 }} />
        {searchParams?.error ? <p style={{ color: 'crimson' }}>Wrong password</p> : null}
        <button type="submit" style={{ marginTop: 10, padding: '10px 16px' }}>Enter</button>
      </form>
    </main>
  );
}
```

- [ ] **Step 4: Verify the gate locally**

Run: `DASHBOARD_PASSWORD=hunter2 SESSION_SECRET=test-secret-test-secret-32bytes!! npm run dev` then in another shell:
```bash
curl -sI localhost:3000/ | grep -i location   # expect redirect to /login
```
Expected: `location: /login` (unauthenticated requests are redirected).

- [ ] **Step 5: Commit**
```bash
git add middleware.ts app/login app/api && git commit -m "feat(auth): middleware gate + login/logout"
```

---

### Task 4: GitHub read client

**Files:**
- Create: `lib/github.ts`
- Test: `tests/github.test.ts`

- [ ] **Step 1: Write the failing test**

Create `tests/github.test.ts`:
```ts
import { it, expect, vi, beforeEach } from 'vitest';
process.env.DASHBOARD_GITHUB_TOKEN = 'tok';
process.env.GITHUB_REPO = 'owner/repo';
import { readJson, hasToken } from '@/lib/github';

beforeEach(() => { vi.restoreAllMocks(); });

it('hasToken reflects env', () => { expect(hasToken()).toBe(true); });

it('decodes base64 content to JSON', async () => {
  const content = Buffer.from(JSON.stringify({ a: 1 })).toString('base64');
  global.fetch = vi.fn().mockResolvedValue({ ok: true, json: async () => ({ content }) }) as any;
  expect(await readJson('x.json')).toEqual({ a: 1 });
});

it('throws on non-ok', async () => {
  global.fetch = vi.fn().mockResolvedValue({ ok: false, status: 404 }) as any;
  await expect(readJson('missing.json')).rejects.toThrow('GitHub 404');
});
```

- [ ] **Step 2: Run to verify it fails**

Run: `npm test`
Expected: FAIL (cannot resolve `@/lib/github`).

- [ ] **Step 3: Implement**

Create `lib/github.ts`:
```ts
function repo(): string { return process.env.GITHUB_REPO || 'schneider2285-cmyk/salesaiguide'; }
function ref(): string { return process.env.GITHUB_REF || 'redesign/nerdwallet-v1'; }
function token(): string { return process.env.DASHBOARD_GITHUB_TOKEN || ''; }

export function hasToken(): boolean { return Boolean(token()); }

export async function readJson(path: string): Promise<any> {
  const url = `https://api.github.com/repos/${repo()}/contents/${path}?ref=${encodeURIComponent(ref())}`;
  const res = await fetch(url, {
    headers: { Authorization: `Bearer ${token()}`, Accept: 'application/vnd.github+json' },
    cache: 'no-store',
  });
  if (!res.ok) throw new Error(`GitHub ${res.status} for ${path}`);
  const data = await res.json();
  const decoded = Buffer.from(data.content, 'base64').toString('utf8');
  return JSON.parse(decoded);
}
```

- [ ] **Step 4: Run to verify it passes**

Run: `npm test`
Expected: PASS.

- [ ] **Step 5: Commit**
```bash
git add lib/github.ts tests/github.test.ts && git commit -m "feat(github): read repo json via contents api"
```

---

### Task 5: Derive view models (pure)

**Files:**
- Create: `lib/derive.ts`
- Test: `tests/derive.test.ts`

- [ ] **Step 1: Write the failing test**

Create `tests/derive.test.ts`:
```ts
import { it, expect } from 'vitest';
import { funnelView, counts, queueRows, affiliateRows } from '@/lib/derive';

const links = { links: { a: { status: 'live', network: 'x' }, b: { status: 'placeholder' }, c: { status: 'placeholder' } } };
const funnel = {
  lastUpdated: '2026-06-09',
  summary: { monetizableSurfaces: 1914, trackingCoveragePercent: 100, liveProgramCoveragePercent: 11.2 },
  slugCoverage: { a: { monetizableSurfaces: 75 }, b: { monetizableSurfaces: 108 }, c: { monetizableSurfaces: 5 } },
};
const pipeline = { pipeline: {} };

it('funnelView pulls summary', () => {
  expect(funnelView(funnel)).toMatchObject({ monetizableSurfaces: 1914, liveProgramCoveragePercent: 11.2, lastUpdated: '2026-06-09' });
});
it('counts total/live/placeholder', () => { expect(counts(links)).toEqual({ total: 3, live: 1, placeholder: 2 }); });
it('queue excludes live, sorts by surfaces desc', () => { expect(queueRows(links, funnel).map(r => r.slug)).toEqual(['b', 'c']); });
it('affiliate rows are live-first', () => { expect(affiliateRows(links, funnel, pipeline)[0].status).toBe('live'); });
```

- [ ] **Step 2: Run to verify it fails**

Run: `npm test`
Expected: FAIL (cannot resolve `@/lib/derive`).

- [ ] **Step 3: Implement**

Create `lib/derive.ts`:
```ts
export function funnelView(funnel: any) {
  const s = funnel?.summary || {};
  return {
    monetizableSurfaces: s.monetizableSurfaces ?? 0,
    trackingCoveragePercent: s.trackingCoveragePercent ?? 0,
    liveProgramCoveragePercent: s.liveProgramCoveragePercent ?? 0,
    lastUpdated: funnel?.lastUpdated ?? null,
  };
}

export function counts(links: any) {
  const L = links?.links || {};
  const total = Object.keys(L).length;
  const live = Object.values(L).filter((m: any) => m?.status === 'live').length;
  return { total, live, placeholder: total - live };
}

export function queueRows(links: any, funnel: any) {
  const cov = funnel?.slugCoverage || {};
  const L = links?.links || {};
  return Object.entries(L)
    .filter(([, m]: any) => m?.status !== 'live')
    .map(([slug]: any) => ({ slug, surfaces: cov[slug]?.monetizableSurfaces ?? 0 }))
    .sort((x, y) => y.surfaces - x.surfaces);
}

export function affiliateRows(links: any, funnel: any, pipeline: any) {
  const cov = funnel?.slugCoverage || {};
  const pl = pipeline?.pipeline || {};
  const L = links?.links || {};
  const rows = Object.entries(L).map(([slug, m]: any) => ({
    slug,
    status: m?.status || 'placeholder',
    stage: m?.status === 'live' ? 'live' : (pl[slug]?.stage || 'not_started'),
    network: m?.network || '',
    surfaces: cov[slug]?.monetizableSurfaces ?? 0,
  }));
  rows.sort((a, b) => (a.status !== 'live' ? 1 : 0) - (b.status !== 'live' ? 1 : 0) || b.surfaces - a.surfaces);
  return rows;
}
```

- [ ] **Step 4: Run to verify it passes**

Run: `npm test`
Expected: PASS (all suites).

- [ ] **Step 5: Commit**
```bash
git add lib/derive.ts tests/derive.test.ts && git commit -m "feat(derive): view models from repo json"
```

---

### Task 6: Dashboard page + views

**Files:**
- Create: `app/page.tsx`, `components/Dashboard.tsx`

- [ ] **Step 1: Implement the server page**

Create `app/page.tsx`:
```tsx
import { readJson, hasToken } from '@/lib/github';
import { funnelView, counts, queueRows, affiliateRows } from '@/lib/derive';
import Dashboard from '@/components/Dashboard';

export const dynamic = 'force-dynamic';

export default async function Home() {
  if (!hasToken()) {
    return <main style={{ fontFamily: 'system-ui', padding: 24 }}>
      <h1>Configure token</h1>
      <p>Set <code>DASHBOARD_GITHUB_TOKEN</code> in Vercel to load project data.</p>
    </main>;
  }
  try {
    const [funnel, links, pipeline, probe] = await Promise.all([
      readJson('ops/data/revenue-funnel.json'),
      readJson('affiliate-links.json'),
      readJson('ops/data/affiliate-pipeline.json'),
      readJson('ops/distribution/probe-config.json'),
    ]);
    return <Dashboard
      funnel={funnelView(funnel)}
      counts={counts(links)}
      queue={queueRows(links, funnel).slice(0, 10)}
      rows={affiliateRows(links, funnel, pipeline)}
      probe={{ wedge: probe?.wedge, targets: (probe?.targets || []).length, channels: (probe?.channels || []).length }}
    />;
  } catch (e: any) {
    return <main style={{ fontFamily: 'system-ui', padding: 24 }}>
      <h1>Load error</h1><pre>{String(e?.message || e)}</pre>
    </main>;
  }
}
```

- [ ] **Step 2: Implement the view component**

Create `components/Dashboard.tsx`:
```tsx
export default function Dashboard({ funnel, counts, queue, rows, probe }: any) {
  const card: React.CSSProperties = { border: '1px solid #ddd', borderRadius: 8, padding: 16, margin: '12px 0' };
  return (
    <main style={{ fontFamily: 'system-ui', maxWidth: 880, margin: '0 auto', padding: 24 }}>
      <header style={{ display: 'flex', justifyContent: 'space-between' }}>
        <h1>SalesAIGuide control</h1>
        <form method="post" action="/api/logout"><button>Log out</button></form>
      </header>

      <section style={card}>
        <h2>Revenue funnel</h2>
        <p>{funnel.monetizableSurfaces} monetizable surfaces, {funnel.trackingCoveragePercent}% tracked,
           <b> {funnel.liveProgramCoveragePercent}%</b> point at a live program.</p>
        <small>funnel updated {funnel.lastUpdated}</small>
      </section>

      <section style={card}>
        <h2>Affiliate portfolio</h2>
        <p>{counts.total} programs, {counts.live} live, {counts.placeholder} placeholder.</p>
        <h3>Top activation targets</h3>
        <ol>{queue.map((q: any) => <li key={q.slug}>{q.slug} ({q.surfaces} surfaces)</li>)}</ol>
      </section>

      <section style={card}>
        <h2>Distribution probe</h2>
        <p>wedge: {probe.wedge}; {probe.targets} targets, {probe.channels} channels.</p>
      </section>

      <section style={card}>
        <h2>All programs</h2>
        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 14 }}>
          <thead><tr><th align="left">slug</th><th>status</th><th>network</th><th>surfaces</th></tr></thead>
          <tbody>{rows.map((r: any) => (
            <tr key={r.slug} style={{ borderTop: '1px solid #eee' }}>
              <td>{r.slug}</td><td align="center">{r.status}</td><td align="center">{r.network || '-'}</td><td align="center">{r.surfaces}</td>
            </tr>))}</tbody>
        </table>
      </section>
    </main>
  );
}
```

- [ ] **Step 3: Verify locally with a real read**

Set a fine-grained GitHub token (contents:read on the salesaiguide repo) in your shell, then:
```bash
DASHBOARD_PASSWORD=hunter2 SESSION_SECRET=test-secret-test-secret-32bytes!! \
  GITHUB_REPO=schneider2285-cmyk/salesaiguide GITHUB_REF=redesign/nerdwallet-v1 \
  DASHBOARD_GITHUB_TOKEN=ghp_xxx npm run dev
```
Log in at localhost:3000 with the password; expect the four cards to render real numbers (49 programs / 4 live, 1914 surfaces / 11.2%, the queue, the probe wedge).
Run `npm test` again: expect all suites still pass (no logic changed).

- [ ] **Step 4: Commit**
```bash
git add app/page.tsx components/Dashboard.tsx && git commit -m "feat(dashboard): monitor views"
```

---

### Task 7: Deploy to Vercel

**Files:**
- Create: `README.md` (run + deploy notes)

- [ ] **Step 1: Push the repo to GitHub**
```bash
gh repo create salesaiguide-dashboard --private --source=. --remote=origin --push
```

- [ ] **Step 2: Create the Vercel project and set env**

Link the project: `npx vercel link --yes`.

Then set these for Production + Preview, either in the Vercel dashboard (Settings -> Environment Variables) or via `vercel env add <NAME>` (it prompts for the value and target environments):
- `DASHBOARD_PASSWORD` = a strong password
- `SESSION_SECRET` = a long random string
- `GITHUB_REPO` = `schneider2285-cmyk/salesaiguide`
- `GITHUB_REF` = `redesign/nerdwallet-v1`
- `DASHBOARD_GITHUB_TOKEN` = a fine-grained PAT, `contents:read` on that one repo

Then deploy a preview: `npx vercel`.

- [ ] **Step 3: Verify the live deploy**

Open the preview URL. Expect: the password gate appears; wrong password is rejected; correct password loads the dashboard with real numbers. Confirm an unauthenticated `curl -sI <url>/` redirects to `/login`.

- [ ] **Step 4: Write README + commit**

Create `README.md` documenting the env vars (point at `.env.example`), the read-only scope, and that controls are a follow-up (Plan B). Then:
```bash
git add README.md && git commit -m "docs: dashboard readme" && git push
```

---

## Verification Checklist (end state of Plan A)
- `npm test` green (smoke, auth, github, derive).
- Local `npm run dev`: unauthenticated -> /login; correct password -> dashboard with real numbers (49/4 programs, 1914 surfaces, 11.2%).
- Deployed on Vercel behind the password; env vars set; `DASHBOARD_GITHUB_TOKEN` is a single-repo `contents:read` fine-grained PAT.
- No writes, no actions, no Netlify token anywhere.

## Plan B (follow-up, not this plan)
The guarded controls: add `.github/workflows/activate-program.yml` and `deploy-prod.yml` to the salesaiguide repo, add `lib/dispatch.ts` + `/api/activate` + `/api/deploy` to the dashboard (gated by `DASHBOARD_ACTIONS_ENABLED`), and the buttons. Token gains `actions:write`. Each action runs the existing guard chain in CI.
