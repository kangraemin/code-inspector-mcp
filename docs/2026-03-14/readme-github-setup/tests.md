| TC | 검증 항목 | 기대 결과 | 상태 |
|----|----------|----------|------|
| TC-01 | README.md 존재 및 주요 섹션 포함 | Overview, Installation, Tools, Configuration, Metrics 섹션 존재 | ✅ |
| TC-02 | GitHub description 업데이트 | gh repo view에서 새 description 확인 | ✅ |
| TC-03 | GitHub topics 설정 | gh repo view에서 10개 topics 확인 | ✅ |

## 실행출력

TC-01: `head -5 README.md && grep "^## " README.md`
→ 섹션 확인: 설치, MCP 도구, 설정, 메트릭, 라이선스

TC-02: `gh repo view --json description`
→ "Kotlin/Android code quality inspector — MCP server for Detekt, Ktlint & Android Lint"

TC-03: `gh repo view --json repositoryTopics`
→ android, android-lint, claude-code, code-quality, detekt, kotlin, ktlint, mcp, mcp-server, static-analysis (10개)
