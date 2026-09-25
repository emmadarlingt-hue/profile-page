# emmadarling.dev — revamp

## What this is
One-page portfolio + case-study pages. Design is locked: see
design/portfolio-directions.dc.html — build direction **2a** (dark, default)
and **2b** (light). Ignore 1a/1b/1c and 3a/3b; they were explorations.

## Stack — non-negotiable
- One index.html, one <style> block in <head>, one <script> block before </body>.
- One exception to the single-script rule: a short inline script in <head> sets
  data-theme on <html> before first paint. It reads localStorage 'theme' inside
  try/catch, trusts only the words "light" and "dark", and otherwise falls back to
  prefers-color-scheme. It sits above every stylesheet <link> on purpose — a
  stylesheet still loading blocks the scripts after it from running, and this one
  has to beat the first paint. Nothing else may go in it.
- Second exception: tokens live in /tokens.css, linked by every page straight
  after the theme script and before Google Fonts. It holds only :root and
  [data-theme="light"] — no selectors, no components. Decided 24 Sep (M10) so
  tokens are declared once across pages.
- Google Fonts via <link>. No framework, no build step, no npm, no CDN libraries.
- Case-study pages at /work/<slug>/index.html, same tokens and header.
- Internal links are root-absolute (/, /#envision, /work/<slug>/): the site is
  always served, so navigation is tested through a local server, never file://.
  Decided 25 Sep (M10).
- Asset paths (stylesheets, images) are relative; navigation links are root-absolute.

## Tokens
- Every colour, font, size, space, radius, shadow and easing declared once, in :root in /tokens.css.
- Light mode is a [data-theme="light"] override set. Nothing hard-coded below :root.
- No prefers-color-scheme media query anywhere: the theme is chosen by script and
  written to <html>, so there is one token set rather than two kept in sync. With
  JavaScript off the dark default stands, color-scheme: dark included, and the
  toggle stays hidden. Deliberate, decided 22 Sep — not an oversight to "fix".
- Fonts: Playfair Display 600 (display), DM Sans 400/500 (body, labels),
  Cormorant Garamond 400 italic (pull-quote only). Four weights total. Nothing else.
- Gold #C8922A has at most four roles per page: the hero monogram, the top-bar
  monogram copy, the active rail letter, and text links. Never as text on cream.

## Design decisions
- Monogram: E·M·A in Noto Serif Display, tightly tracked, matching the LinkedIn
  banner. No shared stroke. Source: images/ema-monogram.svg.
- Case-study header: compact. A top-bar-size monogram links home and still draws
  in; no shrink or top bar. Rail letters link to /#section, with E marked current.

## Rules of the build
- One milestone per session, one commit per milestone. Do not start the next.
- Sections are full-bleed; .container inside sets max-width and has no background.
- Projects render from a `projects` array — no project markup hand-written in HTML.
- Motion: token easing, prefers-reduced-motion collapses everything to 0.01ms.
- Two IntersectionObservers — rail scroll-spy (rootMargin band, threshold 0,
  permanent) and section reveals (threshold 0.15, unobserve after firing).
  Never a third.
- Accessibility: contrast ≥ 4.5:1, :focus-visible 2px outline in var(--focus), 44px targets.
  --focus is lavender in dark mode and on teal #0E2A35 bands in both themes, teal #0E2A35 on cream — never gold.
  External links: target="_blank" rel="noopener noreferrer".
- Comment CSS sections and JS functions in plain English — I'm learning from this code.
- Ask before running commands. Never force-push. Never touch main.
