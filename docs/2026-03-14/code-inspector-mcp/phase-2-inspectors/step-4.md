# Step 4: Android Lint Inspector

## TC

| TC | 검증 항목 | 기대 결과 | 상태 |
|----|----------|----------|------|
| TC-01 | AndroidLintInspector import | import 성공 | ✅ |
| TC-02 | XML 파싱 | Android Lint XML → Issue 리스트 변환 | ✅ |
| TC-03 | gradlew 없으면 graceful | available=False, error 메시지 | ✅ |

## 구현 내용
- android_lint.py: AndroidLintInspector (gradlew lintDebug, XML 파싱, severity 매핑, 300초 타임아웃)

## 실행출력

Output:
TC-01: import OK
TC-02: 2 issues, rules=['HardcodedText', 'ObsoleteSdkInt'], sevs=['warning', 'error']
TC-03: available=False, error=True
