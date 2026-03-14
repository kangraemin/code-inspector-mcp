# Code Inspector MCP

Kotlin/Android 프로젝트의 코드 품질을 검사하는 [MCP](https://modelcontextprotocol.io) 서버.
Detekt, Ktlint, Android Lint를 병렬 실행하고, 복잡도·중복도·커버리지 메트릭을 분석하여 10점 만점 품질 점수를 산출한다.

## 설치

```bash
# uv 사용
uv pip install -e .

# 또는 pip
pip install -e .
```

### 필수 도구

검사기를 사용하려면 아래 도구가 시스템에 설치되어 있어야 한다:

| 검사기 | 설치 방법 |
|--------|----------|
| [Detekt](https://detekt.dev) | `brew install detekt` 또는 Gradle 플러그인 |
| [Ktlint](https://pinterest.github.io/ktlint) | `brew install ktlint` |
| Android Lint | Android Gradle 프로젝트에 포함 (`./gradlew lintDebug`) |

설치되지 않은 검사기는 자동으로 건너뛰고 결과에 `not installed`로 표시된다.

### Claude Code에 등록

`claude mcp add` 또는 `~/.claude.json`에 직접 추가:

```json
{
  "mcpServers": {
    "code-inspector": {
      "command": "uv",
      "args": ["run", "--directory", "/path/to/code-inspector-mcp", "code-inspector"]
    }
  }
}
```

## MCP 도구

### `inspect`

코드 품질 검사를 실행하고 점수를 반환한다.

| 파라미터 | 타입 | 기본값 | 설명 |
|---------|------|-------|------|
| `path` | string | `"."` | 검사할 프로젝트 경로 |
| `scope` | string | `"changed"` | `"changed"` (git diff 대상만) 또는 `"all"` (전체) |
| `fix` | bool | `false` | 통과 실패 시 수정 제안 포함 |
| `threshold` | float | 설정값 또는 `7.0` | 합격 기준 점수 (10점 만점) |

반환 예시:
```
detekt: 8.5/10 ✅
ktlint: 9.2/10 ✅
android_lint: ⚠️ (not installed)
complexity: 2 violation(s)
duplication: 3.1%
coverage: 72.5%
overall: 8.8/10 PASS ✅
```

### `inspect_init`

프로젝트의 모든 Kotlin 파일과 메타데이터를 수집한다. Claude가 분석하여 `.code-inspector.json` 설정을 생성하는 데 사용한다.

- 모든 `.kt`/`.kts` 파일 내용 수집
- `detekt.yml`, `build.gradle` 등 설정 파일 수집
- 아키텍처 패턴 감지 (ViewModel, Repository, UseCase, Compose, Hilt 등)

### `inspect_config`

`.code-inspector.json` 설정 파일을 읽기/수정/초기화한다.

| 파라미터 | 타입 | 기본값 | 설명 |
|---------|------|-------|------|
| `path` | string | `"."` | 프로젝트 경로 |
| `action` | string | `"read"` | `"read"`, `"update"`, `"reset"` |
| `updates` | dict | `null` | 부분 업데이트할 설정 (`action="update"` 시) |

## 설정

프로젝트 루트에 `.code-inspector.json`을 생성하거나, `inspect_init` → `inspect_config`로 자동 생성한다.

```json
{
  "threshold": 7.0,
  "inspectors": {
    "detekt": { "enabled": true, "weight": 0.4 },
    "ktlint": { "enabled": true, "weight": 0.3 },
    "android_lint": { "enabled": true, "weight": 0.3 }
  },
  "metrics": {
    "complexity": { "enabled": true, "max_per_function": 15 },
    "duplication": { "enabled": true, "min_tokens": 100 },
    "coverage": { "enabled": true, "min_percent": 80.0 }
  },
  "severity_weights": {
    "error": 0.3,
    "warning": 0.1,
    "info": 0.05
  },
  "ignore": ["**/generated/**", "**/build/**"]
}
```

### 검사기 가중치

전체 점수는 각 검사기 점수의 가중 평균이다. 기본값은 Detekt 40%, Ktlint 30%, Android Lint 30%.

### 점수 산출

```
score = 10 - min(raw_deductions / total_files * 10, 10.0)
```

심각도별 감점: error 0.3점, warning 0.1점, info 0.05점.

## 메트릭

| 메트릭 | 분석 방식 | 설정 |
|--------|----------|------|
| **Complexity** | 분기 키워드 카운트 (if/when/for/while/catch/&&/\|\|) | `max_per_function`: 함수당 최대 복잡도 |
| **Duplication** | 5줄 슬라이딩 윈도우 MD5 해시 비교 | `min_tokens`: 최소 토큰 수 |
| **Coverage** | JaCoCo XML 리포트 파싱 | `min_percent`: 최소 커버리지 % |

## 라이선스

MIT
