# README.md 생성 + GitHub repo 설정

## 변경 파일별 상세

### `README.md` (신규)
- **변경 이유**: 프로젝트 소개, 설치법, 사용법, 설정 문서가 없음
- **Before**: 파일 없음
- **After**: 프로젝트 개요, 설치, MCP 도구 3개 설명, 설정(.code-inspector.json), 메트릭 설명 포함
- **영향 범위**: 없음 (신규 파일)

### GitHub repo 설정 (gh CLI)
- **변경 이유**: description 업데이트 + 검색용 topics 추가
- **description**: `Kotlin/Android code quality inspector — MCP server for Detekt, Ktlint & Android Lint`
- **topics**: `mcp`, `mcp-server`, `kotlin`, `android`, `code-quality`, `detekt`, `ktlint`, `android-lint`, `static-analysis`, `claude-code`

## 검증
- 검증 명령어: `cat README.md | head -5` + `gh repo view --json description,repositoryTopics`
- 기대 결과: README 존재, description/topics 설정됨
