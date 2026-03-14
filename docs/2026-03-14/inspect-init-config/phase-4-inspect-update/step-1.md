# Step 1: inspect 설정 반영

## TC

| TC | 검증 항목 | 기대 결과 | 상태 |
|----|----------|----------|------|
| TC-01 | scoring.py 커스텀 weights | 다른 weights 전달 시 점수 변경 | ✅ |
| TC-02 | inspector enable/disable | disabled inspector 실행 안 함 | ✅ |
| TC-03 | 가중 평균 | weight 반영된 overall score | ✅ |
| TC-04 | 설정 없으면 기존 동작 | 하위 호환 유지 | ✅ |

## 구현 내용
- scoring.py: calculate_score에 severity_weights 파라미터 추가
- server.py: inspect에 설정 로드, enable/disable, 가중 평균, tool_name_map 추가

## 실행출력

Output:
TC-01: default=9.7, custom=9.0, different=True
TC-02: tools=['detekt', 'ktlint'] (android_lint disabled)
TC-03: threshold=8.0 (from config)
TC-04: tools=['detekt', 'ktlint', 'android_lint'], threshold=7.0 (defaults)
