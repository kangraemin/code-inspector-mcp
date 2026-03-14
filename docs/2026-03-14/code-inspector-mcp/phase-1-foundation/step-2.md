# Step 2: Pydantic 데이터 모델

## TC

| TC | 검증 항목 | 기대 결과 | 상태 |
|----|----------|----------|------|
| TC-01 | Issue 모델 생성 | Issue 인스턴스 생성 + JSON 직렬화 성공 | ✅ |
| TC-02 | ToolResult 모델 생성 | ToolResult 인스턴스 생성 성공 | ✅ |
| TC-03 | InspectionResult 모델 생성 | 전체 결과 모델 직렬화 성공 | ✅ |

## 구현 내용
- models.py: Issue, ToolResult, InspectionResult Pydantic 모델 정의
- Issue: file, line, column, rule, message, severity, source
- ToolResult: tool, score, issues, available, error
- InspectionResult: path, scope, overall_score, passed, threshold, tool_results, summary

## 실행출력

TC-01: `Issue(file='Main.kt', line=10, rule='MagicNumber', message='magic', severity='error', source='detekt')`
→ {"file":"Main.kt","line":10,"column":null,"rule":"MagicNumber","message":"magic","severity":"error","source":"detekt"}

TC-02: `ToolResult(tool='detekt', score=8.5, issues=[issue])`
→ {"tool":"detekt","score":8.5,"issues":[...]} — 성공

TC-03: `InspectionResult(path='.', scope='changed', overall_score=8.5, passed=True, threshold=7.0, ...)`
→ {"path":".","scope":"changed","overall_score":8.5,"passed":true,...} — 성공
