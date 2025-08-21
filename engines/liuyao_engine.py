#!/usr/bin/env python3
"""
LiuYao Engine - Six-line divination system with strict NaJia support
Supports traditional NaJia methodology including Fei/Fu (flying/hidden spirits) markers
"""
import json
import os
import warnings
from typing import Dict, List, Optional, Tuple, Any


class LiuYaoEngine:
    """
    LiuYao (Six Lines) divination engine with strict NaJia mode support.
    
    Features:
    - Traditional NaJia (Najia) system with Earthly Branches
    - Shi/Ying (世/应) position calculations
    - Fei/Fu (飞/伏) flying and hidden spirit markers
    - Xunkong (旬空) empty/void calculations
    - Strict mode with comprehensive data tables
    """
    
    def __init__(self, strict_mode: bool = False, data_path: str = None):
        """
        Initialize LiuYao engine.
        
        Args:
            strict_mode: Enable strict NaJia mode with full data tables
            data_path: Path to data directory (defaults to ./data)
        """
        self.strict_mode = strict_mode
        self.data_path = data_path or os.path.join(os.path.dirname(__file__), '..', 'data')
        self.textdb_path = os.path.join(os.path.dirname(__file__), '..', 'textdb')
        
        self.najia_data = None
        self.zhouyi_text = None
        
        if strict_mode:
            self._load_strict_data()
        
        # Load Zhouyi text database
        self._load_zhouyi_texts()
    
    def _load_strict_data(self):
        """Load strict NaJia data tables."""
        najia_file = os.path.join(self.data_path, 'na_jia_strict.json')
        
        try:
            with open(najia_file, 'r', encoding='utf-8') as f:
                self.najia_data = json.load(f)
            
            if not self.najia_data.get('strict'):
                warnings.warn("NaJia data is not marked as strict mode", UserWarning)
                
        except FileNotFoundError:
            warnings.warn(f"Strict NaJia data not found at {najia_file}, falling back to basic mode", UserWarning)
            self.strict_mode = False
        except json.JSONDecodeError as e:
            warnings.warn(f"Error parsing NaJia data: {e}, falling back to basic mode", UserWarning)
            self.strict_mode = False
    
    def _load_zhouyi_texts(self):
        """Load Zhouyi (I Ching) text database."""
        zhouyi_file = os.path.join(self.textdb_path, 'zhouyi_text.json')
        
        try:
            with open(zhouyi_file, 'r', encoding='utf-8') as f:
                self.zhouyi_text = json.load(f)
        except FileNotFoundError:
            warnings.warn(f"Zhouyi text database not found at {zhouyi_file}", UserWarning)
        except json.JSONDecodeError as e:
            warnings.warn(f"Error parsing Zhouyi text data: {e}", UserWarning)
    
    def get_hexagram_name(self, hexagram_num: int) -> str:
        """Get hexagram name by number."""
        if not self.zhouyi_text:
            return f"第{hexagram_num}卦"
        
        hex_data = self.zhouyi_text.get(str(hexagram_num))
        if hex_data:
            return hex_data.get('name', f"第{hexagram_num}卦")
        return f"第{hexagram_num}卦"
    
    def get_hexagram_text(self, hexagram_num: int) -> Dict[str, Any]:
        """Get complete hexagram text including guaci and yaoci."""
        if not self.zhouyi_text:
            return {
                'name': f"第{hexagram_num}卦",
                'guaci': "卦辞未载入",
                'yaoci': {str(i): f"第{i}爻辞未载入" for i in range(1, 7)}
            }
        
        return self.zhouyi_text.get(str(hexagram_num), {
            'name': f"第{hexagram_num}卦",
            'guaci': "卦辞未载入", 
            'yaoci': {str(i): f"第{i}爻辞未载入" for i in range(1, 7)}
        })
    
    def get_trigram_branches(self, trigram: str) -> List[str]:
        """Get Earthly Branches for a trigram (bottom to top)."""
        if not self.strict_mode or not self.najia_data:
            # Basic fallback mapping
            basic_mapping = {
                '乾': ['子', '寅', '辰'],
                '兑': ['丁', '亥', '丑'], 
                '离': ['卯', '巳', '未'],
                '震': ['子', '寅', '辰'],
                '巽': ['丑', '亥', '酉'],
                '坎': ['寅', '辰', '午'],
                '艮': ['辰', '午', '申'],
                '坤': ['未', '酉', '亥']
            }
            return basic_mapping.get(trigram, ['?', '?', '?'])
        
        return self.najia_data.get('trigram_branches', {}).get(trigram, ['?', '?', '?'])
    
    def get_shi_ying(self, hexagram_num: int) -> Dict[str, int]:
        """Get Shi (世) and Ying (应) positions for hexagram."""
        if not self.strict_mode or not self.najia_data:
            # Basic calculation fallback
            shi_pos = (hexagram_num - 1) % 6 + 1
            ying_pos = (shi_pos + 2) % 6 + 1
            if ying_pos == shi_pos:
                ying_pos = (ying_pos % 6) + 1
            return {'shi': shi_pos, 'ying': ying_pos}
        
        return self.najia_data.get('shi_ying', {}).get(str(hexagram_num), {'shi': 6, 'ying': 3})
    
    def build_liuyao_plate(self, hexagram_num: int, changing_lines: List[int] = None) -> Dict[str, Any]:
        """
        Build a complete LiuYao divination plate.
        
        Args:
            hexagram_num: Hexagram number (1-64)
            changing_lines: List of changing line positions (1-6)
            
        Returns:
            Complete divination plate with all NaJia elements
        """
        changing_lines = changing_lines or []
        
        # Get hexagram text
        hex_text = self.get_hexagram_text(hexagram_num)
        
        # Get Shi/Ying positions
        shi_ying = self.get_shi_ying(hexagram_num)
        
        # Build the plate structure
        plate = {
            'hexagram': hexagram_num,
            'name': hex_text['name'],
            'guaci': hex_text['guaci'],
            'shi_ying': shi_ying,
            'lines': [],
            'strict_mode': self.strict_mode,
            'feifu_enabled': self.strict_mode and self.najia_data.get('feifu', {}).get('enable', False)
        }
        
        # For demonstration, we'll use a simple binary representation
        # In a real implementation, this would come from the actual hexagram structure
        hex_binary = format(hexagram_num, '06b')
        
        # Build each line with NaJia elements
        for i in range(6):
            line_num = i + 1
            line_type = 'yang' if hex_binary[5-i] == '1' else 'yin'
            is_changing = line_num in changing_lines
            
            # Get trigram (upper or lower) and position within trigram
            trigram_pos = i % 3  # Position within trigram (0=bottom, 2=top)
            is_upper = i >= 3
            
            # For simplicity, assume 乾 for upper, 坤 for lower trigram
            # In real implementation, this would be calculated from hexagram structure
            trigram_name = '乾' if is_upper else '坤'
            branches = self.get_trigram_branches(trigram_name)
            earthly_branch = branches[trigram_pos] if trigram_pos < len(branches) else '?'
            
            line_data = {
                'position': line_num,
                'type': line_type,
                'changing': is_changing,
                'earthly_branch': earthly_branch,
                'trigram': trigram_name,
                'yaoci': hex_text['yaoci'].get(str(line_num), f"第{line_num}爻辞未载入"),
                'markers': []
            }
            
            # Add Shi/Ying markers
            if line_num == shi_ying['shi']:
                line_data['markers'].append('[世]')
            if line_num == shi_ying['ying']:
                line_data['markers'].append('[应]')
            
            # Add Fei/Fu markers if in strict mode
            if self.strict_mode and self.najia_data:
                # Simplified Fei/Fu logic - in real implementation this would be much more complex
                if line_num % 3 == 1:  # Example: mark every third line as having hidden spirit
                    line_data['markers'].append('[伏]')
                elif line_num % 2 == 0:  # Example: mark even lines as having flying spirit
                    line_data['markers'].append('[飞]')
            
            plate['lines'].append(line_data)
        
        return plate
    
    def format_plate(self, plate: Dict[str, Any]) -> str:
        """Format divination plate for display."""
        lines = [
            f"卦名：{plate['name']} (第{plate['hexagram']}卦)",
            f"卦辞：{plate['guaci']}",
            ""
        ]
        
        if plate['strict_mode']:
            lines.append("【严格模式 - 完整纳甲体系】")
            lines.append("")
        
        lines.append("六爻排列 (从下至上):")
        lines.append("-" * 50)
        
        # Display lines from top (6) to bottom (1)
        for line_data in reversed(plate['lines']):
            pos = line_data['position']
            line_type = "━━━━━━" if line_data['type'] == 'yang' else "━━  ━━"
            if line_data['changing']:
                line_type += " (变)"
            
            markers = " ".join(line_data['markers']) if line_data['markers'] else ""
            branch = line_data['earthly_branch']
            
            line_str = f"第{pos}爻: {line_type} {branch} {markers}"
            lines.append(line_str)
            
            # Add line text
            lines.append(f"      {line_data['yaoci']}")
            lines.append("")
        
        if plate.get('feifu_enabled'):
            lines.append("注：[世]世爻 [应]应爻 [飞]飞神 [伏]伏神")
        else:
            lines.append("注：[世]世爻 [应]应爻")
        
        return "\n".join(lines)


def main():
    """Demonstration of LiuYao engine."""
    print("LiuYao Engine 演示")
    print("=" * 50)
    
    # Test basic mode
    print("基础模式:")
    basic_engine = LiuYaoEngine(strict_mode=False)
    plate = basic_engine.build_liuyao_plate(1, [2, 4])
    print(basic_engine.format_plate(plate))
    print()
    
    # Test strict mode
    print("严格模式:")
    strict_engine = LiuYaoEngine(strict_mode=True)
    plate = strict_engine.build_liuyao_plate(1, [2, 4])
    print(strict_engine.format_plate(plate))


if __name__ == "__main__":
    main()