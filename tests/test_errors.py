import pytest
import os
import logging
import json
import tkinter as tk
from unittest.mock import MagicMock, patch
from sqlalchemy.exc import SQLAlchemyError
from app.exceptions import SoulSenseError, DatabaseError, ConfigurationError
from app.db import safe_db_context
from app.config import load_config, CONFIG_PATH
from app.logger import setup_logging
from app.main import show_error, global_exception_handler

# Test Exceptions
def test_exception_hierarchy():
    exc = DatabaseError("DB Error")
    assert isinstance(exc, SoulSenseError)
    assert isinstance(exc, Exception)

# Test Logger
def test_logger_setup(tmp_path):
    with patch("app.logger.LOG_DIR", str(tmp_path)):
        setup_logging()
        assert os.path.exists(tmp_path)
        logger = logging.getLogger()
        assert len(logger.handlers) > 0

# Test DB Handling
def test_safe_db_context_error():
    with patch("app.db.SessionLocal") as MockSession:
        mock_session = MockSession.return_value
        mock_session.commit.side_effect = SQLAlchemyError("Mock DB Error")
        
        with pytest.raises(DatabaseError) as excinfo:
            with safe_db_context() as session:
                pass
        
        assert "A database error occurred" in str(excinfo.value)
        mock_session.rollback.assert_called_once()

# Test Config Error
def test_load_config_missing_is_warning(caplog):
    # Missing config should warn and return defaults
    with patch("os.path.exists", return_value=False):
        cfg = load_config()
        assert "database" in cfg
        assert "Using defaults" in caplog.text or "not found" in caplog.text

def test_load_config_corrupt_raises():
    # Corrupt config should raise ConfigurationError
    with patch("os.path.exists", return_value=True), \
         patch("builtins.open", side_effect=json.JSONDecodeError("Corrupt", "doc", 0)):
        
        with pytest.raises(ConfigurationError):
            load_config()

# Test UI Error Handler
def test_global_exception_handler():
    with patch("app.main.show_error") as mock_show:
        # Args: self, exc_type, exc_value, traceback
        global_exception_handler(None, ValueError, ValueError("Test Error"), None)
        mock_show.assert_called_once()
        args = mock_show.call_args[0]
        assert args[0] == "Unexpected Error"

def test_show_error_logging():
    with patch("tkinter.messagebox.showerror") as mock_box, \
         patch("logging.error") as mock_log:
        
        err = RuntimeError("Test")
        show_error("Title", "Msg", err)
        
        mock_log.assert_called()
        mock_box.assert_called()
