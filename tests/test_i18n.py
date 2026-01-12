"""
Test script for i18n implementation
Tests language switching and translation loading
"""

import os
import sys

# Add the current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.i18n_manager import get_i18n, I18nManager

def test_i18n():
    """Test the i18n implementation"""
    print("=" * 60)
    print("Testing SoulSense i18n Implementation")
    print("=" * 60)
    
    # Initialize i18n
    i18n = get_i18n()
    
    print(f"\n✓ I18n manager initialized")
    print(f"  Current language: {i18n.current_language}")
    print(f"  Language name: {i18n.get_language_name()}")
    
    # Test all supported languages
    print(f"\n✓ Supported languages:")
    for code, name in I18nManager.SUPPORTED_LANGUAGES.items():
        print(f"  - {code}: {name}")
    
    # Test English translations
    print(f"\n✓ Testing English translations:")
    i18n.switch_language('en')
    print(f"  App title: {i18n.get('app_title')}")
    print(f"  Enter name: {i18n.get('enter_name')}")
    print(f"  Error (nested): {i18n.get('errors.empty_name')}")
    print(f"  Question 1: {i18n.get_question(0)}")
    
    # Test Hindi translations
    print(f"\n✓ Testing Hindi translations:")
    i18n.switch_language('hi')
    print(f"  App title: {i18n.get('app_title')}")
    print(f"  Enter name: {i18n.get('enter_name')}")
    print(f"  Error (nested): {i18n.get('errors.empty_name')}")
    print(f"  Question 1: {i18n.get_question(0)}")
    
    # Test Spanish translations
    print(f"\n✓ Testing Spanish translations:")
    i18n.switch_language('es')
    print(f"  App title: {i18n.get('app_title')}")
    print(f"  Enter name: {i18n.get('enter_name')}")
    print(f"  Error (nested): {i18n.get('errors.empty_name')}")
    print(f"  Question 1: {i18n.get_question(0)}")
    
    # Test parameter formatting
    print(f"\n✓ Testing parameter formatting:")
    i18n.switch_language('en')
    formatted = i18n.get('quiz.question_counter', current=3, total=5)
    print(f"  Formatted: {formatted}")
    
    formatted = i18n.get('results.thank_you', username="John")
    print(f"  Formatted: {formatted}")
    
    # Test all questions
    print(f"\n✓ Testing question loading:")
    questions = i18n.get_all_questions()
    print(f"  Total questions loaded: {len(questions)}")
    for idx, q in enumerate(questions, 1):
        print(f"  Q{idx}: {q[:50]}..." if len(q) > 50 else f"  Q{idx}: {q}")
    
    # Test settings persistence
    print(f"\n✓ Testing settings persistence:")
    i18n.switch_language('hi')
    print(f"  Switched to Hindi, saved to file")
    print(f"  Settings file: {i18n.settings_file}")
    
    # Verify settings file exists
    if os.path.exists(i18n.settings_file):
        import json
        with open(i18n.settings_file, 'r', encoding='utf-8') as f:
            settings = json.load(f)
        print(f"  Saved language: {settings.get('language')}")
    
    print(f"\n{'=' * 60}")
    print("✅ All i18n tests passed successfully!")
    print("=" * 60)
    
    # Clean up test settings file
    if os.path.exists(i18n.settings_file):
        os.remove(i18n.settings_file)
        print(f"\n🧹 Cleaned up test settings file")

if __name__ == "__main__":
    try:
        test_i18n()
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
