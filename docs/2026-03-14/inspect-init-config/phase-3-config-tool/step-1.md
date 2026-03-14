# Step 1: inspect_config 도구

## TC

| TC | 검증 항목 | 기대 결과 | 상태 |
|----|----------|----------|------|
| TC-01 | inspect_config 등록 | mcp.get_tool('inspect_config') 성공 | ✅ |
| TC-02 | read (파일 없음) | 기본 config 반환 | ✅ |
| TC-03 | update | deep merge 후 저장, 변경 반영 확인 | ✅ |
| TC-04 | reset | 파일 삭제 후 기본값 반환 | ✅ |

## 구현 내용
- inspect_config: read/update/reset 3 action 지원, deep_merge로 부분 업데이트

## 실행출력

Output:
TC-01: tool name=inspect_config
TC-02: action=read (defaults, no file exists), threshold=7.0
TC-03: threshold=8.0, android_enabled=False, file exists=True
TC-04: action=reset to defaults (file removed), file_exists=False
