# PHASE 5.3 reference-conditioning spike

This is a bounded Cloudflare FLUX.2 klein 4B calibration experiment, not a new
production feature or a reference-image archive. Original user references remain
outside this repository. Only the Git-ignored, head-out PNG derivatives used by
the live smoke test are stored in `data/reference-conditioned/`.

## Provider contract

- Cloudflare's current FLUX.2 klein 4B REST endpoint accepts multipart form data
  even for text-only prompts.
- It accepts up to four binary inputs named `input_image_0` through
  `input_image_3`; each must be smaller than 512×512.
- This spike intentionally sends no more than two conditioned references and uses
  the documented optional `guidance` and `seed` fields only when configured.
- Source: [Cloudflare FLUX.2 klein 4B launch documentation](https://developers.cloudflare.com/changelog/post/2026-01-15-flux-2-klein-4b-workers-ai/).

## Visual-grammar selection

The selections below are references to proportion, framing, pose, material, and
editorial mood only. They never authorize person, brand, logo, garment, graphic,
or exact-outfit reproduction.

| Style | Reference ID | Why it is representative | Live input |
| --- | --- | --- | --- |
| SOFT_BOYFRIEND | `soft-street` | Walking street frame, relaxed upper/longer lower proportion, shoulder bag counterweight, natural negative space. | Yes |
| MINIMAL | `minimal-black-zip` | Quiet black/white tonal separation, clean vertical line, restrained accessories. | No |
| MINIMAL | `minimal-structured-coat` | Tailored outer/inner layering and controlled dark proportion without decorative noise. | No |
| AMEKAJI | `amekaji-indigo-fatigue` | Boxy work shirt, wide fatigue trouser, material contrast, candid outdoor framing. | No |
| AMEKAJI | `amekaji-ma1-selvedge` | Short workwear outer, cuffed denim, substantial boot weight, practical color blocks. | No |
| OTAKU_GRUNGE | `otaku-tailored-dark` | DETAILED_DARK_TOP: relaxed black tailoring, muted inner layer, long dark trouser line, seated editorial mood. | Yes |
| OTAKU_GRUNGE | `otaku-faded-dark` | DETAILED_DARK_TOP: faded charcoal texture, controlled distressed black denim, heavy footwear presence without accessory stacking. | Yes |

## Conditioned live inputs

| Reference ID | Original size | Head-out crop | Conditioned size | Derived path |
| --- | ---: | ---: | ---: | --- |
| `soft-street` | 644×874 | top 55 px | 402×511 | `data/reference-conditioned/soft-street.png` |
| `otaku-tailored-dark` | 729×929 | top 85 px | 441×511 | `data/reference-conditioned/otaku-tailored-dark.png` |
| `otaku-faded-dark` | 580×870 | top 130 px | 401×511 | `data/reference-conditioned/otaku-faded-dark.png` |

Each derivative uses a top crop only, preserves aspect ratio, is converted to RGB
PNG, and is resized with Lanczos so both dimensions are at most 511 px. The
conditioner reads a specified source once and writes only beneath its fixed local
output root; the Cloudflare adapter receives in-memory validated PNG bytes rather
than a path.

## Prompt order

When references are present, the prompt begins with the copy-safe reference-use
instruction, then keeps the existing order: faceless composition, silhouette,
OutfitRecipe garment structure, proportion, pose/art direction, style grammar,
texture/palette, environment, camera/lighting. The reference instruction is
omitted entirely from existing text-only prompt paths. OpenAI deliberately rejects
a reference-conditioned request rather than silently dropping references or using
a paid fallback.

## Bounded live result

The one-pass A/B run used seed `20260826` and the locally configured guidance
value (if present); it did not vary either parameter.

| Sample | Recipe / composition | Art direction | References | Output | Result |
| --- | --- | --- | ---: | --- | --- |
| SOFT_BOYFRIEND | `BOXY_TOP_RELAXED_BOTTOM` / `FACELESS_HERO` | `CLEAN_ARCHITECTURAL`, hands-in-pockets, front | 1 | `data/generated/2026-08-28/editorial.png`, 1080×1350 | Chin/jaw area visible: faceless hard-policy failure. |
| OTAKU_GRUNGE | `RELAXED_TAILORING`, `DETAILED_DARK_TOP` / `REAR` | `CANDID_URBAN`, step-forward, rear | 2 | `data/generated/2026-08-26/editorial.png`, 1080×1350 | Face invisible (rear-only head); dark tailoring reads, but faded/alternative street texture remains under-conditioned. |

No image was retried. Neither output closely reproduces a reference outfit,
graphic, logo, or person.
