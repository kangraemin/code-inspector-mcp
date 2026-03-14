# Step 2: metrics 모듈을 inspect 도구에 연결

## TC

| TC | 검증 항목 | 기대 결과 | 실제 결과 |
|----|----------|----------|----------|
| TC-01 | metrics import 성공 | server.py에서 complexity/coverage/duplication import 에러 없음 | ✅ |
| TC-02 | _collect_kt_files 함수 존재 | server 모듈에서 접근 가능 | ✅ |
| TC-03 | complexity 분석 동작 | analyze_complexity 호출 결과에 functions 키 존재 | ✅ |
| TC-04 | server import 정상 | `from code_inspector.server import mcp` 성공 | ✅ |

## 실행 결과

TC-01~04: `.venv/bin/python -c` 통합 테스트
→
```
TC-01: imports OK
TC-02: True
TC-03: True - functions: [{'name': 'test', 'line': 1, 'complexity': 2, 'lines': 3}]
TC-04: mcp import OK
```
