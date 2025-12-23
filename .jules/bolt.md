# Bolt's Journal ⚡

## 2025-05-18 - Missing Database Index on Thumbnails
**Learning:** Found that the `ix_images_profile_created` index was dropped in a previous migration (`392e04d439f5`) but never re-added, likely causing slow queries on the main dashboard which filters images by profile and sorts by creation date.
**Action:** Restored the index on `(profile_id, created_at)` to optimize the `list_thumbnails` query. Added `Index` to the SQLAlchemy model to ensure consistency.
