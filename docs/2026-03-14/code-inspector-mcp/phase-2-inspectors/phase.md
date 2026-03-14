# Phase 2: Inspectors

## 목표
BaseInspector 추상 클래스 + detekt/ktlint/android_lint 3개 구현체

## 범위
- base.py: ABC, subprocess 유틸, git diff 유틸
- detekt.py: detekt-cli/gradlew detekt, XML 파싱
- ktlint.py: ktlint --reporter=json, JSON 파싱
- android_lint.py: gradlew lintDebug, XML 파싱

## Steps
1. Step 1: base.py (BaseInspector ABC + 유틸)
2. Step 2: detekt.py (detekt inspector)
3. Step 3: ktlint.py (ktlint inspector)
4. Step 4: android_lint.py (Android Lint inspector)
