## 2024-05-23 - Missing Database Index
**Learning:** The `images` table in `backend/app/models/images.py` is missing the `ix_images_profile_created` index (covering `profile_id` and `created_at`) despite memory suggesting it was explicitly defined.
**Action:** In future sessions, verify database indexes against the actual model definitions and `alembic` migrations rather than relying solely on memory or documentation. Consider adding this index in a future migration to optimize the `thumbnails.list_thumbnails` query.
