---
title: Home Page Next Image Baseline
type: quality
date: 2026-06-15
status: completed
execution: code
---

# Home Page Next Image Baseline

## Summary

Replace the five raw home-page image elements with the repository's existing
Next.js image component pattern. Preserve the current assets, responsive
constraints, accessible labels, button behavior, and link behavior while
eliminating the maintained frontend lint warnings.

## Requirements

- R1. Every home-page asset must render through `next/image`; raw `<img>`
  elements must not remain in the page.
- R2. Intrinsic dimensions must match the checked-in asset dimensions so image
  aspect ratios remain stable before load.
- R3. Existing responsive maximum widths, alternative text, modal trigger, and
  technical-details navigation must remain unchanged.
- R4. The maintenance baseline must reject restoration of a raw image element,
  removal of the image import, or drift in the five expected asset mappings.
- R5. Frontend lint and production build verification must complete without the
  previously documented `no-img-element` warnings.

## Scope Boundaries

- Do not redesign the page, replace image assets, or change visible copy.
- Do not alter story-generation behavior or external service integrations.
- Do not add remote image hosts or bypass Next.js image optimization.

## Implementation Units

1. Convert the five local home-page images to `next/image` with checked-in
   intrinsic dimensions and the existing responsive classes.
2. Extend the static maintenance baseline with a focused home-page image
   contract and completed-plan evidence.
3. Run focused mutations, the full Python/frontend gates, and final artifact,
   diff, and secret audits.

## Verification

- `npm run lint` completed with zero warnings or errors, removing the five
  previously documented `no-img-element` warnings.
- The Next.js 15.5.19 production build completed successfully, including type
  checking and all seven generated pages.
- Playwright Chromium 140 desktop and mobile full-page captures confirmed the
  responsive image constraints, stable layout, and unchanged controls. The
  host's Chrome 80 was not used as evidence because it predates the CSS cascade
  layers required by Tailwind 4.
- Seven hostile mutations were rejected across raw image restoration, missing
  import, dimension, source, class, alternative-text, and plan-status drift.
- Full repository and external-directory `make check` verification passed with
  the offline Python suite, frontend lint, and dependency audit.
