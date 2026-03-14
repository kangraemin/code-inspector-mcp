# Step 1: BaseInspector ABC

## TC

| TC | 검증 항목 | 기대 결과 | 상태 |
|----|----------|----------|------|
| TC-01 | BaseInspector import 가능 | import 성공 | ✅ |
| TC-02 | ABC 강제 | 직접 인스턴스화 시 TypeError | ✅ |
| TC-03 | _run_subprocess 동작 | echo 명령 실행 결과 반환 | ✅ |
| TC-04 | _get_changed_files 동작 | git diff 기반 파일 목록 반환 | ✅ |

## 구현 내용
- base.py: BaseInspector ABC (run 추상 메서드, is_available, _run_subprocess, _get_changed_files)

## 실행출력

TC-01: import OK
TC-02: TypeError raised → OK
TC-03: stdout=hello, code=0
TC-04: changed files type=list, count=0
