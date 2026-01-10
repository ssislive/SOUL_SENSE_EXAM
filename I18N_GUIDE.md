# Internationalization (i18n) Guide

## Overview

SoulSense now supports multiple languages! This guide explains how the internationalization system works and how to add new languages.

## Currently Supported Languages

- **English (en)** - Default
- **Hindi (hi)** - हिंदी
- **Spanish (es)** - Español

## How It Works

The application uses a centralized translation system:

1. **Translation Files**: Located in `locales/` directory
   - `en.json` - English translations
   - `hi.json` - Hindi translations
   - `es.json` - Spanish translations

2. **I18n Manager**: `i18n_manager.py` handles:
   - Loading translation files
   - Switching languages
   - Formatting strings with parameters
   - Persisting language preferences

3. **Language Switcher**: Available on the main screen
   - Dropdown menu to select language
   - Changes persist across sessions
   - Updates all UI elements immediately

## Adding a New Language

### Step 1: Create Translation File

1. Copy `locales/en.json` to `locales/{language_code}.json`
2. Translate all strings while keeping the structure
3. Ensure proper UTF-8 encoding

Example for French (`fr.json`):
```json
{
  "app_title": "Évaluation SoulSense",
  "user_details_title": "SoulSense - Détails de l'utilisateur",
  ...
}
```

### Step 2: Register the Language

Edit `i18n_manager.py` and add the language to `SUPPORTED_LANGUAGES`:

```python
SUPPORTED_LANGUAGES = {
    'en': 'English',
    'hi': 'हिंदी (Hindi)',
    'es': 'Español (Spanish)',
    'fr': 'Français (French)'  # Add this line
}
```

### Step 3: Test

1. Run the application
2. Select your new language from the dropdown
3. Verify all strings are translated correctly

## Translation File Structure

```json
{
  "app_title": "Application title",
  "errors": {
    "empty_name": "Error message for empty name"
  },
  "quiz": {
    "question_counter": "Question {current} of {total}"
  },
  "questions": [
    "Question 1 text",
    "Question 2 text",
    ...
  ]
}
```

## Using Translations in Code

### Import the i18n manager:
```python
from i18n_manager import get_i18n

i18n = get_i18n()
```

### Get a simple translation:
```python
title = i18n.get("app_title")
```

### Get a nested translation:
```python
error = i18n.get("errors.empty_name")
```

### Format with parameters:
```python
message = i18n.get("quiz.question_counter", current=1, total=5)
# Result: "Question 1 of 5"
```

### Get questions:
```python
question = i18n.get_question(0)  # First question
all_questions = i18n.get_all_questions()  # All questions
```

## Best Practices

1. **Keep keys consistent** across all language files
2. **Use descriptive keys** like `journal.save_analyze` instead of `btn1`
3. **Test with different languages** to ensure UI layout works
4. **Consider text length** - translations can be longer/shorter
5. **Use UTF-8 encoding** for all translation files
6. **Preserve placeholders** like `{username}` in translations

## Common Issues

### UI Elements Not Updating

If UI elements don't update when changing language, ensure you've:
- Called `update_ui_language()` after language change
- Updated all label references in the update function

### Missing Translations

If you see key names instead of translations:
- Check the key exists in the JSON file
- Verify the JSON structure matches
- Ensure no typos in key names

### Language Not Appearing

If your language doesn't show in the dropdown:
- Verify it's added to `SUPPORTED_LANGUAGES` in `i18n_manager.py`
- Restart the application
- Check the translation file is in `locales/` directory

## Contributing Translations

We welcome contributions for new languages! Please:

1. Fork the repository
2. Create a new translation file
3. Test thoroughly
4. Submit a pull request
5. Include translation credits in AUTHORS.md

Thank you for helping make SoulSense accessible to more people! 🌍
