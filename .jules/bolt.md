## 2025-05-15 - Initial Setup
**Learning:** Initializing Bolt's performance journal.
**Action:** Document critical performance learnings here.
## 2025-05-15 - Throttling Drag Events
**Learning:** Using `requestAnimationFrame` for dragging UI elements is powerful but requires capturing the *latest* event data in a ref, rather than relying on the event value from the throttled closure.
**Action:** When implementing RAF throttling in React, always pair it with a `useRef` to store the latest interaction coordinates.
