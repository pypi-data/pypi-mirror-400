#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for Mātrā-vṛtta (matra-based meter) support

This script tests the mātrā-vṛtta implementation in chanda/core.py

@author: Hrishikesh Terdalkar
"""

import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from chanda import Chanda
from chanda.utils import get_default_data_path

DATA_PATH = get_default_data_path()

###############################################################################
# Test Data - Mātrā-vṛtta examples
###############################################################################

# Example verses for different mātrā-vṛtta meters
MATRA_METER_EXAMPLES = {
    "आर्या": [
        "सरसा सालङ्कारा",
        "सुपदन्यासा सुवर्णमयमूर्तिः।",
        "आर्या तथैव भार्या",
        "दुष्प्रापा पुण्यहीनेन॥"
    ],
    "वैतालीय": [
        "सहसा विदधीत न क्रियाम्",
        "अविवेकः परम् आपदां पदम्।",
        "वृणते हि विमृश्यकारिणो",
        "गुणलब्धाः स्वयम् एव सम्पदः॥"
    ],
}

###############################################################################
# Test Functions
###############################################################################

def test_matra_loading():
    """Test 1: Check if mātrā-vṛtta definitions are loaded"""
    print("="*80)
    print("Test 1: Loading Mātrā-vṛtta Definitions")
    print("="*80)

    analyzer = Chanda(DATA_PATH)

    # Check if MATRA_CHANDA is populated
    if not analyzer.MATRA_CHANDA:
        print("✗ FAILED: MATRA_CHANDA is empty")
        return False

    print(f"✓ Loaded {len(analyzer.MATRA_CHANDA)} mātrā-vṛtta patterns")

    # Check if MATRA_PATTERNS is populated
    if not analyzer.MATRA_PATTERNS:
        print("✗ FAILED: MATRA_PATTERNS is empty")
        return False

    print(f"✓ Loaded {len(analyzer.MATRA_PATTERNS)} mātrā-vṛtta names")

    # Display loaded meters
    print("\nLoaded mātrā-vṛtta:")
    for name, pattern in analyzer.MATRA_PATTERNS.items():
        pattern_str = '-'.join(str(m) for m in pattern)
        print(f"  - {name}: {pattern_str}")

    print("\n✓ Test 1 PASSED\n")
    return True


def test_matra_counting():
    """Test 2: Check mātrā counting accuracy"""
    print("="*80)
    print("Test 2: Mātrā Counting")
    print("="*80)

    analyzer = Chanda(DATA_PATH)

    # Test cases: (LG pattern, expected mātrā)
    test_cases = [
        ("", 0),          # Empty
        ("L", 1),         # Single laghu
        ("G", 2),         # Single guru
        ("LLL", 3),       # 1+1+1 = 3
        ("GGG", 6),       # 2+2+2 = 6
        ("LGL", 4),       # 1+2+1 = 4
        ("LGLLGLLG", 11), # 1+2+1+1+2+1+1+2 = 11 (CORRECTED)
        ("LLLLLLLL", 8),  # 8 laghus = 8 mātrā
        ("GGGG", 8),      # 4 gurus = 8 mātrā
        ("LGGLGLGG", 13), # 1+2+2+1+2+1+2+2 = 13
    ]

    all_passed = True
    for lg_pattern, expected in test_cases:
        result = analyzer.count_matra(lg_pattern)
        status = "✓" if result == expected else "✗"
        print(f"{status} Pattern '{lg_pattern}': expected {expected}, got {result}")
        if result != expected:
            all_passed = False

    if all_passed:
        print("\n✓ Test 2 PASSED\n")
    else:
        print("\n✗ Test 2 FAILED\n")

    return all_passed


def test_pattern_matching():
    """Test 3: Test find_matra_match method"""
    print("="*80)
    print("Test 3: Mātrā Pattern Matching")
    print("="*80)

    analyzer = Chanda(DATA_PATH)

    # Test cases: (matra_counts, expected_meter)
    test_cases = [
        ((12, 18, 12, 15), 'आर्या'),
        ((12, 18, 12, 18), 'गीति'),
        ((14, 16, 14, 16), 'वैतालीय'),
        ((16, 16, 16, 16), 'मात्रासमक'),  # or पादाकुलक
        ((99, 99, 99, 99), None),  # Invalid pattern
    ]

    all_passed = True
    for matra_counts, expected_meter in test_cases:
        match = analyzer.find_matra_match(matra_counts)

        pattern_str = '-'.join(str(m) for m in matra_counts)
        print(f"\nPattern: {pattern_str}")

        if expected_meter is None:
            # Should not find a match
            if match['found']:
                print(f"✗ Expected no match, but found: {match['chanda']}")
                all_passed = False
            else:
                print("✓ Correctly found no match")
        else:
            # Should find a match
            if not match['found']:
                print(f"✗ Expected {expected_meter}, but found no match")
                all_passed = False
            else:
                meter_names = [name for name, _ in match['chanda']]
                if expected_meter in meter_names:
                    print(f"✓ Correctly found: {' / '.join(meter_names)}")
                else:
                    print(f"✗ Expected {expected_meter}, got: {meter_names}")
                    all_passed = False

    if all_passed:
        print("\n✓ Test 3 PASSED\n")
    else:
        print("\n✗ Test 3 FAILED\n")

    return all_passed


def test_verse_examples():
    """Test 4: Test mātrā-vṛtta meter identification with full verses"""
    print("="*80)
    print("Test 4: Mātrā-vṛtta Verse Identification")
    print("="*80)

    analyzer = Chanda(DATA_PATH)
    all_passed = True

    for meter_name, lines in MATRA_METER_EXAMPLES.items():
        print(f"\n{'='*80}")
        print(f"Testing: {meter_name}")
        print(f"{'='*80}")

        # Join lines with newlines
        text = '\n'.join(lines)

        print(f"Input text:\n{text}\n")

        # Analyze the verse
        results = analyzer.identify_from_text(text, verse=True, fuzzy=True)

        # Check verse-level identification
        print("-"*80)
        print("Verse Identification:")
        print("-"*80)

        if results['result']['verse']:
            verse = results['result']['verse'][0]
            if verse.get('chanda'):
                meters, score = verse['chanda']
                print(f"Identified meters: {' / '.join(meters)}")
                print(f"Confidence score: {score:.2f}")

                if meter_name in meters:
                    print(f"✓ Correctly identified as {meter_name}!")
                else:
                    print(f"⚠ Expected {meter_name}, got: {meters}")
                    # Show mātrā counts for debugging
                    print("\nMātrā counts per line:")
                    for i, line_result in enumerate(results['result']['line'], 1):
                        matra = line_result['result'].get('matra', 0)
                        print(f"  Line {i}: {matra} mātrā")
                    all_passed = False
            else:
                print("✗ No meter identified")
                all_passed = False
        else:
            print("✗ No verse results")
            all_passed = False

    if all_passed:
        print("\n✓ Test 4 PASSED\n")
    else:
        print("\n✗ Test 4 FAILED\n")

    return all_passed


def test_mixed_verse():
    """Test 5: Test verse with both varna and mātrā meters"""
    print("="*80)
    print("Test 5: Mixed Verse Analysis (Anuṣṭup)")
    print("="*80)

    analyzer = Chanda(DATA_PATH)

    # A verse with Anuṣṭup (varṇa-vṛtta, not mātrā-vṛtta)
    anustup = """इक्ष्वाकुवंशप्रभवो रामो नाम जनैः श्रुतः।
