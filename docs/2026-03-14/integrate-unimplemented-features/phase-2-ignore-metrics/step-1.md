# Step 1: ignore 패턴 필터링 적용

## TC

| TC | 검증 항목 | 기대 결과 | 실제 결과 |
|----|----------|----------|----------|
| TC-01 | _should_ignore 함수 존재 | server 모듈에서 접근 가능 | ✅ |
| TC-02 | generated 경로 이슈 필터링 | `**/generated/**` 패턴에 매칭되는 파일 제외 | ✅ |
| TC-03 | build 경로 이슈 필터링 | `**/build/**` 패턴에 매칭되는 파일 제외 | ✅ |
| TC-04 | 일반 파일은 필터링 안 됨 | `src/main/MyFile.kt`는 유지 | ✅ |

## 실행 결과

TC-01~04: `.venv/bin/python -c` 통합 테스트
→
```
TC-01: True
TC-02: True
TC-03: True
TC-04 (should be False): False
```
