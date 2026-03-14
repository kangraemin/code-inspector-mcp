# Step 3: ktlint Inspector

## TC

| TC | 검증 항목 | 기대 결과 | 상태 |
|----|----------|----------|------|
| TC-01 | KtlintInspector import | import 성공 | ✅ |
| TC-02 | JSON 파싱 | ktlint JSON → Issue 리스트 변환 | ✅ |
| TC-03 | 미설치 시 graceful | available=False, error 메시지 | ✅ |

## 구현 내용
- ktlint.py: KtlintInspector (ktlint --reporter=json, JSON 파싱, 전부 warning 레벨)

## 실행출력

TC-01: import OK
TC-02: 1 issues, rule=no-wildcard-imports, sev=warning
TC-03: available=False, error=True
