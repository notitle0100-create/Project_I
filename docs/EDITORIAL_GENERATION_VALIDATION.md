# PHASE 5.5 editorial generation validation

Date: 2026-08-22. This is a bounded calibration record, not a production-quality decision.

- Provider/model: Cloudflare Workers AI / `@cf/black-forest-labs/flux-2-klein-4b`
- Successful generation requests: 2 (no aesthetic retry or fallback)
- Shared seed: `460826`; guidance: provider default (not configured)
- References: the already approved conditioned PNGs only; one reference per request

| Style | Recipe controls | Direction | Output |
| --- | --- | --- | --- |
| SOFT_BOYFRIEND | `soft_draped` top; `clean_wide_trouser`; `soft_suede_like_silhouette`; `soft_tactile` + `clean_smooth` | `EDITORIAL_CROP`, `PINTEREST_STREET`, `weight_shift`, subdued cafe exterior | `data/generated/2026-08-23/editorial.png` |
| OTAKU_GRUNGE | `GRAPHIC_FOCAL_TOP`; `graphic_focal` top; `relaxed_black_denim`; `distressed_low_top`; `washed_charcoal` + `faded_dark`; one necklace; no bag | `FACELESS_HERO`, `CANDID_URBAN`, `step_forward`, narrow urban street | `data/generated/2026-08-26/editorial.png` |

Observation only: both successful files show disallowed facial regions (SOFT: chin/jaw and part
of the face; OTAKU: full face). No Vision QC, automatic crop, or additional generation was
performed. PHASE 6 remains unstarted.
