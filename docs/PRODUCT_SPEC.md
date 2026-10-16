# Product specification

## PHASE 5 image provider policy

V1 uses Cloudflare Workers AI as the default image provider with
`@cf/black-forest-labs/flux-2-klein-4b`. It requests `1088x1360` and
normalizes to the final `1080x1350` 4:5 image without cropping or stretching.
Cloudflare quota, credential, permission, and capacity
failures must stop generation without automatic paid-provider fallback. OpenAI
Image API remains optional and is selected only through configuration.

`AGENTS.md`의 영구 범위 안에서 구현해야 할 제품·콘텐츠 상세 규칙이다. 구현 순서는 `PLAN.md`를 따른다.

## Product identity

- “서울의 내일 날씨에 맞춰 매일 하나의 20대 남성 데일리 코디를 제안하는 Faceless Fashion Magazine”
- AI는 내부 제작 수단이며 콘텐츠 전면에 내세우지 않는다.
- 현실적인 착용성, 날씨 적합성, 높은 이미지 미감, 다양한 스타일, 일관된 editorial identity를 우선한다.
- 대상은 20대 성인 남성이고, 일상·대학·데이트·카페·약속·주말·가벼운 출근·전시·여행 등 다양한 상황을 사용한다.

## Style rotation

초기에는 동일 비중으로 다음 순서를 반복한다. 충분한 데이터 전에는 가중치 최적화를 하지 않는다.

`SOFT_BOYFRIEND → MINIMAL → AMEKAJI → OTAKU_GRUNGE → repeat`

- `SOFT_BOYFRIEND`: soft tactile upper, controlled relaxed proportion, intentional understated
  footwear, and contemporary 20s casual layering; a gray/navy/white office-casual formula is not
  a default.
- `MINIMAL`: neutral palette, clean lines, low visual noise, proportions와 silhouette 중심
- `AMEKAJI`: denim, fatigue/workwear, canvas, leather, heritage; 코스튬보다 일상성 우선
- `OTAKU_GRUNGE`: contemporary Korean/Japanese alternative men's streetwear: washed black/charcoal, deliberate upper/lower proportion, controlled contrast, restrained rock influence, and everyday editorial wearability.

### OTAKU_GRUNGE visual direction

- Two content axes are used: `DETAILED_DARK_TOP` (dark tailoring, construction, texture, or layering as the focal point) and `GRAPHIC_FOCAL_TOP` (an original abstract or anime-inspired graphic, never a copied character).
- Tailoring, long outerwear, faded/distressed texture, and vertical layering are optional structural devices; flannel is optional and never a core archetype.
- Generic black cargo, techwear, and random chain/keyring stacking are not defaults. Cargo or Bermuda lower is used only when it serves the selected silhouette.
- All-black uses washed black, charcoal, matte black, faded black, and material contrast. Silver details are limited to one or two focal points at the neck, waist, wrist, or bag.
- Footwear uses a brand-agnostic visual weight: restrained low-profile sneaker, dark leather footwear, bulky black layered-sole sneaker, or rugged work boot.
- User-provided references ground the visual grammar. Graphics must remain original and abstract; the result must read as everyday streetwear rather than cosplay.
- Reference video: <https://www.youtube.com/watch?v=eWZ7nAF3JMs&list=PLPkXedpYi1q7fl6DfBKNSSXI2vn4wTfni>

## Weather rules

- 위치: Seoul, South Korea
- 시간대: `Asia/Seoul`
- 실제 Weather API에서 다음 날 최고/최저기온, 일교차, 강수확률, condition을 가져온다. LLM이 값을 생성하지 않는다.
- 큰 일교차는 layering 우선순위를 높이고, 비가 오면 관리하기 어려운 소재와 지나치게 긴 바지를 피한다.

| 최고기온 | 기본 의류 방향 |
| --- | --- |
| `>= 28°C` | 반소매, 가벼운 소재, summer styling |
| `23–27°C` | 반소매, 얇은 셔츠, 가벼운 바지 |
| `20–22°C` | 셔츠, 긴소매, light trousers |
| `17–19°C` | cardigan, light knit, sweatshirt, hoodie |
| `12–16°C` | jacket, cardigan, denim jacket, knit |
| `9–11°C` | trench, field jacket, jumper |
| `5–8°C` | coat, warmer layers |
| `<= 4°C` | puffer, heavy coat, thermal layering |

복잡한 weather scoring engine은 만들지 않는다.

## OutfitRecipe and later composition

