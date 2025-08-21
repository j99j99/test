"""
Liuyau Engine (A-engine) - Liu Yao divination with strict NaJia data
Supports strict mode with trigram branches, shi/ying positions, and fei/fu markers
"""

import json
import os


class LiuyauEngine:
    """A-engine that processes hexagrams using strict NaJia data for Liu Yao divination."""
    
    def __init__(self):
        """Initialize the engine and load strict NaJia data."""
        self.strict_data = self._load_strict_data()
        self.strict_mode = self.strict_data.get('strict', False)
        self.hexagram_names = self._get_hexagram_names()
    
    def _load_strict_data(self):
        """Load the strict NaJia data from JSON file."""
        try:
            data_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'na_jia_strict.json')
            with open(data_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print("Warning: na_jia_strict.json not found. Falling back to simplified mode.")
            return {"strict": False}
        except json.JSONDecodeError as e:
            print(f"Error loading na_jia_strict.json: {e}. Falling back to simplified mode.")
            return {"strict": False}
    
    def _get_hexagram_names(self):
        """Get hexagram names from basic mapping."""
        return {
            1: "乾", 2: "坤", 3: "屯", 4: "蒙", 5: "需", 6: "讼", 7: "师", 8: "比",
            9: "小畜", 10: "履", 11: "泰", 12: "否", 13: "同人", 14: "大有", 15: "谦", 16: "豫",
            17: "随", 18: "蛊", 19: "临", 20: "观", 21: "噬嗑", 22: "贲", 23: "剥", 24: "复",
            25: "无妄", 26: "大畜", 27: "颐", 28: "大过", 29: "坎", 30: "离", 31: "咸", 32: "恒",
            33: "遁", 34: "大壮", 35: "晋", 36: "明夷", 37: "家人", 38: "睽", 39: "蹇", 40: "解",
            41: "损", 42: "益", 43: "夬", 44: "姤", 45: "萃", 46: "升", 47: "困", 48: "井",
            49: "革", 50: "鼎", 51: "震", 52: "艮", 53: "渐", 54: "归妹", 55: "丰", 56: "旅",
            57: "巽", 58: "兑", 59: "涣", 60: "节", 61: "中孚", 62: "小过", 63: "既济", 64: "未济"
        }
    
    def _get_trigram_branches(self, hexagram_number):
        """Get earthly branches for hexagram lines based on trigram structure."""
        if not self.strict_mode:
            # Simplified fallback - just use basic sequence
            branches = ["子", "丑", "寅", "卯", "辰", "巳"]
            return branches
        
        trigram_branches = self.strict_data.get('trigram_branches', {})
        
        # This is a simplified approach - in practice, you'd need to determine
        # which trigrams make up the hexagram and map accordingly
        # For now, we'll use a basic mapping pattern
        upper_trigram = self._get_upper_trigram_name(hexagram_number)
        lower_trigram = self._get_lower_trigram_name(hexagram_number)
        
        upper_branches = trigram_branches.get(upper_trigram, ["午", "申", "戌"])
        lower_branches = trigram_branches.get(lower_trigram, ["子", "寅", "辰"])
        
        # Combine lower (lines 1-3) and upper (lines 4-6) trigram branches
        return lower_branches + upper_branches
    
    def _get_upper_trigram_name(self, hexagram_number):
        """Get upper trigram name - simplified mapping."""
        # This is a basic approximation - real implementation would decode hexagram structure
        trigrams = ["乾", "兑", "离", "震", "巽", "坎", "艮", "坤"]
        return trigrams[(hexagram_number - 1) // 8]
    
    def _get_lower_trigram_name(self, hexagram_number):
        """Get lower trigram name - simplified mapping."""
        # This is a basic approximation - real implementation would decode hexagram structure
        trigrams = ["乾", "兑", "离", "震", "巽", "坎", "艮", "坤"]
        return trigrams[(hexagram_number - 1) % 8]
    
    def _get_shi_ying_positions(self, hexagram_number):
        """Get shi and ying positions for the hexagram."""
        if not self.strict_mode:
            return {"shi": 5, "ying": 2}  # Default fallback
        
        shi_ying = self.strict_data.get('shi_ying', {})
        return shi_ying.get(str(hexagram_number), {"shi": 5, "ying": 2})
    
    def _get_feifu_markers(self, hexagram_number, line_number):
        """Get fei/fu markers for specific line."""
        if not self.strict_mode:
            return []
        
        feifu_data = self.strict_data.get('feifu', {})
        if not feifu_data.get('enable', False):
            return []
        
        positions = feifu_data.get('rules', {}).get('feifu_positions', {})
        hex_positions = positions.get(str(hexagram_number % 8 + 1), {"fei": [], "fu": []})
        
        markers = []
        if line_number in hex_positions.get('fei', []):
            markers.append('飞')
        if line_number in hex_positions.get('fu', []):
            markers.append('伏')
        
        return markers
    
    def process_hexagram(self, hexagram_number):
        """Process and display hexagram with Liu Yao analysis."""
        if not (1 <= hexagram_number <= 64):
            print(f"Error: Invalid hexagram number {hexagram_number}. Must be 1-64.")
            return
        
        hexagram_name = self.hexagram_names.get(hexagram_number, "未知")
        
        # Display header
        print(f"\n=== 第{hexagram_number}卦：{hexagram_name} (Liu Yao Analysis) ===")
        
        if self.strict_mode:
            print("严格模式：启用")
        else:
            print("简化模式：严格数据不可用")
        
        # Get hexagram data
        branches = self._get_trigram_branches(hexagram_number)
        shi_ying = self._get_shi_ying_positions(hexagram_number)
        
        print("\n六爻分析：")
        
        # Display each line with its information
        for i in range(6, 0, -1):  # Display from top to bottom (6th to 1st line)
            line_name = ["", "初", "二", "三", "四", "五", "上"][i]
            branch = branches[i-1] if i <= len(branches) else "未知"
            
            # Check for shi/ying positions
            position_marker = ""
            if i == shi_ying['shi']:
                position_marker += " [世]"
            if i == shi_ying['ying']:
                position_marker += " [应]"
            
            # Check for fei/fu markers
            feifu_markers = self._get_feifu_markers(hexagram_number, i)
            for marker in feifu_markers:
                position_marker += f" [{marker}]"
            
            print(f"  {line_name}爻：{branch}{position_marker}")
        
        # Additional information
        if self.strict_mode:
            print(f"\n世爻：第{shi_ying['shi']}爻")
            print(f"应爻：第{shi_ying['ying']}爻")
            
            # Palace information
            feifu_data = self.strict_data.get('feifu', {})
            palace_mapping = feifu_data.get('rules', {}).get('palace_mapping', {})
            palace = palace_mapping.get(str(hexagram_number % 8 + 1), "未知宫")
            print(f"所属宫：{palace}")
        
        print(f"\n--- Hexagram {hexagram_number} Liu Yao analysis complete ---")
    
    def get_hexagram_analysis(self, hexagram_number):
        """Get hexagram analysis as a dictionary."""
        if not (1 <= hexagram_number <= 64):
            return None
        
        return {
            'hexagram_number': hexagram_number,
            'name': self.hexagram_names.get(hexagram_number, "未知"),
            'strict_mode': self.strict_mode,
            'branches': self._get_trigram_branches(hexagram_number),
            'shi_ying': self._get_shi_ying_positions(hexagram_number)
        }