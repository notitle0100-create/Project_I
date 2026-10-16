# V1 implementation plan

## PHASE 5 provider update — Cloudflare Workers AI

- [x] Cloudflare Workers AI REST adapter for `@cf/black-forest-labs/flux-2-klein-4b`
- [x] Cloudflare as the V1 default; OpenAI remains an explicit optional provider
- [x] Cloudflare `1088x1360` generation with `1080x1350` normalization, bounded technical retries, and quota-safe errors
- [x] Mocked provider, selection, processing, and OpenAI regression tests

Status: Cloudflare Workers AI provider implementation: **DONE**. Initial live Cloudflare smoke
test completed; reference-calibrated live results are recorded below. OpenAI live smoke test remains
**OPTIONAL / NOT REQUIRED FOR V1**.

## PHASE 5.1 — Prompt calibration spike

- [x] Front-load positive neck-down composition instructions for front-facing faceless images
- [x] Send FLUX.2's documented structured JSON prompt only through the Cloudflare adapter
- [x] Add optional Cloudflare `guidance` forwarding without setting a project default
- [x] Recalibrate OTAKU_GRUNGE as three concrete, wearable archetypes
- [x] Run one SOFT_BOYFRIEND and one OTAKU_GRUNGE live sample (no retry)

Exit: determine whether klein 4B can follow the faceless composition with the calibrated prompt;
this spike does not start PHASE 6 or add Vision QC.

Status: SOFT_BOYFRIEND FACELESS_HERO passed visual framing. The FLANNEL_GRUNGE sample
expressed the intended streetwear grammar but retained chin/jaw facial area; no further live
generation was performed. PHASE 6 remains unstarted.

## PHASE 4.5 — Reference-calibrated styling

- [x] Add controlled OutfitRecipe silhouette profile and silhouette strategies without a migration
- [x] Include silhouette/pant break/footwear weight/content axis in recipe diversity signatures
- [x] Replace OTAKU fixed FLANNEL_GRUNGE archetype with `DETAILED_DARK_TOP` and
  `GRAPHIC_FOCAL_TOP` content axes
- [x] Apply restrained accessory placement/role and all-black tonal hierarchy rules
- [x] Add SOFT_BOYFRIEND, MINIMAL, AMEKAJI, OTAKU, weather, compatibility, and invalid-combination tests

Status: **IMPLEMENTED**. The current recipe JSON payload is extended without new columns or an
Alembic migration. All local tests pass.

## PHASE 5.2 — Reference-calibrated art direction

- [x] Add provider-neutral controlled art direction preset, pose, camera, occupancy, space, texture,
  clarity, lighting, and mood fields
- [x] Rotate art direction, scene, composition, and recent preset history without a new DB column
- [x] Front-load faceless framing, silhouette, garment structure, proportion, and pose in text/FLUX JSON prompts
- [x] Replace generic scene catalog with a small controlled scene vocabulary
- [x] Run exactly one Cloudflare live image for each of SOFT_BOYFRIEND, MINIMAL, AMEKAJI, and OTAKU_GRUNGE

Status: **IMPLEMENTED; LIVE CALIBRATION FOLLOW-UP REQUIRED**. The four-call smoke run produced
valid files. SOFT_BOYFRIEND and MINIMAL were neck-down; AMEKAJI used an allowed rear head; the
OTAKU_GRUNGE `STREET_SNAP` sample exposed a face. No retry was made. The STREET_SNAP positive
head-outside framing was strengthened and unit-tested, but it has not been revalidated live because
the four-call budget was exhausted. PHASE 6 remains unstarted.

## PHASE 5.3 — Reference image conditioning spike

- [x] Confirm documented FLUX.2 klein 4B multipart multi-reference, guidance, and seed support
- [x] Create Git-ignored, head-out, aspect-preserving PNG derivatives below 512×512
- [x] Add Cloudflare-only optional `input_image_0` / `input_image_1` forwarding with no more than two references
- [x] Front-load copy-safe visual-grammar reference instruction without changing text-only behavior
- [x] Run exactly one reference-conditioned SOFT_BOYFRIEND and one OTAKU_GRUNGE live image

Status: **IMPLEMENTED; CALIBRATION RESULT RECORDED**. The SOFT_BOYFRIEND sample retained a
chin/jaw area and therefore failed the faceless hard policy. The OTAKU_GRUNGE rear sample kept
the face invisible, but expressed a cleaner tailored look than the intended faded/alternative
streetwear range. No retry was performed. These results do not start PHASE 6 or add Vision QC.

