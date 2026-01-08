"""
Quick Demo of EQ Progress Visualization
Shows the matplotlib graph in a standalone window
"""

import sqlite3
import matplotlib.pyplot as plt
from datetime import datetime

DB_PATH = "soulsense_db"

def demo_visualization():
    """Create a standalone visualization demo"""
    print("📊 Loading EQ Progress Data...")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Get data for test_user
    cursor.execute("""
        SELECT total_score, timestamp, id 
        FROM scores 
        WHERE username = 'test_user' 
        ORDER BY id
    """)
    data = cursor.fetchall()
    conn.close()
    
    if not data:
        print("❌ No data found for test_user. Run test_eq_tracking.py first!")
        return
    
    scores = [row[0] for row in data]
    print(f"✅ Found {len(scores)} EQ scores")
    
    # Create the graph
    plt.figure(figsize=(10, 6))
    
    # Plot line with markers
    plt.plot(range(1, len(scores) + 1), scores, 
            marker='o', linestyle='-', linewidth=2.5, markersize=10,
            color='#4CAF50', markerfacecolor='#2196F3', 
            markeredgewidth=2, markeredgecolor='#1976D2',
            label='EQ Score')
    
    # Fill area under curve
    plt.fill_between(range(1, len(scores) + 1), scores, alpha=0.3, color='#4CAF50')
    
    # Add value labels on each point
    for i, score in enumerate(scores):
        plt.annotate(str(score), 
                    xy=(i + 1, score), 
                    xytext=(0, 10),
                    textcoords='offset points',
                    ha='center',
                    fontsize=10,
                    fontweight='bold',
                    bbox=dict(boxstyle='round,pad=0.4', facecolor='yellow', alpha=0.8))
    
    # Formatting
    plt.xlabel('Attempt Number', fontsize=12, fontweight='bold')
    plt.ylabel('EQ Score', fontsize=12, fontweight='bold')
    plt.title('🎯 Your EQ Progress Journey', fontsize=14, fontweight='bold', pad=20)
    plt.grid(True, alpha=0.3, linestyle='--', linewidth=0.7)
    plt.xticks(range(1, len(scores) + 1))
    
    # Add statistics text box
    stats_text = (
        f"📊 Statistics:\n"
        f"Total Attempts: {len(scores)}\n"
        f"First Score: {scores[0]}\n"
        f"Latest Score: {scores[-1]}\n"
        f"Best Score: {max(scores)}\n"
        f"Average: {sum(scores)/len(scores):.1f}\n"
        f"Improvement: {((scores[-1]-scores[0])/scores[0]*100):+.1f}%"
    )
    
    plt.text(0.02, 0.98, stats_text,
            transform=plt.gca().transAxes,
            fontsize=10,
            verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    
    plt.tight_layout()
    print("✅ Visualization created! Close the window to exit.")
    plt.show()

if __name__ == "__main__":
    print("=" * 60)
    print("  EQ PROGRESS VISUALIZATION DEMO")
    print("=" * 60)
    demo_visualization()