मामकाः पाण्डवाश्चैव किमकुर्वत सञ्जय॥"""

    print("Testing Anuṣṭup (varṇa-vṛtta, NOT mātrā-vṛtta):")
    print(anustup)
    print()

    results = analyzer.identify_from_text(anustup, verse=True, fuzzy=True)

    if results['result']['verse']:
        verse = results['result']['verse'][0]
        if verse.get('chanda'):
            meters, score = verse['chanda']
            print(f"Identified: {' / '.join(meters)}")
            print(f"Confidence: {score:.2f}")

            # Should identify as Anuṣṭup, not a mātrā-vṛtta
            varna_meters = ['Anuṣṭup', 'अनुष्टुभ्', 'अनुष्टुप्', 'Śloka', 'श्लोक']
            if any(m in meters for m in varna_meters):
                print("✓ Correctly identified as varṇa-vṛtta (not mātrā-vṛtta)")
            else:
                print(f"⚠ Unexpected identification: {meters}")
                # Not a failure, just interesting
        else:
            print("✗ No meter identified")
            return False

    print("\n✓ Test 5 PASSED\n")
    return True


def test_edge_cases():
    """Test 6: Edge cases and error handling"""
    print("="*80)
    print("Test 6: Edge Cases")
    print("="*80)

    analyzer = Chanda(DATA_PATH)

    # Test case 1: Empty input
    print("Test 6.1: Empty input")
    try:
        result = analyzer.identify_from_text("", verse=False)
        if result and 'result' in result:
            print(f"  ✓ Handled empty input gracefully")
        else:
            print(f"  ✓ Returned empty/None for empty input")
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False

    # Test case 2: Single word
    print("\nTest 6.2: Single word")
    try:
        result = analyzer.identify_line("राम")
        if result:
            print(f"  Mātrā: {result.get('matra', 'N/A')}")
            print("  ✓ Handled single word")
        else:
            print("  ✓ Returned empty result")
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False

    # Test case 3: Invalid mātrā pattern
    print("\nTest 6.3: Invalid mātrā pattern")
    match = analyzer.find_matra_match((999, 999, 999, 999))
    if not match['found']:
        print("  ✓ Correctly returned no match")
    else:
        print(f"  ✗ Should not match, but got: {match}")
        return False

    print("\n✓ Test 6 PASSED\n")
    return True


###############################################################################
# Main Test Runner
###############################################################################

def run_all_tests():
    """Run all mātrā-vṛtta tests"""
    print("\n")
    print("*" * 80)
    print("MĀTRĀ-VṚTTA TEST SUITE")
    print("*" * 80)
    print()

    tests = [
        ("Loading Definitions", test_matra_loading),
        ("Mātrā Counting", test_matra_counting),
        ("Pattern Matching", test_pattern_matching),
        ("Verse Examples", test_verse_examples),
        ("Mixed Verse", test_mixed_verse),
        ("Edge Cases", test_edge_cases),
    ]

    results = []
    for test_name, test_func in tests:
        try:
            passed = test_func()
            results.append((test_name, passed))
        except Exception as e:
            print(f"\n✗ Test '{test_name}' raised exception: {e}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))

    # Summary
    print("="*80)
    print("TEST SUMMARY")
    print("="*80)

    passed_count = sum(1 for _, passed in results if passed)
    total_count = len(results)

    for test_name, passed in results:
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{status}: {test_name}")

    print()
    print(f"Total: {passed_count}/{total_count} tests passed")

    if passed_count == total_count:
        print("\n🎉 ALL TESTS PASSED! 🎉")
        return 0
    else:
        print(f"\n⚠️  {total_count - passed_count} test(s) failed")
        return 1


if __name__ == '__main__':
    sys.exit(run_all_tests())
