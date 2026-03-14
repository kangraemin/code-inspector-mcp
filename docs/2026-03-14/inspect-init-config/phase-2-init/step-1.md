# Step 1: inspect_init 도구

## TC

| TC | 검증 항목 | 기대 결과 | 상태 |
|----|----------|----------|------|
| TC-01 | inspect_init 등록 | mcp.get_tool('inspect_init') 성공 | ✅ |
| TC-02 | kt 파일 수집 | 테스트 디렉토리에서 kt 파일 내용 반환 | ✅ |
| TC-03 | 설정 파일 수집 | detekt.yml, build.gradle 등 감지 | ✅ |
| TC-04 | 아키텍처 힌트 | ViewModel/Repository 파일명 감지 | ✅ |
| TC-05 | ignore 패턴 | build/, generated/ 디렉토리 제외 | ✅ |

## 구현 내용
- inspect_init: os.walk로 kt 파일 전수 수집, gradle.kts 제외, SKIP_DIRS 필터링
- 아키텍처 힌트: 파일명+내용 패턴 매칭 (ViewModel, Repository, UseCase, Compose, Hilt, Flow)
- 설정 파일 수집: 프로젝트 루트의 detekt.yml, .editorconfig, build.gradle 등

## 실행출력

Output:
TC-01: tool name=inspect_init
TC-02: kt_files=['app/src/main/MainViewModel.kt', 'app/src/main/UserRepository.kt']
TC-03: config=['detekt.yml', 'build.gradle.kts']
TC-04: vm=True, repo=True
TC-05: build_in_results=False, gradle.kts excluded=True
