#!/usr/bin/env python3
"""
Smoke test script to validate Zhouyi text database and NaJia strict data.
Ensures all required data is present and properly formatted.
"""
import json
import os
import sys
from typing import Dict, List, Any


def test_zhouyi_database(textdb_path: str) -> bool:
    """Test Zhouyi text database completeness and format."""
    print("Testing Zhouyi text database...")
    
    zhouyi_file = os.path.join(textdb_path, 'zhouyi_text.json')
    
    if not os.path.exists(zhouyi_file):
        print(f"❌ Zhouyi text file not found: {zhouyi_file}")
        return False
    
    try:
        with open(zhouyi_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"❌ JSON parsing error: {e}")
        return False
    
    # Check all 64 hexagrams exist
    missing_hexagrams = []
    for i in range(1, 65):
        if str(i) not in data:
            missing_hexagrams.append(i)
    
    if missing_hexagrams:
        print(f"❌ Missing hexagrams: {missing_hexagrams}")
        return False
    
    # Check structure of each hexagram
    total_lines = 0
    errors = []
    
    for hex_num in range(1, 65):
        hex_key = str(hex_num)
        hex_data = data[hex_key]
        
        # Check required fields
        if 'name' not in hex_data:
            errors.append(f"Hexagram {hex_num}: missing 'name' field")
        elif not hex_data['name']:
            errors.append(f"Hexagram {hex_num}: empty name")
            
        if 'guaci' not in hex_data:
            errors.append(f"Hexagram {hex_num}: missing 'guaci' field")
        elif not hex_data['guaci']:
            errors.append(f"Hexagram {hex_num}: empty guaci")
            
        if 'yaoci' not in hex_data:
            errors.append(f"Hexagram {hex_num}: missing 'yaoci' field")
        else:
            yaoci = hex_data['yaoci']
            if not isinstance(yaoci, dict):
                errors.append(f"Hexagram {hex_num}: yaoci must be a dictionary")
            else:
                # Check all 6 lines exist
                for line_num in range(1, 7):
                    line_key = str(line_num)
                    if line_key not in yaoci:
                        errors.append(f"Hexagram {hex_num}: missing line {line_num}")
                    elif not yaoci[line_key]:
                        errors.append(f"Hexagram {hex_num}: empty line {line_num}")
                    else:
                        total_lines += 1
    
    if errors:
        print("❌ Structure errors found:")
        for error in errors[:10]:  # Show first 10 errors
            print(f"   {error}")
        if len(errors) > 10:
            print(f"   ... and {len(errors) - 10} more errors")
        return False
    
    print(f"✅ Zhouyi database: {len(data)} hexagrams, {total_lines} line texts")
    return True


def test_najia_strict_data(data_path: str) -> bool:
    """Test NaJia strict data completeness and format."""
    print("Testing NaJia strict data...")
    
    najia_file = os.path.join(data_path, 'na_jia_strict.json')
    
    if not os.path.exists(najia_file):
        print(f"❌ NaJia strict data file not found: {najia_file}")
        return False
    
    try:
        with open(najia_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"❌ JSON parsing error: {e}")
        return False
    
    errors = []
    
    # Check strict mode flag
    if not data.get('strict'):
        errors.append("Missing or false 'strict' flag")
    
    # Check trigram_branches
    if 'trigram_branches' not in data:
        errors.append("Missing 'trigram_branches' section")
    else:
        trigrams = ['乾', '兑', '离', '震', '巽', '坎', '艮', '坤']
        trigram_data = data['trigram_branches']
        
        for trigram in trigrams:
            if trigram not in trigram_data:
                errors.append(f"Missing trigram: {trigram}")
            else:
                branches = trigram_data[trigram]
                if not isinstance(branches, list) or len(branches) != 3:
                    errors.append(f"Trigram {trigram}: must have exactly 3 branches")
    
    # Check shi_ying positions
    if 'shi_ying' not in data:
        errors.append("Missing 'shi_ying' section")
    else:
        shi_ying_data = data['shi_ying']
        
        for hex_num in range(1, 65):
            hex_key = str(hex_num)
            if hex_key not in shi_ying_data:
                errors.append(f"Missing shi_ying for hexagram {hex_num}")
            else:
                positions = shi_ying_data[hex_key]
                if 'shi' not in positions or 'ying' not in positions:
                    errors.append(f"Hexagram {hex_num}: missing shi or ying position")
                else:
                    shi = positions['shi']
                    ying = positions['ying']
                    if not (1 <= shi <= 6) or not (1 <= ying <= 6):
                        errors.append(f"Hexagram {hex_num}: shi/ying positions must be 1-6")
                    if shi == ying:
                        errors.append(f"Hexagram {hex_num}: shi and ying cannot be the same position")
    
    # Check feifu configuration
    if 'feifu' not in data:
        errors.append("Missing 'feifu' section")
    else:
        feifu = data['feifu']
        if 'enable' not in feifu:
            errors.append("Missing feifu.enable flag")
        if 'rules' not in feifu:
            errors.append("Missing feifu.rules section")
    
    if errors:
        print("❌ Structure errors found:")
        for error in errors:
            print(f"   {error}")
        return False
    
    print(f"✅ NaJia strict data: 8 trigrams, 64 shi/ying positions, feifu enabled")
    return True


