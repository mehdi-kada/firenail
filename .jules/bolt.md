## 2024-10-27 - Next.js Development Artifacts
**Learning:** Running `next dev` modifies `next-env.d.ts` to include local development types (e.g., `import "./.next/dev/types/routes.d.ts";`). This breaks builds in CI/CD or other environments where `.next` is not populated or different.
**Action:** Always verify `next-env.d.ts` is reverted to its clean state before creating a PR.
