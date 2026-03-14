# Step 2: Scoring 공식 수정 + severity_weights 전달

## TC

| TC | 검증 항목 | 기대 결과 | 실제 결과 |
|----|----------|----------|----------|
| TC-01 | scoring 정규화: 파일 많을수록 점수 높음 | calculate_score(1 error, 10 files) > calculate_score(1 error, 1 file) | ✅ |
| TC-02 | severity_weights 전달 시 반영됨 | custom weights로 점수 변동 확인 | ✅ |
| TC-03 | run() 시그니처에 severity_weights 존재 | inspect 파라미터 확인 | ✅ |
| TC-04 | server.py에서 cfg.severity_weights 전달 | 소스 코드에 cfg.severity_weights 포함 | ✅ |

## 실행 결과

TC-01~04: `.venv/bin/python -c` 통합 테스트
→
```
TC-01: 1 file=7.0, 10 files=9.7, 10files > 1file? True
TC-02: default=9.4, custom=8.0, different? True
TC-03: severity_weights in run()? True
TC-04: cfg.severity_weights in server? True
```
