# emmadarling.dev revamp — build plan (15 Sep 2026)

Rules live in `CLAUDE.md`. This file is *what* to build, in order. Tick each box only after the branch preview has been checked on a phone.

Locked direction: **B rail + C monogram hero + A rhythm.** Playfair 600 headings, DM Sans body. Eucalyptus `#3A6357` on cream. Gold never as text on cream. Light mode = cream page, teal hero, teal Make band.

---

## M0 — Branch and safety net
- [x] `git checkout -b revamp` from an up-to-date `main`
- [x] Netlify → Site configuration → Build & deploy → Branch deploys → add `revamp`
- [x] Screenshot the current live site (desktop + phone) → save to `Promptwrought-Private/` as the "before"
- [x] Copy `CLAUDE.md` and `BUILD-PLAN.md` into the repo root
- Commit: `chore: revamp branch, CLAUDE.md, build plan`

## M1 — Design tokens
- [x] `:root` block: colours (teal, gold, cream, eucalyptus, aubergine, lavender), fluid type scale with `clamp()`, spacing scale, radii, shadows, `--ease`
- [x] `[data-theme="light"]` override set
- [x] Nothing hard-coded below `:root`
- Commit: `feat: design tokens`

## M2 — Skeleton and the column fix
- [x] Semantic structure per `CLAUDE.md`; rough content is fine
- [x] Every `<section>` full-bleed and coloured; `.container` inside with no background
- [x] Check at 1440 and 390: the aubergine column is gone
- Commit: `feat: page skeleton, full-bleed sections`

## M3 — Typography and rhythm
- [x] Playfair Display 600 on `h1`/`h2`; DM Sans body 17–19px, lh 1.6–1.7, ~68ch
- [x] Cormorant italic on the one pull-quote only
- [x] Vertical rhythm from the spacing scale
- Commit: `feat: typography`

## M4 — The monogram + rail
- [x] EMA as inline SVG paths (not an image), `<title>` inside
- [x] Large gold monogram in the hero (direction C)
- [x] Sticky rail: three letters E · M · A as anchor links; active letter in gold; no descriptor text
- [x] Draw-in animation on load, letters draw in E → M → A
- Commit: `feat: monogram hero and rail nav`

## M5 — Motion system
- [x] One `IntersectionObserver`, reveal once, stagger via `transition-delay`
- [x] Link underlines draw in from the left; 
- [x] Links: colour via a `--link` token (gold in dark, eucalyptus in light), no underline at rest, underline draws in on hover — "handfinish" is the test case 
- [x] Cards lift with a strengthened --line hairline on hover; never gold
- [x] `prefers-reduced-motion` collapses everything
- Commit: `feat: scroll reveals`

## M6 — Make: data-driven project grid
- [x] `projects` array → cards. Featured (larger): Parkgate, Verbarium, Bank-a-Win. Tight row: Forecast, Lingua Daily, Pagine, Tip Calculator
- [x] teal band in light mode; glass panels (`backdrop-filter: blur`) on teal
- [x] Tall-band reveal check: a band taller than ~6.7 screen heights never reaches the 0.15 reveal threshold. If the stacked grid on a phone gets there, observe the cards instead of the band
- Commit: `feat: project grid from data`
- [x] Check aubergine meta text on cream against the teal; if it clashes, `--text-muted` and `--label` move to eucalyptus in light mode

## M7 — Envision
- [x] Positioning line + three principles: restraint, evidence, shipping
- [x] Parkgate case-study entry card → `/work/parkgate/`
- Commit: `feat: envision section`

## M8 — Automate
- [x] Line: "I work with agentic AI tools — Claude Code, Cowork — as a controlled, reviewed part of how I build: permissions on, every change read before commit."
- [x] Three-step pipeline graphic: draft → schema-matched entry → published issue
- [x] Latest Promptwrought issue as a static card (no iframe)
- [x] Contact: icon + label row; muted colour; aria-labels not needed because labels are visible.
- Commit: `feat: automate section`

## M9 — Light/dark toggle
- [x] Respect `prefers-color-scheme` on first load; toggle writes `data-theme`, persists to `localStorage`
- [x] Swap token sets only — no per-element overrides
- [x] Light mode check: cream page, teal hero, teal Make band, zero gold text on cream
- Decided 22 Sep: theme set by script, not media query — one token set. A three-line script in <head> reads localStorage (else prefers-color-scheme) and sets data-theme before paint; documented in CLAUDE.md as the one exception to the single-script rule. The toggle reuses the same function.
- Commit: `feat: theme toggle`

## M10 — Parkgate case study
- [ ] `/work/parkgate/index.html` sharing tokens + header
- [ ] Structure: brief → constraints → three decisions and why → what shipped → what next. Live-site captures, desktop 1440 + phone 390, full page, details solid-blocked as Emma marks. No "before": Parkgate had no website (decided 24 Sep).
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


### Parkgate case study

**The brief**
Parkgate Construction had a domain name and nothing else: no website, no
business email, no brand. The owner wanted the company to look established,
something he could point a client to with confidence. I took on all of it,
from the logo to the last DNS record.

**Constraints**
No fixed budget and no deadline. The starting kit was one domain login, so
every word, colour and email address had to be made from scratch. The owner
had little time to spare, so I wrote the copy myself from short
conversations. He was new to having a website, so the result had to feel
manageable rather than technical. And it was my first client site.

**Three decisions and why**

1. Foundations before the website.
Before designing a single page, I set up Google Workspace on his domain:
his own address, plus hello@ and admin@. Looking established starts with
the email a client receives. It also meant suppliers could send receipts
straight to the business, which made the bookkeeping far smoother.

2. A green built to last.
I designed the logo in Canva first, in a neutral, trustworthy green: a
clean break from the navy and orange of his previous business. I kept
design trends out of it. It needed to be understated and minimal, to
stand the test of time, and to have a quiet Britishness that suits the
man behind it.

3. Type that had to earn its place.
The first draft was set in Garet throughout, and the owner didn't take to
it. I rebuilt it with DM Serif Display for headings, classic and steady,
and DM Sans for everything else, plain and practical.

**What shipped**
A logo, business email on Google Workspace, a one-page website deployed on
Netlify with the custom domain pointed via DNS, and a minimal invoice
template that carries the brand, with green only in the wordmark. The
owner was impressed with the site and happy with the wording.

**What's next**
Say less. Seeing his business live on the web was a lot for the owner, and
some details I drafted as placeholders still need confirming. The next
version keeps only confirmed facts, moves contact to email rather than
phone, and may carry a short availability note while current work runs.
On the working side, I'd set up shared access from day one, so fixes and
invoices don't wait on a single laptop.