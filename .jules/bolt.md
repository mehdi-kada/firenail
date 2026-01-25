## 2025-05-27 - [Frontend Verification Setup]
**Learning:** Frontend verification with Playwright in this codebase requires mocking Supabase environment variables in `.env.local` to prevent client-side crashes, and mocking API responses. `next/image` requires matching `remotePatterns` or using local images for verification.
**Action:** When running Playwright verification, create `.env.local` with dummy Supabase keys and use local images for `next/image` mocks.