def test_engine_integration() -> bool:
    """Test LiuYao engine integration."""
    print("Testing LiuYao engine integration...")
    
    try:
        # Import engine
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'engines'))
        from liuyao_engine import LiuYaoEngine
        
        # Test basic mode
        basic_engine = LiuYaoEngine(strict_mode=False)
        plate = basic_engine.build_liuyao_plate(1)
        
        if not plate or 'hexagram' not in plate:
            print("❌ Basic engine failed to build plate")
            return False
        
        # Test strict mode
        strict_engine = LiuYaoEngine(strict_mode=True)
        plate = strict_engine.build_liuyao_plate(1)
        
        if not plate or 'hexagram' not in plate:
            print("❌ Strict engine failed to build plate")
            return False
        
        # Test text retrieval
        hex_text = strict_engine.get_hexagram_text(1)
        if 'name' not in hex_text or 'guaci' not in hex_text:
            print("❌ Failed to retrieve hexagram text")
            return False
        
        # Test multiple hexagrams
        test_hexagrams = [1, 2, 32, 63, 64]
        for hex_num in test_hexagrams:
            plate = strict_engine.build_liuyao_plate(hex_num, [1, 3, 5])
            if not plate or plate['hexagram'] != hex_num:
                print(f"❌ Failed to build plate for hexagram {hex_num}")
                return False
        
        print(f"✅ Engine integration: tested {len(test_hexagrams)} hexagrams successfully")
        return True
        
    except ImportError as e:
        print(f"❌ Engine import failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Engine test failed: {e}")
        return False


def main():
    """Run all smoke tests."""
    print("🧪 Zhouyi & NaJia Strict Data Smoke Tests")
    print("=" * 50)
    
    # Determine paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.dirname(script_dir)
    textdb_path = os.path.join(repo_root, 'textdb')
    data_path = os.path.join(repo_root, 'data')
    
    print(f"Repository root: {repo_root}")
    print(f"Text database path: {textdb_path}")
    print(f"Data path: {data_path}")
    print()
    
    # Run tests
    tests = [
        ("Zhouyi Text Database", lambda: test_zhouyi_database(textdb_path)),
        ("NaJia Strict Data", lambda: test_najia_strict_data(data_path)),
        ("Engine Integration", test_engine_integration)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append(result)
            print()
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append(False)
            print()
    
    # Summary
    print("📊 Test Summary")
    print("-" * 30)
    passed = sum(results)
    total = len(results)
    
    for i, (test_name, _) in enumerate(tests):
        status = "✅ PASS" if results[i] else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! System is ready.")
        return 0
    else:
        print("⚠️  Some tests failed. Please check the issues above.")
        return 1


if __name__ == "__main__":
    exit(main())