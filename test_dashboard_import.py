
import sys
import traceback
import tkinter as tk

print("Testing AnalyticsDashboard Import...")
try:
    from analytics_dashboard import AnalyticsDashboard
    print("✅ Successfully imported AnalyticsDashboard")
    
    root = tk.Tk()
    ad = AnalyticsDashboard(root, "test_user")
    print("✅ Successfully initialized AnalyticsDashboard")
    
    # Try opening it (this might fail if backend issues)
    ad.open_dashboard()
    print("✅ Successfully opened dashboard window")
    
    # root.destroy() # Don't destroy immediately to let it try rendering
    
except Exception as e:
    print("❌ Failed to import/init AnalyticsDashboard:")
    traceback.print_exc()
    print("❌ Failed to import/init AnalyticsDashboard:")
    traceback.print_exc()
