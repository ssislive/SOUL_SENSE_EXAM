"""
Tests for Database Backup & Restore Module (Issue #345)
"""

import os
import pytest
import tempfile
import shutil
from datetime import datetime
from unittest.mock import patch, MagicMock

# Import the module under test
from app.db_backup import (
    create_backup,
    restore_backup,
    list_backups,
    delete_backup,
    BackupInfo,
    BACKUP_DIR,
    _validate_sqlite_file
)
from app.exceptions import DatabaseError


@pytest.fixture
def temp_backup_env(tmp_path, monkeypatch):
    """
    Set up a temporary environment for backup testing.
    Creates a temp DB file and temp backup directory.
    """
    # Create temp database
    db_path = tmp_path / "test_db.db"
    
    # Create a valid SQLite database
    import sqlite3
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE test (id INTEGER PRIMARY KEY, name TEXT)")
    cursor.execute("INSERT INTO test (name) VALUES ('test_value')")
    conn.commit()
    conn.close()
    
    # Create temp backup directory
    backup_dir = tmp_path / "backups"
    backup_dir.mkdir()
    
    # Patch the module constants
    monkeypatch.setattr("app.db_backup.DB_PATH", str(db_path))
    monkeypatch.setattr("app.db_backup.BACKUP_DIR", str(backup_dir))
    
    return {
        "db_path": str(db_path),
        "backup_dir": str(backup_dir),
        "tmp_path": tmp_path
    }


class TestCreateBackup:
    """Tests for create_backup function."""
    
    def test_create_backup_success(self, temp_backup_env):
        """Test successful backup creation."""
        result = create_backup()
        
        assert isinstance(result, BackupInfo)
        assert os.path.exists(result.path)
        assert result.size_bytes > 0
        assert result.filename.startswith("soulsense_backup_")
        assert result.filename.endswith(".db")
    
    def test_create_backup_with_description(self, temp_backup_env):
        """Test backup with custom description."""
        description = "Before major update"
        result = create_backup(description)
        
        assert result.description == description
        assert "Before_major_update" in result.filename
        
        # Check metadata file exists
        meta_path = result.path + ".meta"
        assert os.path.exists(meta_path)
        with open(meta_path, "r") as f:
            assert f.read().strip() == description
    
    def test_create_backup_description_sanitization(self, temp_backup_env):
        """Test that special characters in description are sanitized."""
        description = "Test<>:*?|backup"
        result = create_backup(description)
        
        # Filename should not contain special chars
        assert "<" not in result.filename
        assert ">" not in result.filename
        assert ":" not in result.filename
    
    def test_create_backup_db_not_found(self, temp_backup_env, monkeypatch):
        """Test error when database file doesn't exist."""
        monkeypatch.setattr("app.db_backup.DB_PATH", "/nonexistent/path/db.db")
        
        with pytest.raises(DatabaseError):
            create_backup()


class TestRestoreBackup:
    """Tests for restore_backup function."""
    
    def test_restore_backup_success(self, temp_backup_env):
        """Test successful backup restoration."""
        import sqlite3
        
        # Create a backup
        backup_info = create_backup("test backup")
        
        # Modify the original database
        conn = sqlite3.connect(temp_backup_env["db_path"])
        cursor = conn.cursor()
        cursor.execute("INSERT INTO test (name) VALUES ('modified')")
        conn.commit()
        conn.close()
        
        # Verify modification
        conn = sqlite3.connect(temp_backup_env["db_path"])
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM test")
        count_before = cursor.fetchone()[0]
        conn.close()
        assert count_before == 2
        
        # Restore from backup
        result = restore_backup(backup_info.path)
        assert result is True
        
        # Verify restoration
        conn = sqlite3.connect(temp_backup_env["db_path"])
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM test")
        count_after = cursor.fetchone()[0]
        conn.close()
        assert count_after == 1  # Should be back to original
    
    def test_restore_nonexistent_backup(self, temp_backup_env):
        """Test error when backup file doesn't exist."""
        with pytest.raises(DatabaseError) as exc_info:
            restore_backup("/nonexistent/backup.db")
        assert "not found" in str(exc_info.value)
    
    def test_restore_invalid_backup(self, temp_backup_env):
        """Test error when backup file is not valid SQLite."""
        # Create an invalid file
        invalid_path = os.path.join(temp_backup_env["backup_dir"], "invalid.db")
        with open(invalid_path, "w") as f:
            f.write("not a sqlite database")
        
        with pytest.raises(DatabaseError) as exc_info:
            restore_backup(invalid_path)
        assert "Invalid backup" in str(exc_info.value)


