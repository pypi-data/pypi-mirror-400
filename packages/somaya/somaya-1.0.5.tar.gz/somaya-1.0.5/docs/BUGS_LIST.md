# COMPREHENSIVE BUGS LIST - ALL ISSUES FOUND

## 🔴 CRITICAL BUGS (Must Fix Immediately)

### 1. **AuthLogin Component - Undefined Element Error**
- **Error**: `Element type is invalid: expected a string... but got: undefined`
- **Location**: `frontend/components/auth-login.tsx`
- **Cause**: One of the imported components is undefined
- **Potential Issues**:
  - Alert component not properly exported
  - Toast component not properly exported
  - Missing dependency or circular import
- **Status**: 🔴 CRITICAL - Blocks authentication page

### 2. **Backend Authentication - Request Parameter Issue**
- **Error**: `Security() got an unexpected keyword argument 'auto_error'`
- **Location**: `src/servers/main_server.py` line 1722
- **Status**: ✅ FIXED (but need to verify)

### 3. **Frontend Import - Missing Lock Icon**
- **Error**: `ReferenceError: Lock is not defined`
- **Location**: `frontend/components/sidebar.tsx`
- **Status**: ✅ FIXED (but need to verify)

### 4. **Frontend Import - Missing AuthLogin Component**
- **Error**: `ReferenceError: AuthLogin is not defined`
- **Location**: `frontend/app/page.tsx`
- **Status**: ✅ FIXED (but need to verify)

### 5. **Frontend Import - Missing Alert Component**
- **Error**: `Module not found: Can't resolve '@/components/ui/alert'`
- **Location**: `frontend/components/auth-login.tsx`
- **Status**: ✅ FIXED (but still has runtime error)

## ⚠️ POTENTIAL BUGS (Need Investigation)

### 6. **Alert Component Export Issue**
- **Issue**: Alert component exists but might not be properly exported or loaded
- **Location**: `frontend/components/ui/alert.tsx`
- **Check**: Verify exports, check for "use client" directive

### 7. **Toast Component Import**
- **Issue**: `toast` import might be incorrect
- **Location**: `frontend/components/auth-login.tsx` line 11
- **Check**: Verify export from `@/components/notification-toast`

### 8. **API Functions Export**
- **Issue**: `login`, `verifyAuth`, `logout` functions might not be exported
- **Location**: `frontend/lib/api.ts`
- **Check**: Verify all auth functions are exported

### 9. **Request Parameter Handling in Backend**
- **Issue**: Changed `request` to `code_request` and `terminal_request` - need to verify all usages
- **Location**: `src/servers/main_server.py`
- **Check**: All endpoint functions use correct parameter names

### 10. **Environment Variables Not Set**
- **Issue**: Production requires env vars but might not be documented clearly
- **Status**: ⚠️ Need to verify all required env vars are documented

## 🟡 MINOR ISSUES

### 11. **Next.js Metadata Warnings**
- **Warning**: `Unsupported metadata themeColor/viewport in metadata export`
- **Location**: `frontend/app/layout.tsx`
- **Impact**: Minor - just warnings, doesn't break functionality

### 12. **TypeScript Type Issues**
- **Check**: All TypeScript types properly defined
- **Location**: Various frontend files

### 13. **Missing Error Boundaries**
- **Issue**: No error boundaries for better error handling
- **Location**: Frontend app structure

## 📋 CHECKLIST TO FIX ALL BUGS

### Immediate Actions:
- [ ] Verify Alert component is properly exported and accessible
- [ ] Verify Toast component export
- [ ] Verify all API function exports
- [ ] Test AuthLogin component in isolation
- [ ] Check console for additional errors
- [ ] Verify all component imports are correct
- [ ] Test authentication flow end-to-end

### Backend Checks:
- [ ] Verify all endpoint parameter names are correct
- [ ] Test all API endpoints
- [ ] Verify authentication middleware works
- [ ] Check for any syntax errors

### Frontend Checks:
- [ ] Verify all UI components exist and are exported
- [ ] Check for circular imports
- [ ] Verify all TypeScript types
- [ ] Test all pages render correctly

