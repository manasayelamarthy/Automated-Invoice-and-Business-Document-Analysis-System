# Isolated user workspaces

Phase 1 uses three synthetic users. Each user has an independent workspace:

- `user_001` - invoice review
- `user_002` - purchase-order verification
- `user_003` - contract and compliance review

The ingestion service must always receive a `user_id` and read/write only
inside that user's workspace. Documents must not be searched across users
unless a later feature explicitly adds controlled sharing.
