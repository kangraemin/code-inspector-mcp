# Step 3: 점수 계산 로직

## TC

| TC | 검증 항목 | 기대 결과 | 상태 |
|----|----------|----------|------|
| TC-01 | 이슈 없으면 만점 | calculate_score([], 10) == 10.0 | ✅ |
| TC-02 | error 감점 | error 3개 + 10파일 → 10.0 - (0.3*3)*(10/10) = 9.1 | ✅ |
| TC-03 | 바닥 0점 | 대량 error → 0.0 이상 | ✅ |
| TC-04 | 파일 수 정규화 | 동일 이슈 수, 파일 많으면 점수 높음 | ✅ |

## 구현 내용
- scoring.py: SEVERITY_WEIGHTS 상수 + calculate_score 함수
- 10점 만점에서 이슈별 감점, 파일 수 대비 정규화, 0.0 바닥

## 실행출력

TC-01: `calculate_score([], 10)` → 10.0 ✅
TC-02: `calculate_score(3 errors, 10 files)` → 9.1 ✅
TC-03: `calculate_score(1000 errors, 5 files)` → 0.0 (바닥) ✅
TC-04: `5files=9.0, 50files=9.9, more_files_higher=True` ✅
