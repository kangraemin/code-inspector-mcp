# Step 2: detekt Inspector

## TC

| TC | 검증 항목 | 기대 결과 | 상태 |
|----|----------|----------|------|
| TC-01 | DetektInspector import | import 성공 | ✅ |
| TC-02 | XML 파싱 | checkstyle XML → Issue 리스트 변환 | ✅ |
| TC-03 | 미설치 시 graceful | available=False, score=0, error 메시지 | ✅ |

## 구현 내용
- detekt.py: DetektInspector (detekt-cli/gradlew detekt, checkstyle XML 파싱, severity 매핑)

## 실행출력

TC-01: import OK
TC-02: 2 issues, first=detekt.style.MagicNumber, sev=error
TC-03: available=False, error=True
