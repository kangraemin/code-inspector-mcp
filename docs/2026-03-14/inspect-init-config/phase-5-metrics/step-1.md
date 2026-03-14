# Step 1: complexity.py

## TC

| TC | 검증 항목 | 기대 결과 | 상태 |
|----|----------|----------|------|
| TC-01 | 단순 함수 복잡도 | if/when 없으면 복잡도 1 | ✅ |
| TC-02 | 분기 있는 함수 | if 3개 → 복잡도 4 | ✅ |
| TC-03 | 임계값 초과 감지 | max_per_function 초과 시 경고 | ✅ |

## 구현 내용
- complexity.py: regex 기반 함수 감지 + 분기 키워드 카운트 (if/when/for/while/catch/&&/||)

## 실행출력

Output:
TC-01: complexity=1
TC-02: complexity=4
TC-03: violations=1
