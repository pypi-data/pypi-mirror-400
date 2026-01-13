# Detailed Bug List

## Date: 2025-01-17

## Real Bugs Found (Excluding False Positives)

### 1. Bare Except Clauses (36 instances)

These should be changed from `except:` to `except Exception:` or more specific exception types.

**Files to check:**
- Multiple files detected via AST analysis
- Multiple files detected via string matching

**Action Required:** Search for `except:` patterns and replace with appropriate exception types.

### 2. Wildcard Imports (17 instances)

These `import *` statements should be replaced with explicit imports.

**Action Required:** Replace `from module import *` with explicit imports like `from module import function1, function2`.

### 3. Unused Parameters (38 instances)

Function parameters that are defined but never used in the function body.

**Action Required:**
- Remove if truly unused
- Prefix with `_` if needed for API compatibility (e.g., `_unused_param`)
- Use if they should be used

### 4. Using len() in Boolean Context (14 instances)

Using `if len(items):` instead of the more Pythonic `if items:`.

**Action Required:** Replace `if len(items):` with `if items:` for better performance and style.

### 5. None Comparison (2 instances)

Using `== None` or `!= None` instead of `is None` or `is not None`.

**Action Required:** Replace `== None` with `is None` and `!= None` with `is not None`.

## False Positives (Can Ignore)

### potential_attribute_error (4,348 instances)

These are false positives from static analysis:
- `self` in instance methods (always defined)
- Loop variables like `t`, `s`, `item` (defined in loops)
- Imported module aliases like `np` (numpy imported but static analysis can't always track)

**Action:** None - these can be safely ignored.

## Summary

- **Total Real Bugs:** ~107 issues
- **Critical Bugs:** 0 ✅
- **Medium Priority:** 53 issues (bare except + wildcard imports)
- **Low Priority:** 54 issues (unused params, len in boolean, None comparison)
- **False Positives:** 4,348 (can ignore)

## Next Steps

1. Fix bare except clauses (high priority)
2. Fix wildcard imports (medium priority)
3. Clean up unused parameters (low priority)
4. Improve boolean checks (low priority)
5. Fix None comparisons (low priority)

