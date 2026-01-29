## 2024-10-27 - [Next.js Environment Artifacts]
**Learning:** `frontend/next-env.d.ts` is automatically modified by the Next.js dev server (adding imports like `./.next/dev/types/routes.d.ts`) when running locally.
**Action:** Always check and revert changes to `frontend/next-env.d.ts` before committing to avoid polluting the repo with local dev artifacts.

## 2024-10-27 - [React List Optimization]
**Learning:** Passing inline functions to list items prevents `React.memo` from working, causing O(N) re-renders for single item updates.
**Action:** Always use `useCallback` for event handlers passed to list items, especially when the item component is memoized.
