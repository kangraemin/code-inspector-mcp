# Step 1: 프로젝트 스캐폴딩

## TC

| TC | 검증 항목 | 기대 결과 | 상태 |
|----|----------|----------|------|
| TC-01 | pyproject.toml 존재 및 유효 | `uv run python -c "import code_inspector"` 성공 | ✅ |
| TC-02 | entry point 등록 | `uv run code-inspector --help` 또는 import 가능 | ✅ |
| TC-03 | .gitignore 존재 | __pycache__, .venv, *.egg-info 포함 | ✅ |

## 구현 내용
- pyproject.toml: hatchling 빌드, fastmcp>=2.0 + pydantic>=2.0 의존성, entry point 등록
- .gitignore: Python 표준 패턴
- src/code_inspector/__init__.py, inspectors/__init__.py: 패키지 초기화
- src/code_inspector/server.py: FastMCP stub (main 함수)

## 실행출력

TC-01: `uv run python -c "import code_inspector; print('TC-01: import OK')"`
→ TC-01: import OK

TC-02: `uv run python -c "from code_inspector.server import main; print('TC-02: entry point OK')"`
→ TC-02: entry point OK

TC-03: `grep -c '__pycache__\|\.venv\|egg-info' .gitignore`
→ 3
