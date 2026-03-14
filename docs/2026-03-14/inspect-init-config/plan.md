# inspect_init + 설정 시스템 + 메트릭 확장

## Context
유저가 직접 JSON 설정을 작성하는 건 비현실적. 프로젝트 코드를 전수 조사해서 Claude가 패턴 분석 후 설정 자동 생성. 핵심 가치: **가독성 + 재활용성** 측정.

## 변경 파일별 상세

### `src/code_inspector/config.py` (신규)
- **용도**: .code-inspector.json 스키마 + 로드/저장
- **핵심 코드**:
```python
class CodeInspectorConfig(BaseModel):
    threshold: float = 7.0
    inspectors: dict[str, InspectorConfig]
    metrics: MetricsConfig
    severity_weights: dict[str, float]
    ignore: list[str] = ["**/generated/**", "**/build/**"]
    architecture: ArchitectureConfig

def load_config(path: str) -> CodeInspectorConfig | None
def save_config(path: str, config: CodeInspectorConfig) -> str
```

### `src/code_inspector/server.py` (수정)
- **변경 이유**: inspect_init, inspect_config 도구 추가 + inspect에 설정 반영
- **Before**: inspect 도구만 존재, 하드코딩된 threshold/weights
- **After**: 3개 도구 + 설정 파일 기반 동작

#### inspect_init 도구:
```python
@mcp.tool
async def inspect_init(path: str = ".") -> dict:
    # 1. 프로젝트 kt 파일 전부 수집 (최소 10개, 상한 없음)
    # 2. 설정 파일 수집 (detekt.yml, .editorconfig, build.gradle)
    # 3. 아키텍처 힌트 감지 (ViewModel, Repository, UseCase, Compose...)
    # 4. 전부 Claude에게 반환 → Claude가 분석 후 .code-inspector.json 생성
```

#### inspect_config 도구:
```python
@mcp.tool
async def inspect_config(path: str = ".", action: str = "read", updates: dict | None = None) -> dict:
    # read: 현재 설정 반환
    # update: updates dict를 deep merge
    # reset: 기본값으로 초기화
```

#### inspect 수정:
- load_config()로 설정 로드
- inspector enable/disable 반영
- 가중 평균 점수 계산 (weight)
- severity_weights 커스텀 적용
- ignore 패턴 필터링

### `src/code_inspector/scoring.py` (수정)
- **변경 이유**: 커스텀 severity_weights 지원
- **Before**: `calculate_score(issues, total_files)` — 고정 weights
- **After**: `calculate_score(issues, total_files, severity_weights=None)` — 외부 weights 수용

### `src/code_inspector/inspectors/base.py` (수정)
- **변경 이유**: inspector별 설정 전달
- **Before**: `run(path, files)`
- **After**: `run(path, files, config=None)`

### `src/code_inspector/metrics/` (신규 디렉토리)
- `complexity.py`: 순환 복잡도 (if/when/for/while/catch 카운트)
- `duplication.py`: 코드 중복 감지 (라인 해싱 슬라이딩 윈도우)
- `coverage.py`: JaCoCo XML 파싱 → 테스트 커버리지

## 검증
- `inspect_init` 호출 → kt 파일 전수 + 아키텍처 힌트 반환 확인
- `inspect_config` update → .code-inspector.json 생성/수정 확인
- `inspect` 설정 반영 → 가중 평균, ignore, enable/disable 동작 확인
- 메트릭 → complexity/duplication/coverage 결과 반환 확인
