## 2026-01-19 - React List Optimization
**Learning:** `React.memo` is only effective for list items if the callbacks passed to them are also stable. Inline functions in `map` loops defeat the purpose of `memo`.
**Action:** Always pair `React.memo` on list components with `useCallback` for event handlers in the parent component.
