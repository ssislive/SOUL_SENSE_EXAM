
import sys
import traceback

print("Testing JournalFeature Import...")
try:
    from journal_feature import JournalFeature
    print("✅ Successfully imported JournalFeature")
    
    # Try initializing (headless, might fail on tk but we check imports)
    import tkinter as tk
    root = tk.Tk()
    jf = JournalFeature(root)
    print("✅ Successfully initialized JournalFeature")
    
except Exception as e:
    print("❌ Failed to import/init JournalFeature:")
    traceback.print_exc()
