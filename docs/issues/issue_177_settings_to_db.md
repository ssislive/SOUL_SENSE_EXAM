# Issue #177: Migrate User Settings to Database

## Summary

Move user settings (question count, theme, sound effects) from JSON file storage to SQLite database for better data management and per-user settings support.

## Current Behavior

- Settings stored in `data/settings.json`
- Global settings (same for all usernames)
- Separate from exam data in database

```
data/settings.json
{
  "question_count": 5,
  "theme": "light",
  "sound_effects": true
}
```

## Proposed Behavior

- Settings stored in `user_settings` table
- Per-user settings (different users can have different preferences)
- Single source of truth (all data in database)

```sql
CREATE TABLE user_settings (
    id INTEGER PRIMARY KEY,
    username TEXT NOT NULL UNIQUE,
    question_count INTEGER DEFAULT 10,
    theme TEXT DEFAULT 'light',
    sound_effects BOOLEAN DEFAULT 1,
    language TEXT DEFAULT 'en',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Benefits

1. **Per-user settings** - Each user can have different question counts
2. **Data integrity** - Settings backed up with database
3. **Single source** - No separate JSON files to manage
4. **Extensibility** - Easy to add new settings columns

## Implementation Steps

- [ ] Create `user_settings` table in `app/models.py`
- [ ] Add migration script for existing users
- [ ] Update `app/utils.py` to read/write from DB
- [ ] Update GUI (`app/ui/settings.py`) to use DB
- [ ] Update CLI (`app/cli.py`) to use DB
- [ ] Add default settings on first exam/login
- [ ] Test migration with existing data

## Files to Modify

- `app/models.py` - Add UserSettings model
- `app/utils.py` - Replace JSON read/write with DB operations
- `app/ui/settings.py` - Update save/load logic
- `app/cli.py` - Update settings menu
- `scripts/migrate_settings.py` - New migration script

## Labels

`enhancement`, `database`, `refactoring`
