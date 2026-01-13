# Adversarial Testing Review - January 2026

> Issue #97 review of the test suite following completion of issues #77, #80, #81, #82, #83, #84

## Review Approach

Approached the test suite as a skeptical reviewer looking for:
- Tests that pass but don't validate anything meaningful
- Coverage numbers that hide gaps
- Mocked tests that don't test real integration
- Shared blind spots from agent-written tests

## Findings Summary

| Finding | Severity | Issue Created |
|---------|----------|---------------|
| Frontend tests never run in CI | Critical | #98 |
| No CSS sync verification | Significant | #99 |
| Frontend tests copy functions instead of importing | Moderate | #100 |
| OCR tests fully mocked | Acceptable | N/A |
| Coverage gaps in error handling | Minor | N/A |

## Critical: Frontend Tests Never Run in CI (#98)

**The Problem**: JavaScript tests exist in `developer/tests/` but:
- No `package.json` exists to run them
- CI workflow only runs `pytest -v`

**Impact**: The 600+ lines of frontend test code provide zero CI protection. Bugs in `preview-template.jsx` would ship without being caught.

## Significant: No CSS Sync Verification (#99)

**The Problem**: CSS is duplicated between:
- `anki_utils/themes.py` (Python, generates .apkg files)
- `anki_utils/assets/preview-template.jsx` (React preview)

The code explicitly documents this requires manual sync. No test verifies they match.

**Impact**: Preview could show different styling than exported cards. Silent failure.

## Moderate: Frontend Tests Copy Functions (#100)

**The Problem**: Tests copy pure functions from `preview-template.jsx` instead of importing them.

**Impact**: If source changes but copies aren't updated, tests become stale and test old code.

## Acceptable: OCR Tests Fully Mocked

**The Reality**: All OCR tests mock pytesseract. The one real integration test skips in CI because Tesseract isn't installed.

**Why Acceptable**:
- Installing Tesseract in CI is complex
- An integration test exists that runs locally if Tesseract is available
- The mocked tests still verify the logic around OCR

## Minor: Coverage Gaps in Error Handling

**Uncovered lines** (93% coverage overall):
- `cli.py`: Lines 166-170 (markdown formatting edge case)
- `exporter.py`: Lines 1265-1274 (fallback MIME type detection)
- `exporter.py`: Lines 1281-1283, 1309-1310 (file read/decode errors)

**Why Acceptable**: These are defensive error handling paths that are difficult to trigger and generally safe to leave uncovered.

## What's Good About the Test Suite

1. **Anki import compatibility tests** (#80) are thorough - they verify ZIP structure, SQLite schema, and media manifests
2. **Golden example tests** (#84) provide regression protection for card structure
3. **Edge case coverage** (#77) handles Unicode, special characters, and boundary conditions well
4. **Test organization** is clear with descriptive names and grouped by module

## Recommendations

1. **Urgent**: Fix #98 - Add `package.json` and npm test step to CI
2. **High Priority**: Fix #99 - Add CSS sync verification test
3. **Medium Priority**: Fix #100 - Either extract shared functions or add sync check
4. **Document**: Add a note in AGENTS.md about the OCR testing limitation

## Verification

```bash
# All Python tests pass
$ pytest -v
# 497 passed, 1 skipped

# Coverage is 93%
$ pytest --cov=anki_utils
```

## Review Date

2026-01-03

## Reviewer

Agent working on Issue #97
