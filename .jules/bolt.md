# Bolt's Journal - Critical Learnings

This journal tracks critical performance learnings, anti-patterns, and architectural bottlenecks.

## 2024-03-24 - List Rendering Optimization
**Learning:** The `ThumbnailsPage` was re-rendering all `ThumbnailCard` components whenever any state changed (like `isLoading`) or when regenerating a single thumbnail. This was due to `ThumbnailCard` missing `React.memo` and the `onRegenerate` callback being defined inline.
**Action:** Always wrap list item components in `React.memo` and use stable callbacks (`useCallback`) for event handlers passed to them, especially when the list can be long or items are complex.