- 이미지보다 먼저 Pydantic으로 검증되는 structured `OutfitRecipe`를 만든다.
- 최소 필드: target date, style, occasion, mood, top, bottom, nullable outer, shoes, nullable bag, accessories, palette, layering depth, styling notes, controlled silhouette profile, optional OTAKU content axis. Recipe JSON also uses a small controlled vocabulary for top structure, bottom structure, texture profile, layering role, and footwear shape; it does not introduce free-text garment specifications or database columns.
- Silhouette profile은 upper volume, top length, shoulder shape, outer length, lower volume, pant break, footwear visual weight, and strategy를 작은 enum으로 관리한다. 가방·액세서리에는 제한된 carry/placement와 visual role을 둔다.
- OutfitRecipe에는 실제 brand/product/SKU/price/shop/purchase URL을 넣지 않는다. composition과 scene은 image 단계에서 분리한다.
- schema, 온도 적합성, 스타일 적합성을 통과한 recipe만 이미지 단계로 넘긴다.
- 허용 composition: `FACELESS_HERO`, `EDITORIAL_CROP`, `REAR`, `THREE_QUARTER_REAR`, `STREET_SNAP`, `DETAIL_EDITORIAL`.
- 최근 recipe signature(style/top/bottom/palette/outer/shoes)를 참고해 반복을 줄인다.
- SOFT_BOYFRIEND/MINIMAL은 hero·editorial, AMEKAJI는 hero·rear·detail, OTAKU_GRUNGE는 street·rear·detail·hero를 우선한다.

## Image identity and QC

- 성인 남성의 slim-to-average silhouette를 사용하고 실제 인물·유명인을 복제하지 않는다.
- face, chin, jawline 중 하나라도 보이면 hard fail이다. 머리카락·뒤통수는 허용한다.
- 목표: photorealistic premium editorial, 사실적인 원단/주름/신체 비율, available/soft light, tactile urban or architectural context, intentional negative space.
- Image 단계는 style별 controlled art direction preset으로 pose, body angle, camera height/distance, subject position, frame occupancy, negative space, background texture/clarity, lighting을 선택한다. 같은 centered standing catalog pose를 기본값으로 두지 않는다.
- malformed body/hands/footwear, clothing merge, fake logo, random text, watermark, 명백한 AI artifact를 허용하지 않는다.
- 최종 이미지는 4:5, 1080×1350이다.
- 구현 시점의 Cloudflare Workers AI 공식 REST API와 지원 모델을 확인하고 모델 ID는 env로 주입한다. OpenAI Image API는 optional provider로 유지한다.
- PHASE 5는 단일 prompt 생성에 Cloudflare Workers AI와 기본 `@cf/black-forest-labs/flux-2-klein-4b`를 사용한다. generation size는 config로 관리하며 `1088x1360`을 `1080x1350`으로 resize한다.
- QC 결과에는 face/chin/jaw visibility, body/clothing/shoe anomaly, text artifact, quality, style accuracy, Instagram readiness가 포함되어야 한다.
- 실패 원인을 반영한 재생성은 최대 1회다. 두 번째 실패는 `REVIEW_REQUIRED`로 보내고 게시하지 않는다.

## Carousel and caption

- Carousel은 4–6장으로 hero, tomorrow weather, outfit/layering detail, secondary editorial, 선택적 rear/detail/street, final style guide 순서를 기본으로 한다.
- 가격, 실제 브랜드·상품명, 구매 링크를 넣지 않는다.
- Caption은 한국어 fashion magazine tone으로 날씨, outfit 방향, styling point, 짧은 save CTA, 소수 hashtag를 담는다.
- 광고성 문구, 과도한 AI 말투·친근체·emoji, 구매 유도를 피하고 최근 caption과 문장 구조를 반복하지 않는다.

## Workflow, states, and publishing

`Weather → Style → Occasion/Mood → OutfitRecipe → Composition → Image → QC → Carousel → Caption → Admin Preview → APPROVE → Publish`

최소 상태:

`PLANNED`, `WEATHER_READY`, `OUTFIT_READY`, `IMAGE_GENERATING`, `IMAGE_QC`, `CAROUSEL_READY`, `AWAITING_APPROVAL`, `APPROVED`, `PUBLISHING`, `PUBLISHED`, `REVIEW_REQUIRED`, `REJECTED`, `FAILED`.

- 상태 변경과 실패 원인을 DB에 기록하고 유효하지 않은 전이를 거부한다.
- 최소 entity: `StylePreset`, `WeatherSnapshot`, `OutfitRecipe`, `Content`, `GeneratedImage`, `Publication`, `GenerationLog`.
- Admin UI는 APPROVE / REGENERATE / REJECT에 필요한 최소 기능만 제공한다.
- 하루 한 번, 18:30–19:00 KST 생성 완료 후 승인된 콘텐츠를 19:30 KST에 게시한다.
- 게시에는 구현 시점의 공식 Meta/Instagram API만 사용한다.
- `content_uuid`와 remote media identifier를 저장해 timeout/restart/retry에도 중복 게시를 막는다.
- 최초 30–50개 콘텐츠로 생성 품질과 QC 정확성을 검증한 뒤에만 자동 게시 확대를 검토한다.

## V1 technology and completion

- Python 3.12+, FastAPI, Pydantic, PostgreSQL, SQLAlchemy, Alembic, Cloudflare Workers AI REST API, optional OpenAI SDK, documented Weather API, Pillow, simple scheduler, pytest, Docker/Compose.
- V1 완료 흐름: 서울 다음 날 날씨 → 4-style rotation → recipe → faceless image → QC → magazine content → Admin 승인 → 19:30 KST 공식 게시.
- V1에서 사람이 수행하는 작업은 최종 승인 하나여야 한다.
