# ALL BUGS FOUND - Comprehensive List

## CRITICAL BUGS (Must Fix Immediately)

### 1. **API V2 Router Not Registered - 404 Errors**
**File**: `src/servers/main_server.py:204-219`
**Issue**: Router import fails silently, no registration happens
**Impact**: All `/api/*` endpoints return 404
**Status**: FIXED - Added direct file import fallback

### 2. **Missing Import Error Details**
**File**: `backend/src/servers/api_v2_routes.py:47-80`
**Issue**: Import errors don't show details, making debugging impossible
**Status**: FIXED - Added error details to all imports

### 3. **Inconsistent Error Logging**
**File**: `backend/src/servers/api_v2_routes.py` (multiple locations)
**Issue**: Some use `logging.warning`, some use `logger.warning`
**Status**: FIXED - Standardized to use `logger`

## POTENTIAL BUGS (Need Verification)

### 4. **Missing numpy import in embed endpoint**
**File**: `backend/src/servers/api_v2_routes.py:315`
**Issue**: `import numpy as np` is inside try block, might fail
**Status**: Should move to top of file

### 5. **Missing error handling for file operations**
**File**: `backend/src/servers/api_v2_routes.py:105-112`
**Issue**: File read operations might fail on large files
**Status**: Need to add size limits

### 6. **URL timeout not configurable**
**File**: `backend/src/servers/api_v2_routes.py:116`
**Issue**: Hardcoded 30 second timeout
**Status**: Should be configurable

### 7. **Missing validation for seed parameter**
**File**: `backend/src/servers/api_v2_routes.py:91`
**Issue**: No validation that seed is valid integer
**Status**: Should add validation

### 8. **Missing validation for method parameter**
**File**: `backend/src/servers/api_v2_routes.py:90`
**Issue**: No validation that method is valid tokenizer type
**Status**: Should add validation

### 9. **Missing error handling for tokenizer.build()**
**File**: `backend/src/servers/api_v2_routes.py:132`
**Issue**: `tokenizer.build()` might raise exceptions not caught
**Status**: Already in try-except, but should verify

### 10. **Missing check for empty streams**
**File**: `backend/src/servers/api_v2_routes.py:134`
**Issue**: Check happens but error message could be better
**Status**: Minor - acceptable

## CODE QUALITY ISSUES

### 11. **Duplicate health endpoints**
**File**: 
- `src/servers/main_server.py:255` - `/health`
- `backend/src/servers/api_v2_routes.py:654` - `/api/health`
**Issue**: Two health endpoints (not a bug, but could be confusing)
**Status**: Acceptable - different purposes

### 12. **Inconsistent error messages**
**File**: Multiple files
**Issue**: Some errors are user-friendly, some are technical
**Status**: Should standardize

### 13. **Missing type hints in some functions**
**File**: `backend/src/servers/api_v2_routes.py`
**Issue**: Some functions missing return type hints
**Status**: Minor - acceptable for now

## FRONTEND BUGS

### 14. **Missing error boundary**
**File**: `frontend/components/enhanced-dashboard.tsx`
**Issue**: No error boundary to catch React errors
**Status**: Should add

### 15. **Missing loading states in some places**
**File**: `frontend/components/enhanced-dashboard.tsx`
**Issue**: Some operations don't show loading state
**Status**: Already fixed in previous changes

### 16. **Missing request cancellation**
**File**: `frontend/lib/api-enhanced.ts`
**Issue**: No way to cancel in-flight requests
**Status**: Should add AbortController

## TESTING ISSUES

### 17. **No integration tests**
**Issue**: No tests to verify API V2 routes work
**Status**: Should add

### 18. **No error scenario tests**
**Issue**: No tests for error cases
**Status**: Should add

