## 2025-12-16 - [Frontend] Layout Thrashing in Event Handlers
**Learning:** `getBoundingClientRect()` forces a browser reflow (layout calculation). Calling it inside a high-frequency event handler like `mousemove` causes significant performance degradation ("layout thrashing").
**Action:** Cache layout dimensions (width, position) in `onMouseDown` (or `onTouchStart`) and use these cached values in the movement handler. This reduces work from "layout + paint" to just "paint" or "composite".

## 2025-12-16 - [Frontend] Coordinate Systems
**Learning:** `clientX` is relative to the viewport. `pageX` is relative to the document. When caching element position, `rect.left` is viewport-relative and invalidates on scroll.
**Action:** To be robust against scrolling, calculate document-relative position: `left = rect.left + window.scrollX`. Compare with `e.pageX` in the event handler.
