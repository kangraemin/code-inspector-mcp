# Step 1: config.py

## TC

| TC | 검증 항목 | 기대 결과 | 상태 |
|----|----------|----------|------|
| TC-01 | CodeInspectorConfig 기본값 생성 | 모든 필드 기본값으로 인스턴스 생성 | ✅ |
| TC-02 | save_config + load_config | 저장 후 로드 시 동일한 config 반환 | ✅ |
| TC-03 | 파일 없을 때 load_config | None 반환 | ✅ |
| TC-04 | 기본값이 현재 동작과 호환 | threshold=7.0, 모든 inspector enabled, 기존 severity_weights | ✅ |

## 구현 내용
- config.py: CodeInspectorConfig + InspectorConfig + MetricsConfig + ArchitectureConfig Pydantic 모델
- load_config / save_config / deep_merge 유틸

## 실행출력

Output:
TC-01: threshold=7.0, inspectors=['detekt', 'ktlint', 'android_lint']
TC-02: saved=True, match=True
TC-03: load_config nonexistent = None
TC-04: threshold=True, weights={'error': 0.3, 'warning': 0.1, 'info': 0.05}, all_enabled=True
