# Repository instructions

이 파일은 저장소 전체에 적용되는 Codex 영구 운영 규칙이다. 제품 상세는 [`docs/PRODUCT_SPEC.md`](docs/PRODUCT_SPEC.md), 구현 순서와 현재 Phase는 [`PLAN.md`](PLAN.md), 리뷰 기준은 [`CODE_REVIEW.md`](CODE_REVIEW.md)를 따른다.

## 목적과 V1 범위

- 서울의 다음 날 날씨에 맞는 20대 성인 남성 데일리 코디를 하루 하나 제작하는 faceless Instagram 패션 매거진이다.
- V1은 `날씨 → 스타일/상황 → OutfitRecipe → 이미지 → Vision QC → Carousel/Caption → 관리자 승인 → 공식 Instagram 게시`의 modular monolith다.
- `DRY_RUN=true`에서는 preview까지 실행하고 게시만 mock 처리한다.
- 현재 Phase와 허용 작업은 `PLAN.md`가 결정한다. 한 Codex 작업에서는 사용자가 명시하지 않는 한 **하나의 Phase 또는 하나의 좁은 체크리스트 묶음만** 수행한다.

## 영구 제외 범위

- 여성 코디·여성 계정
- 실제 브랜드, 판매 상품, SKU, 가격, 예산, 재고, 구매 링크, affiliate, 협찬 자동 삽입, commerce
- 쇼핑몰 연동과 이를 위한 crawler/resolver/DB model/API adapter
- Selenium/Playwright 로그인 게시, username/password 자동화, 비공식 Instagram API
- auto-like/follow/unfollow/comment/DM
- 필요성이 검증되지 않은 microservices, Kafka, Kubernetes, 복잡한 event bus/frontend, vector DB, custom image pipeline

## 문서와 디렉터리

```text
.
├── AGENTS.md                 # 영구 Codex 운영 규칙
├── PLAN.md                   # Phase 체크리스트와 진행 상태
├── CODE_REVIEW.md            # 공통 리뷰 기준
├── README.md
├── docs/PRODUCT_SPEC.md      # 제품·콘텐츠 상세 규칙
├── src/seoul_mens_daily_edit/
│   ├── api/                  # FastAPI + 최소 Admin UI
│   ├── core/                 # settings, logging, clock
│   ├── db/                   # SQLAlchemy 연결부
│   ├── weather/
│   ├── styling/
│   ├── outfits/
│   ├── images/
│   ├── qc/
│   ├── editorial/
│   ├── content/
│   ├── publishing/
│   └── scheduling/
├── tests/                    # src 도메인과 평행한 pytest 구조
├── alembic/                  # PHASE 1부터
└── var/                      # 로컬 생성물; Git 제외
```

아직 없는 디렉터리나 파일은 해당 Phase에서 실제로 필요할 때만 만든다.

## 실행·검증 명령

현재 PHASE 0에는 실행 가능한 앱, test, lint 명령이 없다. 성공하지 않은 명령을 성공했다고 보고하지 않는다.

PHASE 1에서 다음 명령을 project dependency와 함께 실제로 구성하고 README에 확정한다.

- 테스트: `python -m pytest`
- lint: `python -m ruff check .`
- format 검사: `python -m ruff format --check .`

작업 전후에는 `git status --short --branch`와 관련 diff를 확인한다. 코드 변경 후에는 최소한 변경 영역의 테스트를 실행하고, 공통 기반·상태 전이·외부 API 경계를 바꿨다면 전체 테스트도 실행한다.

## Coding conventions

- Python 3.12+, `src/` layout, absolute import, 명확한 type hint를 사용한다.
- 도메인별 얕은 패키지를 유지하고 파일 하나에 관련 없는 책임을 섞지 않는다.
- FastAPI handler는 얇게, 비즈니스 규칙은 도메인 서비스에 둔다.
- 입력과 외부 API 응답은 경계에서 Pydantic으로 검증한다.
- 외부 서비스는 작은 typed adapter 뒤에 두되 범용 provider framework를 미리 만들지 않는다.
- workflow 상태, rotation, 승인, 복구, 게시 idempotency는 DB를 기준으로 한다.
- schema 변경에는 Alembic migration과 migration 검증을 함께 둔다.
- bug fix에는 가능하면 실패를 재현하는 regression test를 먼저 추가한다.
- 새 production dependency는 현재 Phase에서 필요한 이유가 명확할 때만 추가한다.

## Security rules

- secret은 `.env` 또는 배포 secret store에서만 주입한다. `.env.example`에는 실제 값이나 그럴듯한 예시 token을 넣지 않는다.
- API key, Meta token, DB password, auth header, session secret을 source, Git, fixture, 로그, exception에 남기지 않는다.
- 외부 API는 HTTPS, 인증서 검증, timeout, bounded retry, 명시적 error handling을 사용한다.
- side effect 재시도는 idempotency를 보장해야 한다.
- SQL은 SQLAlchemy parameter binding을 사용하고 문자열 조합 query를 금지한다.
- Admin mutation에는 해당 Phase에서 인증·권한 검사·CSRF 방어를 포함한다.

## 반드시 지킬 규칙

- 작업 전에 `AGENTS.md`, 선택한 `PLAN.md` Phase, 관련 spec을 읽는다.
- 선택한 Phase 밖의 feature, refactor, 추상화, dependency를 함께 구현하지 않는다.
- 기존 동작과 공개 계약을 임의로 깨뜨리지 않는다. 변경 전 baseline과 관련 테스트를 확인한다.
- 관련 테스트가 실패한 상태로 완료 처리하지 않는다. 실행할 수 없으면 이유와 미검증 범위를 보고한다.
- 사용자 변경을 덮어쓰거나 삭제하지 않는다.
- `git reset --hard`, 강제 checkout/clean, force-push, history rewrite 등 파괴적 Git 명령을 사용하지 않는다.
- 모델/provider/auth/secrets를 repository에 하드코딩하지 않는다.
- `.codex/config.toml`, Skill, MCP, Plugin, Hook, Subagent, Automation은 반복 작업을 줄이는 명확한 ROI와 사용자 범위가 없으면 추가하지 않는다.
- 리뷰는 `CODE_REVIEW.md`를 기준으로 하며 발견 사항을 수정하기 전 요청 범위를 확인한다.

## Definition of Done

- 선택한 `PLAN.md` 체크리스트와 acceptance criteria를 충족한다.
- 관련 테스트와 lint/format 검사가 통과한다. 아직 명령이 없는 PHASE 0은 문서·Git·secret 검증으로 대신한다.
- functional regression, security issue, unsafe secret handling, scope creep가 없다.
- 코드·migration·설정·문서가 실제 동작과 일치한다.
- diff가 선택한 Phase에 한정되고 작고 리뷰 가능하다.
- `CODE_REVIEW.md` self-review를 완료하고 Git이 안전한 commit-ready 상태다.
