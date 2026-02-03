## 2026-02-03 - [React.memo and Inline Functions]
**Learning:** `React.memo` is ineffective if the parent component passes inline functions as props, as these create new references on every render.
**Action:** When memoizing a child component, always ensure that callback props passed from the parent are stabilized using `useCallback`.
