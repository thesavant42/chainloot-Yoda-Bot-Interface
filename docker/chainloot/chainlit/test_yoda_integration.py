#!/usr/bin/env python3
"""
Test script to verify yoda-translator integration works correctly.
Run this script to validate the yoda translation functionality.
"""

import sys
import os

# Add the lib directory to Python path to import yoda module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'lib'))

def test_yoda_import():
    """Test that we can import the yoda module."""
    try:
        from yoda import translate
        print("✓ Successfully imported yoda.translate")
        return True
    except ImportError as e:
        print(f"✗ Failed to import yoda module: {e}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error importing yoda: {e}")
        return False

def test_yoda_translation():
    """Test basic yoda translation functionality."""
    try:
        from yoda import translate
        
        test_cases = [
            ("You are strong with the Force.", "Strong with the Force, you are."),
            ("I sense much anger in you.", "Much anger in you, I sense."),
            ("Size does not matter.", "Size matters not."),
            ("This is my home.", "My home, this is."),
            ("The dark side clouds everything.", "Everything, the dark side clouds.")
        ]
        
        print("\nTesting yoda translations:")
        all_passed = True
        
        for original, expected_pattern in test_cases:
            try:
                translated = translate(original)
                print(f"  Input:  '{original}'")
                print(f"  Output: '{translated}'")
                
                # Basic validation - check if it's different from input and not empty
                if translated and translated != original:
                    print("  ✓ Translation applied successfully")
                else:
                    print("  ⚠ Translation may not have been applied")
                    all_passed = False
                print()
                
            except Exception as e:
                print(f"  ✗ Translation failed: {e}")
                all_passed = False
                
        return all_passed
        
    except Exception as e:
        print(f"✗ Error during translation testing: {e}")
        return False

def test_spacy_model():
    """Test that SpaCy model loads correctly."""
    try:
        import spacy
        nlp = spacy.load("en_core_web_sm")
        doc = nlp("This is a test sentence.")
        print("✓ SpaCy en_core_web_sm model loaded successfully")
        print(f"  Processed {len(doc)} tokens")
        return True
    except OSError as e:
        print(f"✗ SpaCy model not found: {e}")
        print("  Run: python -m spacy download en_core_web_sm")
        return False
    except Exception as e:
        print(f"✗ Error loading SpaCy model: {e}")
        return False

def test_persona_condition():
    """Test the persona condition logic (simulated)."""
    print("\nTesting persona condition logic:")
    
    # Simulate the condition from chat.py
    test_scenarios = [
        ("Yoda", "Hello there, young padawan.", True),
        ("AI", "Hello, I am C-3PO.", False),
        ("Stark", "I am Iron Man.", False),
        ("Yoda", "", False),  # Empty string should not translate
        ("Yoda", "   ", False),  # Whitespace only should not translate
    ]
    
    all_passed = True
    
    for persona, text, should_translate in test_scenarios:
        # Simulate the condition: persona == "Yoda" and full_response.strip()
        condition_met = (persona == "Yoda" and text.strip())
        
        if condition_met == should_translate:
            print(f"  ✓ Persona: {persona}, Text: '{text}' -> Translate: {condition_met}")
        else:
            print(f"  ✗ Persona: {persona}, Text: '{text}' -> Expected: {should_translate}, Got: {condition_met}")
            all_passed = False
    
    return all_passed

def main():
    """Run all verification tests."""
    print("Yoda-Translator Integration Verification")
    print("=" * 45)
    
    tests = [
        ("SpaCy Model Load", test_spacy_model),
        ("Yoda Import", test_yoda_import),
        ("Yoda Translation", test_yoda_translation),
        ("Persona Condition Logic", test_persona_condition),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n--- {test_name} ---")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"✗ Test '{test_name}' crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 45)
    print("VERIFICATION SUMMARY")
    print("=" * 45)
    
    passed = 0
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"{status:>6}: {test_name}")
        if result:
            passed += 1
    
    print(f"\nResults: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("\n🎉 All verification tests passed! Integration ready for live testing.")
    else:
        print(f"\n⚠️  {len(results) - passed} test(s) failed. Please review before proceeding.")
    
    return passed == len(results)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)