class TestListBackups:
    """Tests for list_backups function."""
    
    def test_list_backups_empty(self, temp_backup_env):
        """Test listing when no backups exist."""
        result = list_backups()
        assert result == []
    
    def test_list_backups_multiple(self, temp_backup_env):
        """Test listing multiple backups."""
        import time
        
        # Create several backups with small delay to ensure different timestamps
        backup1 = create_backup("first")
        time.sleep(0.01)  # Small delay to differentiate
        backup2 = create_backup("second")
        time.sleep(0.01)
        backup3 = create_backup("third")
        
        result = list_backups()
        
        assert len(result) == 3
        # Verify all descriptions are present
        descriptions = {b.description for b in result}
        assert descriptions == {"first", "second", "third"}
    
    def test_list_backups_with_info(self, temp_backup_env):
        """Test that backup info is correctly populated."""
        create_backup("test description")
        
        result = list_backups()
        
        assert len(result) == 1
        backup = result[0]
        assert isinstance(backup, BackupInfo)
        assert backup.description == "test description"
        assert backup.size_bytes > 0
        assert isinstance(backup.timestamp, datetime)


class TestDeleteBackup:
    """Tests for delete_backup function."""
    
    def test_delete_backup_success(self, temp_backup_env):
        """Test successful backup deletion."""
        backup_info = create_backup("to delete")
        assert os.path.exists(backup_info.path)
        
        result = delete_backup(backup_info.path)
        
        assert result is True
        assert not os.path.exists(backup_info.path)
    
    def test_delete_backup_removes_metadata(self, temp_backup_env):
        """Test that metadata file is also deleted."""
        backup_info = create_backup("with metadata")
        meta_path = backup_info.path + ".meta"
        
        assert os.path.exists(meta_path)
        
        delete_backup(backup_info.path)
        
        assert not os.path.exists(meta_path)
    
    def test_delete_nonexistent_backup(self, temp_backup_env):
        """Test error when backup doesn't exist."""
        with pytest.raises(DatabaseError):
            delete_backup("/nonexistent/backup.db")
    
    def test_delete_outside_backup_dir(self, temp_backup_env):
        """Test security check prevents deleting files outside backup dir."""
        # Try to delete a file outside the backup directory
        outside_file = os.path.join(temp_backup_env["tmp_path"], "outside.db")
        with open(outside_file, "w") as f:
            f.write("test")
        
        with pytest.raises(DatabaseError) as exc_info:
            delete_backup(outside_file)
        assert "outside backup directory" in str(exc_info.value)


class TestValidateSqliteFile:
    """Tests for _validate_sqlite_file helper."""
    
    def test_validate_valid_sqlite(self, temp_backup_env):
        """Test validation of valid SQLite file."""
        result = _validate_sqlite_file(temp_backup_env["db_path"])
        assert result is True
    
    def test_validate_invalid_file(self, temp_backup_env):
        """Test validation of non-SQLite file."""
        invalid_path = os.path.join(temp_backup_env["tmp_path"], "invalid.txt")
        with open(invalid_path, "w") as f:
            f.write("not a database")
        
        result = _validate_sqlite_file(invalid_path)
        assert result is False
    
    def test_validate_nonexistent_file(self, temp_backup_env):
        """Test validation of non-existent file."""
        result = _validate_sqlite_file("/nonexistent/file.db")
        assert result is False


class TestBackupInfo:
    """Tests for BackupInfo dataclass."""
    
    def test_size_display_bytes(self):
        """Test size display for small files."""
        info = BackupInfo(
            path="/test.db",
            filename="test.db",
            timestamp=datetime.now(),
            size_bytes=500
        )
        assert info.size_display == "500 B"
    
    def test_size_display_kilobytes(self):
        """Test size display for KB-sized files."""
        info = BackupInfo(
            path="/test.db",
            filename="test.db",
            timestamp=datetime.now(),
            size_bytes=2048
        )
        assert "KB" in info.size_display
    
    def test_size_display_megabytes(self):
        """Test size display for MB-sized files."""
        info = BackupInfo(
            path="/test.db",
            filename="test.db",
            timestamp=datetime.now(),
            size_bytes=2 * 1024 * 1024
        )
        assert "MB" in info.size_display
    
    def test_timestamp_display(self):
        """Test timestamp formatting."""
        timestamp = datetime(2026, 1, 15, 10, 30, 0)
        info = BackupInfo(
            path="/test.db",
            filename="test.db",
            timestamp=timestamp,
            size_bytes=1000
        )
        assert info.timestamp_display == "2026-01-15 10:30:00"
