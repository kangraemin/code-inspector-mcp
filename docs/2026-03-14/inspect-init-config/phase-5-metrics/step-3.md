# Step 3: coverage.py

## TC

| TC | 검증 항목 | 기대 결과 | 상태 |
|----|----------|----------|------|
| TC-01 | JaCoCo XML 파싱 | LINE counter에서 커버리지 계산 | ✅ |
| TC-02 | 리포트 없으면 graceful | available=False 반환 | ✅ |
| TC-03 | 임계값 비교 | min_percent 미달 시 passed=False | ✅ |

## 구현 내용
- coverage.py: JaCoCo XML 파싱 (LINE counter), 커버리지 % 계산, 리포트 자동 탐색

## 실행출력

Output:
TC-01: coverage=80.0%, covered=80, missed=20
TC-02: available=False, error=True
TC-03: coverage=40.0%, passed=False
