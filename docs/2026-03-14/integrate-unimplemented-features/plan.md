# 미구현 기능 통합 구현

## 변경 파일별 상세

### `src/code_inspector/inspectors/base.py`
- **변경 이유**: `_count_kt_files` 중복 제거 (3개 inspector → base로 이동), `run()` 시그니처에 `severity_weights` 추가
- **Before** (현재 코드):
```python
class BaseInspector(ABC):
    name: str = ""

    @abstractmethod
    async def run(self, path: str, files: list[str] | None = None) -> ToolResult:
        ...
```
- **After** (변경 후):
```python
class BaseInspector(ABC):
    name: str = ""

    @abstractmethod
    async def run(self, path: str, files: list[str] | None = None, severity_weights: dict[str, float] | None = None) -> ToolResult:
        ...

    def _count_kt_files(self, path: str) -> int:
        count = 0
        for root, _, filenames in os.walk(path):
            for f in filenames:
                if f.endswith((".kt", ".kts")):
                    count += 1
        return max(count, 1)
```
- **영향 범위**: 모든 inspector 서브클래스의 `run()` 시그니처

### `src/code_inspector/inspectors/detekt.py`
- **변경 이유**: `_count_kt_files` 삭제 (base로 이동), `is_available()` 무의미한 오버라이드 삭제, `severity_weights` 전달
- **Before**:
```python
def is_available(self) -> bool:
    if super().is_available():
        return True
    return False
```
```python
async def run(self, path: str, files: list[str] | None = None) -> ToolResult:
    ...
    score = calculate_score(issues, total_files)
```
- **After**:
```python
# is_available 오버라이드 삭제

async def run(self, path: str, files: list[str] | None = None, severity_weights: dict[str, float] | None = None) -> ToolResult:
    ...
    score = calculate_score(issues, total_files, severity_weights)
```
- **영향 범위**: server.py의 inspector 호출

### `src/code_inspector/inspectors/ktlint.py`
- **변경 이유**: `_count_kt_files` 삭제, `severity_weights` 전달
- **Before**:
```python
async def run(self, path: str, files: list[str] | None = None) -> ToolResult:
    ...
    score = calculate_score(issues, total_files)
```
- **After**:
```python
async def run(self, path: str, files: list[str] | None = None, severity_weights: dict[str, float] | None = None) -> ToolResult:
    ...
    score = calculate_score(issues, total_files, severity_weights)
```
- **영향 범위**: server.py의 inspector 호출

### `src/code_inspector/inspectors/android_lint.py`
- **변경 이유**: `_count_kt_files` 삭제, `severity_weights` 전달
- **Before**:
```python
async def run(self, path: str, files: list[str] | None = None) -> ToolResult:
    ...
    score = calculate_score(all_issues, total_files)
```
- **After**:
```python
async def run(self, path: str, files: list[str] | None = None, severity_weights: dict[str, float] | None = None) -> ToolResult:
    ...
    score = calculate_score(all_issues, total_files, severity_weights)
```
- **영향 범위**: server.py의 inspector 호출

### `src/code_inspector/scoring.py`
- **변경 이유**: 정규화 공식이 역방향 (파일 많을수록 감점 증가)
- **Before**:
```python
normalized = raw_deduction * (10 / max(total_files, 1))
```
- **After**:
```python
normalized = raw_deduction / max(total_files, 1) * 10
```
- **영향 범위**: 모든 inspector의 점수 계산

### `src/code_inspector/server.py`
- **변경 이유**: severity_weights 전달, ignore 패턴 필터링, metrics 모듈 연결
- **Before**:
```python
results: list[ToolResult] = await asyncio.gather(
    *[inspector.run(path, files) for inspector in enabled_inspectors]
)
```
- **After**:
```python
results: list[ToolResult] = await asyncio.gather(
    *[inspector.run(path, files, cfg.severity_weights) for inspector in enabled_inspectors]
)

# ignore 패턴으로 이슈 필터링
if cfg.ignore:
    for r in results:
        if r.available and r.issues:
            r.issues = [
                issue for issue in r.issues
                if not _should_ignore(issue.file, cfg.ignore)
            ]
            total = len(files) if files else _count_kt_files_in_path(path)
            r.score = calculate_score(r.issues, total, cfg.severity_weights)
```
- **After** (metrics 연결):
```python
# Metrics 분석
metrics_results = {}
if cfg.metrics.complexity.enabled or cfg.metrics.duplication.enabled:
    kt_files_for_metrics = _collect_kt_files(path, files, cfg.ignore)

if cfg.metrics.complexity.enabled:
    complexity_violations = []
    for fi in kt_files_for_metrics:
        result = analyze_complexity(fi["content"], fi["path"], cfg.metrics.complexity.max_per_function)
        if result["violations"]:
            complexity_violations.append(result)
    metrics_results["complexity"] = {"files_analyzed": len(kt_files_for_metrics), "violations": complexity_violations}

if cfg.metrics.duplication.enabled:
    metrics_results["duplication"] = analyze_duplication(kt_files_for_metrics)

if cfg.metrics.coverage.enabled:
    metrics_results["coverage"] = analyze_coverage(path, cfg.metrics.coverage.min_percent)

output = result.model_dump()
if metrics_results:
    output["metrics"] = metrics_results
```
- **영향 범위**: inspect() 도구의 반환값 구조

## 검증
- 검증 명령어: `cd /Users/ram/programming/vibecoding/codeInspector && python -c "from code_inspector.server import mcp; print('import OK')"`
- 추가 검증: `python -c "from code_inspector.scoring import calculate_score; from code_inspector.models import Issue; i=[Issue(file='a.kt',line=1,rule='r',message='m',severity='error',source='detekt')]; print('1 file:', calculate_score(i,1)); print('10 files:', calculate_score(i,10))"`
  - 기대: 10 files 점수 > 1 file 점수 (파일 많을수록 이슈당 감점 줄어야 함)
- metrics 검증: `python -c "from code_inspector.metrics.complexity import analyze_complexity; r=analyze_complexity('fun test() {\n  if (true) {}\n}', 'test.kt'); print(r)"`
