## 2024-10-27 - [Component Memoization in Lists]
**Learning:** `ThumbnailsPage` re-renders all `ThumbnailCard` components on any state change because the `onRegenerate` callback was unstable. `ThumbnailCard` itself is heavy (contains images, dialogs).
**Action:** Always wrap heavy list items in `React.memo` and ensure callbacks passed to them are stable (using `useCallback`).
