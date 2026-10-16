# PHASE 5.4 controlled klein 4B vs 9B quality A/B

This is a bounded human-evaluation experiment. It does not alter the V1 default
model, perform automatic scoring, or start PHASE 6.

## Official model and cost basis

- `@cf/black-forest-labs/flux-2-klein-4b` remains the configured V1 default.
- `@cf/black-forest-labs/flux-2-klein-9b` is an explicit optional calibration
  choice only. Cloudflare documents it as the enhanced-quality klein variant.
- Both models use the same multipart REST contract, optional seed, and up to four
  binary reference images; this spike keeps the existing one or two inputs.
- Cloudflare's published free allocation is 10,000 Neurons per day. The
  conservative estimate for these four `1088×1360` outputs and their reference
  inputs was approximately 3,758 Neurons. Cloudflare exposes usage in its
  dashboard rather than this REST request, so actual account balance is not
  embedded in repository output.
- Sources: [9B model documentation](https://developers.cloudflare.com/workers-ai/models/flux-2-klein-9b/),
  [9B launch notes](https://developers.cloudflare.com/changelog/post/2026-01-28-flux-2-klein-9b-workers-ai/),
  [Workers AI pricing](https://developers.cloudflare.com/workers-ai/platform/pricing/).

## Controlled variables

Each style pair reuses the same date, WeatherSnapshot, OutfitRecipe,
composition, scene, art direction, prompt content, conditioned reference bytes,
generation size, and seed. Only the Cloudflare model ID differs.

| Style | Target | Composition / art direction | Recipe silhouette | References | Seed | Outputs |
| --- | --- | --- | --- | ---: | ---: | --- |
| SOFT_BOYFRIEND | 2026-08-31 | `EDITORIAL_CROP` / `CLEAN_ARCHITECTURAL`, weight shift | `BOXY_TOP_RELAXED_BOTTOM` | 1 | 20260829 | `4b`, `9b` |
| OTAKU_GRUNGE | 2026-08-29 | `FACELESS_HERO` / `LOW_ANGLE_EDITORIAL`, adjusting outer | `RELAXED_TAILORING`, `DETAILED_DARK_TOP` | 2 | 20260829 | `4b`, `9b` |

The four paths are listed in the task report for human comparison. No automated
winner or production-model decision is recorded here.
