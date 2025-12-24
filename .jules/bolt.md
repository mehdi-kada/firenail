## 2024-05-23 - React List Performance
**Learning:** Purely presentational components in large lists (like `ThumbnailCard`) should often be wrapped in `React.memo` to prevent unnecessary re-renders when parent state updates.
**Action:** Always check if list item callbacks (like `onRegenerate`) are stable (using `useCallback`) before wrapping components in `React.memo`, otherwise the optimization is useless.
