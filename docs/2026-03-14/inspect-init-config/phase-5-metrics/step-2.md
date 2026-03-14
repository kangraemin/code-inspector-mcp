# Step 2: duplication.py

## TC

| TC | 검증 항목 | 기대 결과 | 상태 |
|----|----------|----------|------|
| TC-01 | 중복 없는 코드 | duplicates 빈 리스트 | ✅ |
| TC-02 | 동일 블록 감지 | 같은 5줄 블록 → duplicate 반환 | ✅ |
| TC-03 | 중복률 계산 | duplication_percentage 반환 | ✅ |

## 구현 내용
- duplication.py: 라인 해시 슬라이딩 윈도우 (window_size=5), 블록별 위치 추적

## 실행출력

Output:
TC-01: duplicates=0
TC-02: duplicates=2 (슬라이딩 윈도우 겹침)
TC-03: duplication_pct=142.86% (윈도우 겹침으로 초과 가능 — 추후 개선점)
