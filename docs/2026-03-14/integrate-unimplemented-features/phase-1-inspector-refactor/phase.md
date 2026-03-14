## 목표
Inspector 코드 중복 제거, scoring 정규화 공식 수정, severity_weights config 값 전달

## 범위
- base.py: `_count_kt_files` 추가, `run()` 시그니처 변경
- detekt.py: 중복 메서드 삭제, 무의미한 오버라이드 삭제, severity_weights 전달
- ktlint.py: 중복 메서드 삭제, severity_weights 전달
- android_lint.py: 중복 메서드 삭제, severity_weights 전달
- scoring.py: 정규화 공식 수정
- server.py: inspector 호출 시 severity_weights 전달

## Steps
- Step 1: 중복 제거 + 무의미한 오버라이드 제거
- Step 2: Scoring 공식 수정 + severity_weights 전달
