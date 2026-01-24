## 2025-02-24 - [Unmemoized List Items in Thumbnails Page]
**Learning:** The `ThumbnailsPage` renders a list of `ThumbnailCard` components. Since `ThumbnailCard` was not memoized and the `onRegenerate` callback was created inline, every update to the list (e.g., regenerating one thumbnail) caused *all* thumbnails to re-render. This is a common React performance pitfall in lists.
**Action:** Wrapped `ThumbnailCard` in `React.memo` and used `useCallback` for the event handler in the parent component. Always ensure list items are memoized if they are expensive or numerous.
