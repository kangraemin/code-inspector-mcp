# code-inspector MCP 서버

## Context
Claude Code가 작성한 Android/Kotlin 코드 품질이 불만족스러울 때, **외부 정적 분석 도구**(detekt, ktlint, Android Lint)로 객관적으로 측정하고 기준 미달이면 수정하게 하는 MCP 서버.

AI가 채점하면 자기 코드에 후한 점수를 줄 수 있으므로, 심판(외부 도구)과 선수(Claude)를 분리.

## 변경 파일별 상세

### `pyproject.toml` (신규)
- **용도**: Python 패키지 설정, 의존성, entry point
- **핵심 코드**:
```toml
[project]
name = "code-inspector-mcp"
dependencies = ["fastmcp>=2.0", "pydantic>=2.0"]

[project.scripts]
code-inspector = "code_inspector.server:main"
```

### `src/code_inspector/models.py` (신규)
- **용도**: Pydantic 데이터 모델
- **핵심 코드**:
```python
class Issue(BaseModel):
    file: str
    line: int
    column: int | None = None
    rule: str
    message: str
    severity: Literal["error", "warning", "info"]
    source: Literal["detekt", "ktlint", "android_lint"]

class ToolResult(BaseModel):
    tool: str
    score: float          # 0.0 - 10.0
    issues: list[Issue]
    available: bool
    error: str | None = None

class InspectionResult(BaseModel):
    path: str
    scope: str
    overall_score: float
    passed: bool
    threshold: float
    tool_results: list[ToolResult]
    summary: str
```

### `src/code_inspector/scoring.py` (신규)
- **용도**: 점수 계산
- **로직**: 10점에서 시작, 이슈별 감점 (error=0.3, warning=0.1, info=0.05), 파일 수 대비 정규화
```python
def calculate_score(issues: list[Issue], total_files: int) -> float:
    deductions = sum(SEVERITY_WEIGHTS[i.severity] for i in issues)
    normalized = deductions * (10 / max(total_files, 1))
    return max(0.0, 10.0 - min(normalized, 10.0))
```

### `src/code_inspector/inspectors/base.py` (신규)
- **용도**: Inspector 추상 클래스 + subprocess 유틸
```python
class BaseInspector(ABC):
    @abstractmethod
    async def run(self, path: str, files: list[str] | None) -> ToolResult: ...

    def is_available(self) -> bool: ...

    async def _run_subprocess(self, cmd, cwd) -> tuple[str, str, int]: ...

    def _get_changed_files(self, path: str, ext: str) -> list[str]: ...
```

### `src/code_inspector/inspectors/detekt.py` (신규)
- **용도**: detekt CLI 실행 + XML 파싱
- **방법**: `detekt-cli --input <path> --report xml:<tmp>` 또는 `./gradlew detekt`
- **파싱**: checkstyle XML → Issue 리스트

### `src/code_inspector/inspectors/ktlint.py` (신규)
- **용도**: ktlint CLI 실행 + JSON 파싱
- **방법**: `ktlint --reporter=json <files>`
- **파싱**: JSON array → Issue 리스트 (전부 warning 레벨)

### `src/code_inspector/inspectors/android_lint.py` (신규)
- **용도**: Android Lint 실행 + XML 파싱
- **방법**: `./gradlew lintDebug`, 보고서 `**/build/reports/lint-results*.xml` 파싱
- **파싱**: `<issues><issue>` XML → Issue 리스트

### `src/code_inspector/server.py` (신규)
- **용도**: FastMCP 서버 + inspect 도구 등록
```python
mcp = FastMCP("code-inspector")

@mcp.tool
async def inspect(
    path: str = ".",
    scope: str = "changed",
    fix: bool = False,
    threshold: float = 7.0
) -> dict:
    # 1. 3개 inspector 병렬 실행 (asyncio.gather)
    # 2. 점수 계산
    # 3. fix=True면 수정 제안 포함
    # 4. InspectionResult 반환
```

## 프로젝트 구조
```
codeInspector/
├── pyproject.toml
├── .gitignore
└── src/
    └── code_inspector/
        ├── __init__.py
        ├── server.py
        ├── models.py
        ├── scoring.py
        └── inspectors/
            ├── __init__.py
            ├── base.py
            ├── detekt.py
            ├── ktlint.py
            └── android_lint.py
```

## 설계 결정

1. **3개 inspector 병렬 실행** — asyncio.gather로 총 시간 = max(개별 시간)
2. **미설치 도구 graceful skip** — available=False로 표시, 점수 계산에서 제외
3. **scope="changed"** — git diff로 변경된 .kt/.kts 파일만 검사 (Android Lint는 전체 실행 후 필터)
4. **subprocess 타임아웃** — 120초 (대형 프로젝트 대응)
5. **확장성** — inspectors/ 디렉토리에 새 Inspector 클래스 추가만으로 언어 확장

## 검증
- `uv run code-inspector` 실행 → MCP 서버 stdio 기동 확인
- Claude Code settings에 MCP 서버 등록 → "검사해줘" 입력 → inspect 도구 호출 확인
- Android 프로젝트에서 실행 → detekt/ktlint/lint 결과 + 점수 반환 확인
