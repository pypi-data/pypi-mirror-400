# Fixing Issues Workflow

**Universal rule: Fix issues completely. Never work around them.**

## When You Encounter Any Blocking Issue

1. **Recognize it's blocking**: Test failures, validation errors, missing requirements
2. **Treat it as in-scope**: Regardless of when introduced or which repo
3. **Fix it completely**: Don't skip, bypass, or defer

## Examples

### ❌ WRONG: Working Around
- "This is a pre-existing issue, let's skip the test"
- "Let's fix the workflow in this PR and the formula in another PR"
- "Add conditional to skip this when X"

### ✅ RIGHT: Fixing
- "The formula has invalid placeholders, let me populate it with real values"
- "The test is failing because the code is wrong, let me fix the code"
- "This requires fixing both the workflow AND the formula"

## Before Proposing ANY Conditional Logic

Ask: "Am I adding this condition to work around a problem I should fix?"

If yes → Fix the problem instead
