# emmadarling.dev revamp — build plan (15 Sep 2026)

Rules live in `CLAUDE.md`. This file is *what* to build, in order. Tick each box only after the branch preview has been checked on a phone.

Locked direction: **B rail + C monogram hero + A rhythm.** Playfair 600 headings, DM Sans body. Eucalyptus `#3A6357` on cream. Gold never as text on cream. Light mode = cream page, teal hero, teal Make band.

---

## M0 — Branch and safety net
- [ ] `git checkout -b revamp` from an up-to-date `main`
- [ ] Netlify → Site configuration → Build & deploy → Branch deploys → add `revamp`
- [ ] Screenshot the current live site (desktop + phone) → save to `Promptwrought-Private/` as the "before"
- [ ] Copy `CLAUDE.md` and `BUILD-PLAN.md` into the repo root
- Commit: `chore: revamp branch, CLAUDE.md, build plan`

## M1 — Design tokens
- [ ] `:root` block: colours (teal, gold, cream, eucalyptus, aubergine, lavender), fluid type scale with `clamp()`, spacing scale, radii, shadows, `--ease`
- [ ] `[data-theme="light"]` override set
- [ ] Nothing hard-coded below `:root`
- Commit: `feat: design tokens`

## M2 — Skeleton and the column fix
- [ ] Semantic structure per `CLAUDE.md`; rough content is fine
- [ ] Every `<section>` full-bleed and coloured; `.container` inside with no background
- [ ] Check at 1440 and 390: the aubergine column is gone
- Commit: `feat: page skeleton, full-bleed sections`

## M3 — Typography and rhythm
- [ ] Playfair Display 600 on `h1`/`h2`; DM Sans body 17–19px, lh 1.6–1.7, ~68ch
- [ ] Cormorant italic on the one pull-quote only
- [ ] Vertical rhythm from the spacing scale
- Commit: `feat: typography`

## M4 — The monogram + rail
- [ ] EMA as inline SVG paths (not an image), `<title>` inside
- [ ] Large gold monogram in the hero (direction C)
- [ ] Sticky rail: three letters E · M · A as anchor links; active letter in gold; no descriptor text
- [ ] Draw-in animation on load, letters draw in E → M → A
- Commit: `feat: monogram hero and rail nav`

## M5 — Motion system
- [ ] One `IntersectionObserver`, reveal once, stagger via `transition-delay`
- [ ] Link underlines draw in from the left; 
- [ ] Links: colour via a `--link` token (gold in dark, eucalyptus in light), no underline at rest, underline draws in on hover — "handfinish" is the test case 
- [ ] project cards lift with a gold hairline on hover
- [ ] `prefers-reduced-motion` collapses everything
- Commit: `feat: scroll reveals`

## M6 — Make: data-driven project grid
- [ ] `projects` array → cards. Featured (larger): Parkgate, Verbarium, Bank-a-Win. Tight row: Forecast, Lingua Daily, Pagine, Tip Calculator
- [ ] teal band in light mode; glass panels (`backdrop-filter: blur`) on teal
- Commit: `feat: project grid from data`
- [ ] Check aubergine meta text on cream against the teal; if it clashes, `--text-muted` and `--label` move to eucalyptus in light mode

## M7 — Envision
- [ ] Positioning line + three principles: restraint, evidence, shipping
- [ ] Parkgate case-study entry card → `/work/parkgate/`
- Commit: `feat: envision section`

## M8 — Automate
- [ ] Line: "I work with agentic AI tools — Claude Code, Cowork — as a controlled, reviewed part of how I build: permissions on, every change read before commit."
- [ ] Three-step pipeline graphic: draft → schema-matched entry → published issue
- [ ] Latest Promptwrought issue as a static card (no iframe)
- Commit: `feat: automate section`

## M9 — Light/dark toggle
- [ ] Respect `prefers-color-scheme` on first load; toggle writes `data-theme`, persists to `localStorage`
- [ ] Swap token sets only — no per-element overrides
- [ ] Light mode check: cream page, teal hero, teal Make band, zero gold text on cream
- Commit: `feat: theme toggle`

## M10 — Parkgate case study
- [ ] `/work/parkgate/index.html` sharing tokens + header
- [ ] Structure: brief → constraints → three decisions and why → what shipped → what next. Before/after screenshots
- Commit: `feat: parkgate case study`

## M11 — Polish and ship
- [ ] Accessibility pass (contrast, focus, 44px targets, alt/`<title>`)
- [ ] OG image 1200×630 (monogram on teal); `<title>`, meta description, OG tags
- [ ] Lighthouse ≥ 90 across the board
- [ ] Merge `revamp` → `main`; Netlify deploys production
- [ ] Same day: LinkedIn headline → "Web Designer & Front-End Developer · Envision · Make · Automate"; add the site to the Evidence Inventory
- Commit: `feat: polish and launch`

---

## Content (the only copy Claude Code may use)

**Hero.** Emma Darling · Web Designer & Front-End Developer · *Envision · Make · Automate* · "I design websites, build them, and automate what comes next."

**Envision.** Three principles: restraint, evidence, shipping. Case study: Parkgate Construction — one-page site for a London construction firm; brief → brand → build → custom domain. Pull-quote: "Restraint is a design decision. The art is in the handfinish." — "handfinish" links to its Verbarium entry.

**Make.**
| Project | Stack / what it proves | URL | Featured |
|---|---|---|---|
| Parkgate Construction | HTML/CSS/JS, Netlify, DNS; paying client | parkgate-construction.com | yes |
| Verbarium | ~90 coined words, five volumes, search + category filter, localStorage | verbarium-mmxxvi.netlify.app | yes |
| Bank-a-Win | React habit-reward app — state, persistence | bank-a-win.netlify.app | yes |
| Forecast | Open-Meteo API — fetch, async | forecastlive.netlify.app | |
| Lingua Daily | Trilingual word-of-the-day (EN/FR/IT) | lingua-daily.netlify.app | |
| Pagine | Minimal notes, localStorage | pagine.netlify.app | |
| Tip Calculator | First interactive JS | tipcalculatorv2.netlify.app | |

**Automate.** The line above + pipeline graphic + latest Promptwrought issue (title, one line, link to promptwrought.com).

**Contact.** Email · LinkedIn · GitHub · Promptwrought · "Open to London / hybrid / remote."
