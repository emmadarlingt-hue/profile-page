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
- [x] Links: colour via a `--link` token (gold in dark, eucalyptus in light). In-sentence links keep a faint underline at rest; standalone links have none. The full underline draws in on hover and focus — "handfinish" is the test case (line corrected 27 Sep to match the code)
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
- [x] `/work/parkgate/index.html` sharing tokens + header
- [x] Structure: brief → constraints → three decisions and why → what shipped → what next. Live-site captures, desktop 1440 + phone 390, from the top of the page to the bottom of "What we do", details solid-blocked as Emma marks. No "before": Parkgate had no website (decided 24 Sep).
- Decided 25 Sep: the claims were removed from the live site instead, so the captures carry no grey blocks.
- Capture method (used 25 and 27 Sep):
  - Before capturing, fetch the live HTML fresh (cache-buster; Netlify's `cache-status` should say `fwd=miss`) and check the removed claims are still gone. If any are back, list them and stop.
  - Headless Chrome, driven over the DevTools Protocol pipe from a small Node script. In Claude Code it has to run outside the sandbox; inside, Chrome aborts.
  - Desktop: viewport 1440×900 at device pixel ratio 1 → file 1440px wide. Phone: viewport 390×844 at ratio 2 → file 780px wide. The same ratios as the case page's frames (`--shot-ratio-desktop`, `--shot-ratio-phone`).
  - Reduced motion on. Wait for fonts, scroll down to the bottom of "What we do" so every reveal fires, then back to the top and let it settle, so the fixed nav sits at the top.
  - Crop at the bottom of `#services` ("What we do"). WebP, quality 80.
  - Save to a scratch folder first. After Emma approves: replace the same filenames in `images/parkgate/`, set each `<img>` width/height from `sips -g pixelWidth -g pixelHeight`, and update the alt text below if what the frames show has changed.
- Commit: `feat: parkgate case study`

## M11 — Polish and ship
- Decided 27 Sep: M11 ships ahead of M10.5 so the site can launch tonight; M10.5 follows launch. Committed one step at a time, each pushed to `revamp` for a preview check.
- [x] Accessibility pass (contrast, focus, 44px targets, alt/`<title>`). Both pages, both themes, 390 and 1440, reduced motion on and off: lowest text contrast 4.63:1, a 2px ring on every Tab stop in both directions, one h1 each, real alt text and monogram `<title>`. Fixed:
  - the "Code" links widened to 44px;
  - rail jumps land sections flush under the top bar in Safari too (scroll-margin, not scroll-padding), and Shift+Tab keeps focus clear of the bar;
  - Parkgate's decision numbers no longer read as ". Foundations…".

  "handfinish" keeps its faint underline at rest (WCAG 1.4.1).
- [x] OG image 1200×630 (monogram on teal); `<title>`, meta description, OG tags. Also canonical, og:image width/height/alt, twitter:card summary_large_image, an SVG favicon (the E, outlined) and a 180px apple-touch-icon. `/seo-check` passed both pages. Two suggestions wait for Emma: longer descriptions (they're Content copy, 125 and 84 characters) and JSON-LD (it would be a third `<script>`).
- [x] Image weight (finding 10): the Parkgate captures are already WebP q80 (84,018 B and 157,886 B), lazy-loaded and below the fold. Left as they are, decided 27 Sep.
- [ ] Lighthouse ≥ 90 across the board. Run by Emma on 27 Sep, home page (Performance / Accessibility / Best Practices / SEO): desktop 99 / 100 / 100 / 100, mobile 61 / 100 / 100 / 100. Left unticked because mobile Performance is under 90; the findings are under "Mobile performance (after launch)" below.
- [ ] Merge `revamp` → `main`; Netlify deploys production (Emma). Link previews show the new OG image only after this, because og:image points at production.
- [ ] Same day: LinkedIn headline → "Web Designer & Front-End Developer · Envision · Make · Automate"; add the site to the Evidence Inventory (Emma)
- Commits: `docs: M11 before M10.5`, `feat: head metadata and og image`, `fix: accessibility pass`, `fix: sections land flush under the bar`, `chore: tick M11`, `docs: record lighthouse scores`

## M10.5 — Shared base (after launch)
- Decided 27 Sep: follows M11, once the site is live.

Deferred from the M10 review (#1, #3/#10, #12). The home page and the case page repeat the same CSS and script, and the case page repeats Parkgate's data by hand.
- [ ] First, record the decision in `CLAUDE.md`: shared files beyond `tokens.css` are an exception to the single-file rules, as M10 recorded for tokens
- [ ] `/base.css`: the skeleton, rail, theme toggle, links and reveals that both pages carry today
- [ ] `/site.js`: the theme toggle and reveals, written once. Includes the back/forward-cache fix: on `pageshow` with `event.persisted`, and on the `storage` event, re-read the saved theme and apply it without transitions
- [ ] `/projects.js`: the `projects` array, read by both pages. The case page builds its name, `caseSummary` lead, year/stack line and links from it. Settle the stack first: the case page lists Canva and Google Workspace, the array doesn't. The meta description stays in the HTML, because link previews don't run scripts
- Known bug at launch, fixed by the `/site.js` item above: change the theme on one page, then press Back or Forward. The page the browser restores from its back/forward cache keeps the theme it had, because the `<head>` script doesn't run again on a restore, so it shows the old theme until it's reloaded. A second open tab doesn't follow a change either, because nothing listens for the `storage` event.
- Commit: `refactor: shared base`

## Mobile performance (after launch)
- Found 27 Sep by Lighthouse on the home page, mobile: Performance 61 (desktop 99). This is what keeps M11's Lighthouse box unticked.
- [ ] Render-blocking requests: about 2.8s, mostly Google Fonts
- [ ] Largest Contentful Paint: 5.8s
- Done when mobile Performance is 90 or more; then tick M11's Lighthouse box.

## Latest-issue automation (after launch)
- Decided 29 Sep: the Automate card is plain HTML between two marker comments, rewritten by `tools/update-latest-issue.py`. `.github/workflows/latest-issue.yml` runs it on Tuesdays at 13:07 and 14:07 UTC, with catch-ups at 17:07, 20:07 and Wednesday 08:07, and opens a pull request into main when the card changes. The catch-ups exist because an issue file lands on promptwrought-site's main only after the issue has gone out.
- [x] Script, workflow and the plain-HTML card
- Found on 29 Sep: the first manual dry run failed with "Couldn't read the feed (https://promptwrought.substack.com/feed): HTTP 403". Substack blocks GitHub's runner IPs; the same script reads the feed from the Mac. So the source switched to promptwrought-site's issue files: the highest-numbered issue whose release moment (13:31 London time, Tuesday of ISO week N + 30) has passed, with the link built from the word and checked against the file's issueUrl. The feed is gone, with no fallback.
- [x] Source switched to promptwrought-site
- [ ] After merging to main (Emma): Settings → Actions → General → turn on "Allow GitHub Actions to create and approve pull requests"
- [ ] Then Actions → Latest issue card → Run workflow with "Dry run" ticked. Its log shows the card it would write and says "Dry run (would update)" if there's a newer issue than the page shows, or "Dry run (already current)". Either proves the runner can read promptwrought-site. (The card shows Issue 010, ghostwrought, so until 6 Oct expect "already current".)
- Found on 29 Sep: ghostwrought went out at 12:32 UTC, but its issue file only reached GitHub after 13:21, though its commit is dated the evening before. A commit's date is when it was made, not when it was pushed, so issue files can arrive later than their history suggests. The catch-up runs cover that.
- Worth knowing: GitHub switches off a public repo's scheduled workflows after 60 days without commits, and sends failure emails to whoever last edited the cron lines.
- Commits: `feat: automate latest-issue card`, `fix: read latest issue from promptwrought-site`

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
   **Case summary** (Envision card and case-page header):
   From a domain name and nothing else to a brand, a business inbox and a live website.

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

**Screenshot alt text** (What shipped; describes only what each frame shows)
- Desktop: Parkgate Construction homepage on desktop: the headline 'Built to last. Finished to impress.' beside a dark grid panel.
- Phone: Parkgate Construction homepage on a phone: the headline, introduction and green 'Request a quote' button.

**What's next**
Say less. Seeing his business live on the web was a lot for the owner, so the first revision took things away: the phone number came off in favour of email, placeholder figures became plain statements, and the emoji icons became simple line icons in the brand green. Enquiries from the form now land in the business inbox. Next, I'd set up shared access from day one, so fixes and invoices don't wait on a single laptop.
