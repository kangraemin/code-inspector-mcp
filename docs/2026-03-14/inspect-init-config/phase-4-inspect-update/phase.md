# Phase 4: inspect 도구 업데이트

## 목표
inspect 도구가 .code-inspector.json 설정을 반영하도록 수정

## 범위
- server.py: inspect 도구에 설정 로드 + 가중 평균 + enable/disable + ignore + severity_weights
- scoring.py: 커스텀 severity_weights 파라미터 추가

## Steps
1. Step 1: scoring.py 수정 + inspect 설정 반영
