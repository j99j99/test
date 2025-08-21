#!/usr/bin/env python3
"""
Smoke test script for validating JSON data structure
Validates zhouyi_text.json and na_jia_strict.json without executing calendar logic
"""

import json
import os
import sys


def test_zhouyi_text():
    """Test the Zhouyi text database structure."""
    print("Testing textdb/zhouyi_text.json...")
    
    try:
        # Load the JSON file
        script_dir = os.path.dirname(os.path.abspath(__file__))
        textdb_path = os.path.join(script_dir, '..', 'textdb', 'zhouyi_text.json')
        
        with open(textdb_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Check that we have all 64 hexagrams
        expected_keys = set(str(i) for i in range(1, 65))
        actual_keys = set(data.keys())
        
        if expected_keys != actual_keys:
            missing = expected_keys - actual_keys
            extra = actual_keys - expected_keys
            print(f"❌ Key validation failed!")
            if missing:
                print(f"   Missing keys: {sorted(missing)}")
            if extra:
                print(f"   Extra keys: {sorted(extra)}")
            return False
        
        # Check structure of each hexagram
        total_lines = 0
        for hex_num in range(1, 65):
            hex_key = str(hex_num)
            hex_data = data[hex_key]
            
            # Check required fields
            if 'name' not in hex_data:
                print(f"❌ Hexagram {hex_num} missing 'name' field")
                return False
            
            if 'guaci' not in hex_data:
                print(f"❌ Hexagram {hex_num} missing 'guaci' field")
                return False
            
            if 'yaoci' not in hex_data:
                print(f"❌ Hexagram {hex_num} missing 'yaoci' field")
                return False
            
            yaoci = hex_data['yaoci']
            if not isinstance(yaoci, dict):
                print(f"❌ Hexagram {hex_num} 'yaoci' is not a dictionary")
                return False
            
            # Check all 6 lines are present
            expected_lines = set(str(i) for i in range(1, 7))
            actual_lines = set(yaoci.keys())
            
            if expected_lines != actual_lines:
                print(f"❌ Hexagram {hex_num} missing line texts. Expected {expected_lines}, got {actual_lines}")
                return False
            
            total_lines += 6
        
        print(f"✅ Zhouyi text database validated successfully!")
        print(f"   - 64 hexagrams found")
        print(f"   - {total_lines} line texts (384 expected)")
        print(f"   - All required fields present")
        return True
        
    except FileNotFoundError:
        print(f"❌ File not found: {textdb_path}")
        return False
    except json.JSONDecodeError as e:
        print(f"❌ JSON decode error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


def test_na_jia_strict():
    """Test the strict NaJia data structure."""
    print("\nTesting data/na_jia_strict.json...")
    
    try:
        # Load the JSON file
        script_dir = os.path.dirname(os.path.abspath(__file__))
        data_path = os.path.join(script_dir, '..', 'data', 'na_jia_strict.json')
        
        with open(data_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Check strict flag
        if not data.get('strict', False):
            print("❌ 'strict' flag is not set to True")
            return False
        
        # Check trigram_branches
        if 'trigram_branches' not in data:
            print("❌ Missing 'trigram_branches' field")
            return False
        
        trigram_branches = data['trigram_branches']
        expected_trigrams = {"乾", "兑", "离", "震", "巽", "坎", "艮", "坤"}
        actual_trigrams = set(trigram_branches.keys())
        
        if expected_trigrams != actual_trigrams:
            print(f"❌ Trigram validation failed. Expected {expected_trigrams}, got {actual_trigrams}")
            return False
        
        # Check each trigram has 3 branches
        for trigram, branches in trigram_branches.items():
            if not isinstance(branches, list) or len(branches) != 3:
                print(f"❌ Trigram {trigram} should have exactly 3 branches, got {len(branches) if isinstance(branches, list) else 'non-list'}")
                return False
        
        # Check shi_ying
        if 'shi_ying' not in data:
            print("❌ Missing 'shi_ying' field")
            return False
        
        shi_ying = data['shi_ying']
        expected_hexagrams = set(str(i) for i in range(1, 65))
        actual_hexagrams = set(shi_ying.keys())
        
        if expected_hexagrams != actual_hexagrams:
            missing = expected_hexagrams - actual_hexagrams
            print(f"❌ Shi/Ying validation failed. Missing hexagrams: {sorted(missing) if missing else 'none'}")
            return False
        
        # Check each hexagram has shi and ying positions
        for hex_num in range(1, 65):
            hex_key = str(hex_num)
            positions = shi_ying[hex_key]
            
            if not isinstance(positions, dict):
                print(f"❌ Hexagram {hex_num} shi/ying is not a dictionary")
                return False
            
            if 'shi' not in positions or 'ying' not in positions:
                print(f"❌ Hexagram {hex_num} missing 'shi' or 'ying' position")
                return False
            
            shi = positions['shi']
            ying = positions['ying']
            
            if not (1 <= shi <= 6) or not (1 <= ying <= 6):
                print(f"❌ Hexagram {hex_num} invalid shi/ying positions: shi={shi}, ying={ying}")
                return False
        
        # Check feifu structure
        if 'feifu' not in data:
            print("❌ Missing 'feifu' field")
            return False
        
        feifu = data['feifu']
        if not isinstance(feifu, dict):
            print("❌ 'feifu' is not a dictionary")
            return False
        
        if not feifu.get('enable', False):
            print("⚠️  Fei/Fu is disabled")
        
        print(f"✅ Strict NaJia data validated successfully!")
        print(f"   - All 8 trigrams with branches present")
        print(f"   - Shi/Ying positions for all 64 hexagrams")
        print(f"   - Fei/Fu configuration present")
        return True
        
    except FileNotFoundError:
        print(f"❌ File not found: {data_path}")
        return False
    except json.JSONDecodeError as e:
        print(f"❌ JSON decode error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


def main():
    """Run all smoke tests."""
    print("=== I Ching Data Validation Smoke Tests ===")
    
    # Test both JSON files
    zhouyi_ok = test_zhouyi_text()
    najia_ok = test_na_jia_strict()
    
    print(f"\n=== Results ===")
    print(f"Zhouyi text database: {'✅ PASS' if zhouyi_ok else '❌ FAIL'}")
    print(f"NaJia strict data: {'✅ PASS' if najia_ok else '❌ FAIL'}")
    
    if zhouyi_ok and najia_ok:
        print(f"\n🎉 All tests passed! Data files are ready for use.")
        return 0
    else:
        print(f"\n💥 Some tests failed. Please check the data files.")
        return 1


if __name__ == "__main__":
    sys.exit(main())