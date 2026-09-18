# emmadarling.dev — revamp

## What this is
One-page portfolio + case-study pages. Design is locked: see
design/portfolio-directions.dc.html — build direction **2a** (dark, default)
and **2b** (light). Ignore 1a/1b/1c and 3a/3b; they were explorations.

## Stack — non-negotiable
- One index.html, one <style> block in <head>, one <script> block before </body>.
- Google Fonts via <link>. No framework, no build step, no npm, no CDN libraries.
- Case-study pages at /work/<slug>/index.html, same tokens and header.

## Tokens
- Every colour, font, size, space, radius, shadow and easing declared once in :root.
- Light mode is a [data-theme="light"] override set. Nothing hard-coded below :root.
- Fonts: Playfair Display 600 (display), DM Sans 400/500 (body, labels),
  Cormorant Garamond 400 italic (pull-quote only). Four weights total. Nothing else.
- Gold #C8922A appears at most four times per page and never as text on cream.

## Design decisions
- Monogram: E·M·A in Noto Serif Display, tightly tracked, matching the LinkedIn
  banner. No shared stroke. Source: images/ema-monogram.svg.

## Rules of the build
- One milestone per session, one commit per milestone. Do not start the next.
- Sections are full-bleed; .container inside sets max-width and has no background.
- Projects render from a `projects` array — no project markup hand-written in HTML.
- Motion: token easing, one IntersectionObserver (threshold 0.15, unobserve after
  firing), prefers-reduced-motion collapses everything to 0.01ms.
- Accessibility: contrast ≥ 4.5:1, :focus-visible 2px outline in var(--focus), 44px targets.
  --focus is lavender in dark mode and on ink bands in both themes, ink on cream — never gold.
  External links: target="_blank" rel="noopener noreferrer".
- Comment CSS sections and JS functions in plain English — I'm learning from this code.
- Ask before running commands. Never force-push. Never touch main.