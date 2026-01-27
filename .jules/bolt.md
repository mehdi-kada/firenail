## 2026-01-27 - [Next.js Env File Drift]
**Learning:** Next.js dev server automatically modifies `next-env.d.ts` to include dev-specific types (`./.next/dev/types/routes.d.ts`), which is not suitable for production.
**Action:** Always revert changes to `next-env.d.ts` before committing, or ensure it is ignored in `.gitignore`.
