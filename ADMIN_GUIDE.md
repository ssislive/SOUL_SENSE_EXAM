# Admin Interface Guide

## Overview

The SoulSense Admin Interface provides authorized users with tools to manage questions in the database through both GUI and CLI interfaces.

## Features

- **GUI Admin Panel** - User-friendly graphical interface
- **CLI Tool** - Command-line interface for automation
- **Secure Access** - Password-protected admin accounts
- **CRUD Operations** - Create, Read, Update, Delete questions
- **Category Management** - Organize questions by category
- **Metadata Support** - Age range, difficulty, weight customization

---

## Getting Started

### 1. Create an Admin Account

**Option A: Using GUI**
```bash
python admin_interface.py
```
Click "Create Admin" button and fill in the form.

**Option B: Using CLI**
```bash
python admin_cli.py create-admin --no-auth
```

### 2. Login

Use the credentials you created to access the admin panel.

---

## GUI Interface

### Starting the GUI

```bash
python admin_interface.py
```

### Features

#### 📋 View Questions Tab
- Browse all questions in a table view
- Filter by category
- Show/hide inactive questions
- See question details at a glance

#### ➕ Add Question Tab
- Add new questions to the database
- Set category, age range, difficulty, weight
- Support for creating new categories

#### ✏️ Edit Question Tab
- Load existing questions by ID
- Modify question text and metadata
- Delete questions (soft delete)

#### 🏷️ Categories Tab
- View category statistics
- See question count per category
- Monitor category distribution

---

## CLI Interface

### Basic Commands

#### List All Questions
```bash
python admin_cli.py list
```

#### List Questions by Category
```bash
python admin_cli.py list --category "Self-Awareness"
```

#### Include Inactive Questions
```bash
python admin_cli.py list --inactive
```

#### View Specific Question
```bash
python admin_cli.py view --id 1
```

#### Add New Question
```bash
python admin_cli.py add
```
Follow the interactive prompts to enter question details.

#### Update Question
```bash
python admin_cli.py update --id 1
```
Enter new values or press Enter to keep current values.

#### Delete Question
```bash
python admin_cli.py delete --id 1
```
Confirm the deletion when prompted.

#### View Category Statistics
```bash
python admin_cli.py categories
```

#### Create New Admin User
```bash
python admin_cli.py create-admin
```

---

## Database Schema

### Questions Table

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key, auto-increment |
| text | TEXT | Question text (required) |
| category | TEXT | Category name (default: "General") |
| age_min | INTEGER | Minimum age (default: 12) |
| age_max | INTEGER | Maximum age (default: 100) |
| difficulty | INTEGER | Difficulty level 1-5 (default: 3) |
| weight | REAL | Question weight for scoring (default: 1.0) |
| created_at | TEXT | Creation timestamp |
| updated_at | TEXT | Last update timestamp |
| is_active | INTEGER | Active status (1=active, 0=inactive) |

### Admin Users Table

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key, auto-increment |
| username | TEXT | Admin username (unique) |
| password_hash | TEXT | SHA-256 hashed password |
| role | TEXT | User role (default: "admin") |
| created_at | TEXT | Account creation timestamp |

---

## Best Practices

### Question Writing Guidelines

1. **Be Clear and Specific**
   - Use simple, direct language
   - Avoid ambiguous terms
   - One concept per question

2. **Age-Appropriate**
   - Set appropriate age_min and age_max
   - Use vocabulary suitable for the target age range

3. **Consistent Format**
   - Use statements rather than questions
   - Keep consistent tone across questions
   - Use similar sentence structures

4. **Category Organization**
   - Use consistent category names
   - Create logical groupings
   - Consider using these standard categories:
     - Self-Awareness
     - Self-Management
     - Social Awareness
     - Relationship Management
     - General

### Difficulty Levels

- **1** - Very Easy (basic self-awareness)
- **2** - Easy (simple emotional recognition)
- **3** - Medium (standard EQ assessment)
- **4** - Hard (complex emotional situations)
- **5** - Very Hard (advanced emotional intelligence)

### Weight Guidelines

- **0.5** - Low importance questions
- **1.0** - Standard weight (default)
- **1.5-2.0** - Important questions
- **2.5+** - Critical core questions

---

## Security

### Password Requirements

- Minimum 4 characters
- SHA-256 encryption
- Unique usernames

### Access Control

- All operations require authentication
- Admin credentials stored securely
- No default admin account (must be created)

### Best Security Practices

1. Use strong passwords
2. Limit admin access to trusted users
3. Regularly review question changes
4. Backup database before bulk operations

---

## Troubleshooting

### Common Issues

**Issue: "Invalid credentials"**
- Solution: Verify username and password are correct
- Create new admin account if needed

**Issue: Cannot delete question**
- Solution: Questions are soft-deleted (is_active=0), not permanently removed
- Use database tools for permanent deletion if needed

**Issue: Changes not reflecting in app**
- Solution: Restart the application to reload questions
- Check question is_active status

**Issue: CLI import error**
- Solution: Install required package: `pip install tabulate`

---

## API Reference

### QuestionDatabase Class

#### Methods

**`add_question(text, category, age_min, age_max, difficulty, weight)`**
- Add a new question to the database
- Returns: question_id

**`update_question(question_id, text, category, age_min, age_max, difficulty, weight)`**
- Update an existing question
- Returns: Boolean (success/failure)

**`delete_question(question_id)`**
- Soft delete a question (sets is_active=0)
- Returns: Boolean (success/failure)

**`get_all_questions(include_inactive=False)`**
- Retrieve all questions
- Returns: List of question dictionaries

**`get_question_by_id(question_id)`**
- Get a specific question
- Returns: Question dictionary or None

**`get_categories()`**
- Get all unique categories
- Returns: List of category names

**`verify_admin(username, password)`**
- Verify admin credentials
- Returns: Boolean

**`create_admin(username, password)`**
- Create new admin account
- Returns: Boolean

---

## Examples

### Example 1: Bulk Add Questions

```python
from admin_interface import QuestionDatabase

db = QuestionDatabase()

questions = [
    ("You can recognize your emotions as they happen.", "Self-Awareness", 12, 25, 2, 1.0),
    ("You understand why you feel a certain way.", "Self-Awareness", 14, 30, 3, 1.0),
    ("You can control your emotions in stressful situations.", "Self-Management", 15, 35, 4, 1.5),
]

for q in questions:
    db.add_question(*q)
    print(f"Added: {q[0][:50]}...")
```

### Example 2: Export Questions

```python
from admin_interface import QuestionDatabase
import json

db = QuestionDatabase()
questions = db.get_all_questions()

with open('questions_backup.json', 'w') as f:
    json.dump(questions, f, indent=2)

print(f"Exported {len(questions)} questions")
```

### Example 3: Update Multiple Questions

```python
from admin_interface import QuestionDatabase

db = QuestionDatabase()
questions = db.get_all_questions()

# Update all questions in a category
for q in questions:
    if q['category'] == 'General':
        db.update_question(q['id'], category='Self-Awareness')

print("Updated category for all General questions")
```

---

## Support

For issues or questions:
1. Check this documentation
2. Review the code comments
3. Submit an issue on GitHub
4. Contact the development team

---

## Future Enhancements

Planned features:
- [ ] Bulk import from CSV/JSON
- [ ] Question versioning
- [ ] Usage analytics
- [ ] Multi-language support for admin panel
- [ ] Role-based permissions
- [ ] Audit logging
- [ ] Question templates
- [ ] Automated backups

---

**Happy Question Managing! 📝**
