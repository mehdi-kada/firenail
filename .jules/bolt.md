# BOLT'S JOURNAL - CRITICAL LEARNINGS ONLY

## 2024-05-23 - Throttling UI Updates with requestAnimationFrame
**Learning:** Frequent state updates driven by `mousemove` or `touchmove` events can cause excessive re-renders and performance issues, especially on lower-end devices. Using `requestAnimationFrame` ensures that state updates are synchronized with the browser's repaint cycle (typically 60fps), preventing wasted work and ensuring smooth animations.
**Action:** When implementing drag or resize functionality, wrap the state update logic in `requestAnimationFrame`. Cancel any pending frames before requesting a new one to ensure only the latest event data is used for the next paint.
