
import unittest
from unittest.mock import MagicMock, patch
import sys

# Patch tkinter BEFORE importing modules that use it
with patch.dict(sys.modules, {'tkinter': MagicMock(), 'tkinter.ttk': MagicMock()}):
    import tkinter as tk
    from tkinter import ttk

from app.services.exam_service import ExamSession

class TestGuiShim(unittest.TestCase):
    """Test GUI/Service integration without a real Tkinter window"""
    
    @patch('app.ui.exam.tk')
    @patch('app.ui.exam.ttk')
    def test_exam_manager_uses_session(self, mock_ttk, mock_tk):
        """Test that ExamManager creates and uses ExamSession"""
        # Import inside patch context
        from app.ui.exam import ExamManager
        
        # Setup mocks
        mock_tk.IntVar.return_value = MagicMock()
        mock_tk.Frame.return_value = MagicMock()
        mock_tk.Label.return_value = MagicMock()
        mock_tk.Button.return_value = MagicMock()
        mock_tk.Radiobutton.return_value = MagicMock()
        mock_tk.Text.return_value = MagicMock()
        mock_ttk.Style.return_value = MagicMock()
        mock_ttk.Progressbar.return_value = MagicMock()
        
        # Create mock app
        app = MagicMock()
        app.root = MagicMock()
        app.questions = [(1, "Test Question", "Tooltip", 10, 100)]
        app.username = "GuiTester"
        app.age = 25
        app.age_group = "Adult"
        app.colors = {
            "bg": "#fff", "surface": "#fff", "bg_secondary": "#eee",
            "text_primary": "#000", "text_secondary": "#333", 
            "text_tertiary": "#666", "border": "#ccc", "primary": "#00f",
            "primary_light": "#aaf", "surface_hover": "#ddd",
            "primary_hover": "#009", "text_inverse": "#fff"
        }
        app.clear_screen = MagicMock()
        
        # Create manager
        manager = ExamManager(app)
        
        # Start test - this should create an ExamSession
        manager.start_test()
        
        # Verify Session was created
        self.assertIsInstance(manager.session, ExamSession)
        self.assertEqual(manager.session.username, "GuiTester")
        self.assertEqual(manager.session.age, 25)
        
        # Verify Session State
        self.assertEqual(manager.session.current_question_index, 0)
        self.assertFalse(manager.session.is_finished())
        
        print("✅ GUI ExamManager integrated with ExamSession successfully.")

if __name__ == '__main__':
    unittest.main()
