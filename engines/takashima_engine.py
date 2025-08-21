"""
Takashima Engine (B-engine) - Uses Zhouyi text database
Displays hexagram information with classical Chinese texts
"""

import json
import os


class TakashimaEngine:
    """B-engine that processes hexagrams using Zhouyi text database."""
    
    def __init__(self):
        """Initialize the engine and load Zhouyi text database."""
        self.zhouyi_texts = self._load_zhouyi_texts()
    
    def _load_zhouyi_texts(self):
        """Load the Zhouyi text database from JSON file."""
        try:
            textdb_path = os.path.join(os.path.dirname(__file__), '..', 'textdb', 'zhouyi_text.json')
            with open(textdb_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print("Warning: zhouyi_text.json not found. Using placeholder texts.")
            return {}
        except json.JSONDecodeError as e:
            print(f"Error loading zhouyi_text.json: {e}")
            return {}
    
    def process_hexagram(self, hexagram_number):
        """Process and display hexagram information with Zhouyi texts."""
        if not (1 <= hexagram_number <= 64):
            print(f"Error: Invalid hexagram number {hexagram_number}. Must be 1-64.")
            return
        
        hex_key = str(hexagram_number)
        hexagram_data = self.zhouyi_texts.get(hex_key)
        
        if not hexagram_data:
            print(f"Error: No text data found for hexagram {hexagram_number}")
            return
        
        # Display hexagram information
        print(f"\n=== 第{hexagram_number}卦：{hexagram_data.get('name', '未知')} ===")
        print(f"卦辞：{hexagram_data.get('guaci', '无卦辞')}")
        
        # Display line texts (yaoci)
        yaoci = hexagram_data.get('yaoci', {})
        if yaoci:
            print("\n爻辞：")
            for i in range(1, 7):
                line_text = yaoci.get(str(i), f"第{i}爻：无爻辞")
                print(f"  {line_text}")
        else:
            print("无爻辞数据")
        
        print(f"\n--- Hexagram {hexagram_number} processing complete ---")
    
    def get_hexagram_info(self, hexagram_number):
        """Get hexagram information as a dictionary."""
        if not (1 <= hexagram_number <= 64):
            return None
        
        hex_key = str(hexagram_number)
        return self.zhouyi_texts.get(hex_key)