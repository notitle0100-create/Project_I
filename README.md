# SEOUL MEN'S DAILY EDIT

## Image provider update

V1 defaults to Cloudflare Workers AI with
`@cf/black-forest-labs/flux-2-klein-4b`. It requests `1080x1350` directly and
stores only image metadata and the local file path. OpenAI Image API remains an
optional provider selected with `IMAGE_PROVIDER=openai`; it is not required for
V1. Configure credentials only in the local `.env` or deployment secret store.

Cloudflare live generation is limited to one image per request. It never
automatically falls back to OpenAI or a paid mode when quota or account limits
are reached.

서울의 다음 날 날씨에 맞는 20대 남성 데일리 코디를 하루 하나 제작해, 검수 후 Instagram fashion magazine 형식으로 게시하는 modular monolith 프로젝트다.

현재 상태는 **PHASE 5 — AI Image Generation 구현 완료**다. Vision QC, Instagram, Admin UI 도메인 기능은 아직 없다. Live Cloudflare image smoke test는 credential 설정 후 별도로 수행한다.

## Project documents

- [`AGENTS.md`](AGENTS.md): Codex가 항상 따라야 할 짧은 영구 운영 규칙
- [`docs/PRODUCT_SPEC.md`](docs/PRODUCT_SPEC.md): 제품·콘텐츠 상세 규칙
- [`PLAN.md`](PLAN.md): 현재 Phase와 단계별 체크리스트
- [`CODE_REVIEW.md`](CODE_REVIEW.md): 구현 후 공통 리뷰 기준

## V1 flow

`Weather → Style/Occasion → OutfitRecipe → Image → Vision QC → Carousel/Caption → Admin approval → Official Instagram publish`

V1은 `src/` layout의 modular monolith로 구성하며 `weather`, `styling`, `outfits`, `images`, `qc`, `editorial`, `content`, `publishing`, `scheduling`을 얕은 도메인 패키지로 분리한다. 실제 디렉터리는 해당 Phase에서 필요할 때만 생성한다.

## Recommended Codex workflow

1. 새 작업에서 `AGENTS.md`와 `PLAN.md`의 현재 Phase를 확인한다.
2. 한 번에 하나의 Phase 또는 좁은 체크리스트 묶음만 요청한다.
3. 변경 전 Git 상태와 baseline test를 확인한다.
4. 작은 diff로 구현하고 관련 test/lint를 실행한다.
5. `CODE_REVIEW.md` 기준으로 self-review한다.
6. 검증된 단위만 commit해 복구 지점을 남긴다.

repo-scoped `.codex/config.toml`은 현재 추가하지 않았다. 기본 sandbox/approval 정책을 유지하고, MCP·Plugin·Hook·Subagent·Automation·project-local Skill도 반복 작업의 ROI가 확인될 때만 검토한다.

## Configuration

구현 Phase에서는 `.env.example`을 복사해 로컬 `.env`를 만들고 실제 credential은 로컬 또는 배포 secret store에만 입력한다. `.env`와 로컬 생성물은 Git에서 제외된다.

## Weather

PHASE 2는 [Open-Meteo Forecast API](https://open-meteo.com/en/docs)를 사용한다. API key 없이
서울 좌표와 `Asia/Seoul` 기준 일별 최고/최저기온, 강수확률, WMO weather code를 제공하므로
하루 1회 다음 날 예보에 적합하다. provider-specific HTTP/응답 처리는 `weather/provider.py`에만
두고, 다른 모듈은 정규화된 `WeatherSnapshot`과 `get_tomorrow_weather()`를 사용한다.

Weather credential은 필요하지 않으므로 `.env.example`에 추가할 변수는 없다.

## Style context

`select_style_context(target_date, weather_snapshot, repository)`는 저장된 선택 이력을 기준으로
`SOFT_BOYFRIEND → MINIMAL → AMEKAJI → OTAKU_GRUNGE` 순서를 반복한다. 같은 `target_date`는
기존 결과를 반환하며, 최근 8개의 style/occasion/mood 조합을 피한다. Occasion과 mood는 작은
controlled vocabulary 및 날씨 규칙으로만 결정하며, LLM·성과 기반 최적화·의상 선택은 포함하지 않는다.

## Outfit recipes

`generate_outfit_recipe(weather_snapshot, style_selection, repository)`는 두 입력의 target date가 일치할 때만 Pydantic `OutfitRecipe`를 만든다. 네 스타일의 결정론적 템플릿에 temperature band, 일교차, 비 규칙을 적용하고, 최근 8개 recipe signature를 참조해 중복을 줄인다. 같은 target date는 저장된 recipe를 그대로 반환한다. 실제 브랜드·상품·가격·구매 링크와 외부 API/LLM/image 호출은 포함하지 않는다.

## Image generation

PHASE 5는 [Cloudflare Workers AI](https://developers.cloudflare.com/workers-ai/)의 `@cf/black-forest-labs/flux-2-klein-4b`를 V1 기본 모델로 사용한다. `CLOUDFLARE_IMAGE_MODEL`과 `CLOUDFLARE_IMAGE_SIZE`로 교체 가능하며 `1080x1350`을 직접 생성한다. OpenAI Image API의 `gpt-image-2`는 `IMAGE_PROVIDER=openai`일 때만 사용하는 optional provider다. 생성 metadata와 상태만 DB에 저장하고 원본 binary는 Git-ignored `data/generated/YYYY-MM-DD/`에 저장한다. API key/token은 환경 변수에서만 읽으며 저장·로그 기록하지 않는다.

## Local development

Python 3.12+와 Docker Compose가 필요하다.

```powershell
Copy-Item .env.example .env
# .env의 POSTGRES_PASSWORD를 로컬 전용 값으로 설정
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
docker compose up --build -d
docker compose exec app alembic upgrade head
```

`GET http://localhost:8000/health`는 `{"status":"ok"}`를 반환한다.

```powershell
python -m pytest
python -m ruff check .
python -m ruff format --check .
```

호스트에서 FastAPI를 직접 실행할 때는 `.env`에 `DATABASE_URL`을 별도로 설정한 뒤 다음을 사용한다.

```powershell
uvicorn seoul_mens_daily_edit.main:app --reload
```
