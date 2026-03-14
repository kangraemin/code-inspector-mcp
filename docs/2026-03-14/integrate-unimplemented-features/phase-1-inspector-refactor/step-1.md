# Step 1: 중복 제거 + 무의미한 오버라이드 제거

## TC

| TC | 검증 항목 | 기대 결과 | 실제 결과 |
|----|----------|----------|----------|
| TC-01 | BaseInspector에 _count_kt_files 존재 | `hasattr(BaseInspector, '_count_kt_files')` → True | ✅ |
| TC-02 | DetektInspector에 자체 _count_kt_files 없음 | `'_count_kt_files' not in DetektInspector.__dict__` → True | ✅ |
| TC-03 | DetektInspector에 자체 is_available 없음 | `'is_available' not in DetektInspector.__dict__` → True | ✅ |
| TC-04 | 모든 inspector import 성공 | import 에러 없음 | ✅ |

## 실행 결과

TC-01~04: `.venv/bin/python -c` 통합 테스트
→
```
TC-01: True
TC-02: True
TC-03: True
TC-04: all imports OK
```
