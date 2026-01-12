import sys
import os
import sqlite3
import unittest
from unittest.mock import MagicMock, patch
import io

# Add project root and scripts specific folder to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(project_root)
sys.path.append(os.path.join(project_root, 'scripts'))

from scripts.admin_cli import AdminCLI
from scripts.admin_interface import AdminInterface
from app.config import DB_PATH

class TestAdminAnalytics(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        """Setup test database with dummy scores"""
        cls.conn = sqlite3.connect(DB_PATH)
        cls.cursor = cls.conn.cursor()
        
        # Ensure scores table exists
        cls.cursor.execute("CREATE TABLE IF NOT EXISTS scores (total_score INTEGER, sentiment_score REAL, age INTEGER, username TEXT)")
        
        # Check if we have data, if not insert some
        cls.cursor.execute("SELECT COUNT(*) FROM scores")
        if cls.cursor.fetchone()[0] == 0:
            print("Injecting dummy data for verification...")
            data = [
                (35, 80.5, 25, 'user1'),
                (42, 45.0, 30, 'user2'),
                (28, -20.0, 18, 'user3'),
                (48, 90.0, 45, 'user4'),
                (30, 10.0, 22, 'user5')
            ]
            cls.cursor.executemany("INSERT INTO scores (total_score, sentiment_score, age, username) VALUES (?, ?, ?, ?)", data)
            cls.conn.commit()

    @classmethod
    def tearDownClass(cls):
        cls.conn.close()

    def test_cli_visual_stats(self):
        """Test CLI visual stats output"""
        print("\nTesting CLI Visual Stats...")
        cli = AdminCLI()
        
        # Redirect stdout to capture ASCII charts
        captured_output = io.StringIO()
        sys.stdout = captured_output
        
        try:
            cli.show_stats(visual=True)
        except Exception as e:
            self.fail(f"CLI validation failed: {e}")
        finally:
            sys.stdout = sys.__stdout__
            
        output = captured_output.getvalue()
        print("Captured Output Sample:\n", output[:200] + "...")
        
        self.assertIn("--- Total Score Distribution ---", output)
        self.assertIn("█", output)  # Check for ASCII bar character
        self.assertIn("Sentiment Score Distribution", output)

    @patch('scripts.admin_interface.tk')
    @patch('scripts.admin_interface.ttk')
    @patch('scripts.admin_interface.FigureCanvasTkAgg')
    def test_gui_analytics_init(self, mock_canvas, mock_ttk, mock_tk):
        """Test GUI init (smoke test)"""
        print("\nTesting GUI Analytics Initialization...")
        
        # Mock Tkinter elements
        mock_parent = MagicMock()
        mock_tk.Frame.return_value = MagicMock()
        
        app = AdminInterface()
        # Mock the window to avoid showing it
        app.main_window = MagicMock()
        
        try:
            app.create_analytics_tab(mock_parent)
            print("✓ Analytics tab created successfully")
        except Exception as e:
            self.fail(f"GUI validation failed: {e}")

if __name__ == '__main__':
    unittest.main()
