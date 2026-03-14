# Step 1: FastMCP 서버 + inspect 도구

## TC

| TC | 검증 항목 | 기대 결과 | 상태 |
|----|----------|----------|------|
| TC-01 | server import | from code_inspector.server import mcp 성공 | ✅ |
| TC-02 | inspect 도구 등록 | mcp에 inspect tool 등록 확인 | ✅ |
| TC-03 | inspect 실행 (도구 미설치) | 3개 도구 모두 available=False, 결과 반환 | ✅ |

## 구현 내용
- server.py: FastMCP 서버, inspect 도구(path/scope/fix/threshold), 3개 inspector 병렬 실행, 점수 통합, fix_suggestions 생성

## 실행출력

Output:
TC-01: import OK
TC-02: tool name=inspect
TC-03: unavailable=['detekt', 'ktlint', 'android_lint'], overall=0.0, passed=False
