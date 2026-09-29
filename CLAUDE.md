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
- Every page's <head> carries: title, meta description, canonical, og:type
  (website for home, article for a case study), og:url, og:title,
  og:description, og:image with width 1200, height 630 and alt,
  twitter:card summary_large_image, an SVG icon and an apple-touch-icon.
  Decided 27 Sep (M11).
- Internal links are root-absolute (/, /#envision, /work/<slug>/): the site is
  always served, so navigation is tested through a local server, never file://.
  Decided 25 Sep (M10).
- Asset paths (stylesheets, images, icons) are relative; navigation links are root-absolute.
  Metadata URLs (canonical, og:url, og:image) are absolute https://emmadarling.dev/…,
  because crawlers read them without knowing which page they came from. Decided 27 Sep (M11).
- The latest-issue card is plain HTML between <!-- latest-issue:start --> and
  <!-- latest-issue:end --> in index.html, rewritten by tools/update-latest-issue.py
  (Python standard library). .github/workflows/latest-issue.yml runs it on Tuesdays and
  opens a pull request into main. Neither is part of the page or a build step: the page is
  still one static file. Never hand-edit between the markers. Netlify serves tools/ and
  .github/ publicly, which is harmless. Decided 29 Sep.
- Its source is promptwrought-site's issue files (issues/NNN-word.json on main): the
  highest-numbered issue whose release moment has passed. Issue N goes out at 13:31 London
  time on the Tuesday of ISO week N + 30, 2026, so numbers never slip. Those constants are
  copied from promptwrought-site/tools/build-lexicon.py; change both together. The link is
  built as https://promptwrought.substack.com/p/<word> and must match the file's issueUrl
  whenever that's filled in (promptwrought-site lets it stay empty for a while).
  Not the Substack feed: Substack answers GitHub's runners with HTTP 403, so the Action
  can't read it (found 29 Sep). There is no feed fallback, deliberately.

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
- Files outside the page can't read tokens.css. The OG image, favicon and
  apple-touch-icon hard-code teal #0E2A35, cream #F5EDD6 and the monogram's
  source gold #c18439 (the Canva export; the page's token gold is #C8922A).
  Their letters are only ever the paths from images/ema-monogram.svg, moved and
  scaled, never redrawn. Sources: images/og-image.svg and images/favicon.svg
  (the E, outlined so its hairlines survive at 16px); apple-touch-icon.png is
  the same E at 180px without the outline. Decided 27 Sep (M11).

## Design decisions
- Monogram: E·M·A in Noto Serif Display, tightly tracked, matching the LinkedIn
  banner. No shared stroke. Source: images/ema-monogram.svg.
- Case-study header: compact. A top-bar-size monogram links home and still draws
  in; no shrink or top bar. Rail letters link to /#section, with E marked current.
- Links: in-sentence links keep a faint underline at rest (WCAG 1.4.1 — their
  colour alone is under 3:1 against the text around them); standalone links
  have none. Both draw the full underline in on hover and focus.
- Under the fixed top bar: sections a rail letter jumps to stop flush under it
  (scroll-margin-top: var(--bar-height)); links and buttons stop
  var(--focus-clearance) below it, so Shift+Tab never hides focus. Offsets live
  on the elements as scroll-margin, never as scroll-padding on html, which
  Safari doesn't reliably apply to anchor jumps. Both reset to 0 under reduced
  motion, where there is no bar. Decided 27 Sep (M11).

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
  44px means width as well as height: a short link widens with padding-inline and
  a matching negative margin, so nothing visibly moves.
  Generated content that is only for the eye (CSS counters) gets empty alt text —
  content: x / "" — after a plain declaration as the fallback.
- Images: every <img> keeps its width and height. Images below the fold get
  loading="lazy" decoding="async"; the first image in view never does.
- Comment CSS sections and JS functions in plain English — I'm learning from this code.
- Ask before running commands. Never force-push. Never touch main.
