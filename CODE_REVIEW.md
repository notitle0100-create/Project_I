# Code review checklist

모든 리뷰는 `AGENTS.md`, 현재 `PLAN.md` Phase, 관련 제품 spec을 기준으로 한다. 스타일 선호보다 사용자 영향과 실제 결함을 우선하며, 발견 사항은 재현 조건·영향·근거와 함께 심각도 순으로 보고한다.

## Required checks

- [ ] **Functional bugs:** 요구 동작, 상태 전이, 경계값, 시간대가 정확한가?
- [ ] **Regressions:** 기존 공개 계약과 통과하던 흐름을 깨뜨리지 않는가?
- [ ] **Security:** 인증·권한·CSRF·injection·SSRF·민감정보 노출 위험이 없는가?
- [ ] **Error handling:** timeout, 외부 API 실패, partial failure, retry exhaustion이 안전한 상태로 끝나는가?
- [ ] **Duplicate logic:** 같은 정책이나 변환이 여러 위치에서 서로 다르게 구현되지 않았는가?
- [ ] **Unnecessary complexity:** 현재 Phase에 필요 없는 abstraction, dependency, service, configuration이 없는가?
- [ ] **Missing tests:** 정상·실패·경계·regression 경로를 검증하는 테스트가 있는가?
- [ ] **Secret handling:** key/token/password/auth header가 source, fixture, log, exception, generated artifact에 없는가?
- [ ] **Scope creep:** diff가 선택한 Phase와 요청 범위 안에 있는가?

## Project-specific checks

- [ ] 날씨 값은 실제 provider에서 오며 LLM이 생성하지 않는가?
- [ ] faceless hard fail과 이미지 재생성 1회 제한을 우회할 수 없는가?
- [ ] 상태 전이가 검증되고 이력과 실패 이유가 저장되는가?
- [ ] 승인 전 게시와 timeout/restart 후 중복 게시가 차단되는가?
- [ ] 실제 브랜드·상품·가격·구매 링크·비공식 Instagram 자동화가 유입되지 않았는가?

## Verification

- [ ] 변경 전 baseline 또는 기존 테스트 결과를 확인했다.
- [ ] 변경 영역의 test를 실행했다.
- [ ] 공통 기반·workflow·DB·외부 API 경계를 바꿨다면 전체 test를 실행했다.
- [ ] lint/format 검사를 실행했다.
- [ ] migration/config/documentation이 실제 코드와 일치한다.
- [ ] 실행하지 못한 검증은 이유와 잔여 위험을 명시했다.

차단 결함이 없고 필요한 검증이 끝났을 때만 승인한다. 리뷰만 요청된 경우 사용자 승인 없이 수정·commit·push하지 않는다.