## PHASE 5.4 — Controlled klein 4B vs 9B quality A/B spike

- [x] Verify current Cloudflare klein 9B model, multipart reference, seed, and pricing documentation
- [x] Keep klein 4B as the V1 default while allowing explicit klein 9B calibration configuration
- [x] Tighten relaxed garment drape, soft silhouette, OTAKU hero, bag, and art-direction policies
- [x] Mock-test 9B endpoint, existing 4B behavior, shared seed/reference request fields, and model-only variation
- [x] Generate the bounded SOFT_BOYFRIEND and OTAKU_GRUNGE 4B/9B pairs for human review

Status: **IMPLEMENTED; HUMAN EVALUATION COMPLETE**. The 9B samples improved texture/rendering,
but did not resolve style accuracy or art-direction calibration. The 4B default remains unchanged;
PHASE 6 remains unstarted.

## PHASE 4.6 / PHASE 5.5 — Garment vocabulary and editorial validation

- [x] Calibrate controlled recipe vocabulary for garment structure, lower structure, texture,
  layering role, and footwear shape without a migration
- [x] Rotate SOFT_BOYFRIEND away from the gray/navy/white office-casual fallback
- [x] Rotate OTAKU_GRUNGE across detailed/graphic uppers and at least four lower families,
  with bag restraint and simple blazer-history avoidance
- [x] Validate two reference-conditioned klein 4B samples only after tests pass

Status: **IMPLEMENTED; HUMAN REVIEW REQUIRED**. Both bounded klein 4B outputs were technically
generated, but each exposed facial regions. No retry was made, and this calibration does not start
PHASE 6, add Vision QC, or change the default model. See
[`docs/EDITORIAL_GENERATION_VALIDATION.md`](docs/EDITORIAL_GENERATION_VALIDATION.md).

## Working protocol

- 한 Codex 작업은 사용자가 명시하지 않는 한 하나의 Phase 또는 하나의 좁은 체크리스트 묶음만 다룬다.
- 작업 전에 현재 Git 상태, 관련 코드, 기존 테스트를 확인한다.
- 선택하지 않은 Phase의 feature, dependency, abstraction을 미리 추가하지 않는다.
- 완료 전에 관련 test/lint/format과 `CODE_REVIEW.md` self-review를 수행한다.
- 체크박스는 구현과 검증이 모두 끝난 뒤에만 완료한다.

## PHASE 0 — Repository and Codex foundation

- [x] 저장소와 Git 상태 조사 및 Git 초기화
- [x] 간결한 root `AGENTS.md`와 제품 상세 문서 분리
- [x] architecture와 directory structure 문서화
- [x] `.gitignore`와 secret 없는 `.env.example` 검증
- [x] Phase 단위 계획과 `CODE_REVIEW.md` 작성
- [x] repo-scoped `.codex/config.toml` 필요성 평가: 현재는 기본값 유지
- [x] project-local Skill/MCP/Plugin/Hook/Subagent/Automation 평가: 반복 ROI가 없어 저장소에는 추가하지 않음 (전역 `find-skills` 및 이전 요청으로 설치된 `python-project-structure`은 저장소 설정이 아님)
- [x] production code와 runtime dependency를 추가하지 않음

Exit: 문서가 일관되고 secret/로컬 생성물은 Git에서 제외되며 다음 작업이 PHASE 1로 명확하다.

## PHASE 1 — Project foundation

- [x] Python 3.12+ `src/` layout과 최소 `pyproject.toml`
- [x] FastAPI app factory와 health endpoint
- [x] Pydantic settings, fail-fast validation, secret redaction
- [x] PostgreSQL/SQLAlchemy/Alembic baseline
- [x] pytest fixture와 deterministic clock
- [x] Ruff lint/format 및 canonical 명령 구성
- [x] 최소 Dockerfile/Compose와 README 실행 절차
- [x] Docker daemon E2E: build, PostgreSQL 기동, `alembic upgrade head`, `/health` 확인

Exit: fresh checkout에서 app/DB가 기동되고 health, migration, test, lint가 통과한다. (완료)

## PHASE 2 — Weather

