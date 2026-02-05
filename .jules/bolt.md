## 2026-02-05 - Unnecessary List Re-renders
**Learning:** `ThumbnailsPage` was passing an inline function `onRegenerate` to `ThumbnailCard`, causing all cards to re-render whenever any state changed (like regenerating one thumbnail), even if `ThumbnailCard` was memoized.
**Action:** Always wrap list item callbacks in `useCallback` and ensure `React.memo` is used on the list item component to prevent O(n) re-renders when updating a single item.