- [x] 구현 시점에 문서화된 provider 선택
- [x] 서울/Asia-Seoul의 “다음 날” 경계와 typed schema
- [x] timeout, bounded retry, error mapping
- [x] `WeatherSnapshot`과 provenance 저장
- [x] valid/provider failure/missing field tests

Exit: LLM 없이 실제 예보를 정규화하고 provider 장애를 안전하게 처리한다. (완료)

## PHASE 3 — Style and occasion

- [x] 네 style preset과 정확한 rotation
- [x] DB-backed selection과 restart persistence
- [x] 작은 occasion/mood 집합과 deterministic selection policy
- [x] 최근 style/occasion/mood 조합 이력 조회
- [x] rotation/restart/idempotency tests

Exit: 중복 실행과 재시작에도 다음 스타일이 일관되다. (완료)

## PHASE 4 — OutfitRecipe

- [x] Pydantic recipe/garment schemas
- [x] 온도·일교차·비 규칙
- [x] structured generation과 validation
- [x] recipe signature variation/history
- [x] invalid output의 bounded correction
- [x] schema/temperature/style tests

Exit: 검증된 recipe만 이미지 단계로 전달된다. (완료)

## PHASE 5 — Image generation

- [x] Cloudflare Workers AI 공식 REST API 및 `@cf/black-forest-labs/flux-2-klein-4b` 확인
- [x] env model configuration과 startup validation
- [x] recipe 기반 faceless editorial prompt
- [x] timeout/error handling과 generation log
- [x] 4:5, 1080×1350 normalization
- [x] fake 기반 result/size/error tests

Exit: provenance를 가진 Instagram-ready 후보 이미지를 생성한다. (구현 완료; Live Cloudflare image smoke test pending; OpenAI smoke test optional)

## PHASE 6 — Vision QC

- [ ] structured QC schema와 hard-fail rules
- [ ] 실패 이유 기반 최대 1회 재생성
- [ ] 두 번째 실패의 `REVIEW_REQUIRED` 전이
- [ ] face/chin/jaw/anomaly/retry tests

Exit: hard-fail 이미지는 carousel/게시 단계로 진행하지 않는다.

## PHASE 7 — Carousel

- [ ] 4–6 slide editorial template
- [ ] weather/detail/style guide layouts
- [ ] overflow/safe area 처리
- [ ] commerce 문구 금지 검사
- [ ] 1080×1350 output tests

Exit: recipe/weather/image로 일관된 magazine carousel을 만든다.

## PHASE 8 — Caption

- [ ] 한국어 magazine schema/prompt
- [ ] caption history와 반복 검사
- [ ] 광고성·commerce 표현 검사
- [ ] invalid output/provider failure 처리와 tests

Exit: 금지 표현과 반복을 제어한 caption을 만든다.

## PHASE 9 — Minimal Admin approval

- [ ] preview와 APPROVE/REGENERATE/REJECT
- [ ] 인증·권한·CSRF·double-submit 방어
- [ ] 서버 측 상태 전이와 audit history
- [ ] route/state tests

Exit: 승인되지 않은 콘텐츠는 게시할 수 없다.

## PHASE 10 — Official Instagram publishing

- [ ] 구현 시점 Meta 공식 문서/account 요구 확인
- [ ] 공식 API publisher와 carousel flow
- [ ] `content_uuid` idempotency guard
- [ ] remote media ID와 timeout reconciliation
- [ ] success/timeout/duplicate/credential tests

Exit: 승인 콘텐츠만 공식 API로 정확히 한 번 게시된다.

## PHASE 11 — Scheduler and recovery

- [ ] Asia/Seoul prepare/publish schedule
- [ ] DB lock/constraint 기반 중복 job 방지
- [ ] restart/stale-state recovery
- [ ] daily/restart/duplicate/concurrency tests

Exit: process restart와 scheduler 중복에도 콘텐츠·게시가 중복되지 않는다.

## PHASE 12 — E2E dry run and deployment docs

- [ ] `DRY_RUN=true` Weather → Preview E2E
- [ ] 게시만 mock 처리됨을 검증
- [ ] 주요 실패/recovery E2E
- [ ] secret, migration, backup, health runbook
- [ ] Docker Compose deployment 문서
- [ ] 30–50개 콘텐츠 품질 평가 절차

Exit: fresh environment에서 문서만 따라 dry run을 재현하고 V1 Definition of Done을 검증한다.
