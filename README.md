# Zhouyi & LiuYao Divination System

A complete implementation of the I Ching (Zhouyi) divination system with advanced NaJia (纳甲) methodology support.

## Features

### Complete Zhouyi Text Database
- **Full 64 Hexagrams**: Complete traditional Chinese texts for all hexagrams
- **384 Line Texts**: All six line texts (yaoci 爻辞) for each hexagram  
- **Hexagram Statements**: Traditional hexagram statements (guaci 卦辞)
- **Public Domain**: Uses Wang Bi edition baseline texts (王弼本通行文本)

### Advanced NaJia (纳甲) System
- **Strict Mode**: Complete traditional NaJia methodology
- **Earthly Branches**: Full eight-trigram to Earthly Branch mappings
- **Shi/Ying Positions**: World (世) and Response (应) positions for all 64 hexagrams
- **Fei/Fu System**: Flying (飞神) and Hidden (伏神) spirit calculations
- **Xunkong Support**: Empty/void (旬空) position calculations

## Directory Structure

```
textdb/
  └── zhouyi_text.json       # Complete I Ching text database

data/
  └── na_jia_strict.json     # Strict NaJia data tables

engines/
  └── liuyao_engine.py       # LiuYao divination engine

scripts/
  └── smoke_test.py          # Validation and testing script
```

## Usage

### Basic LiuYao Engine

```python
from engines.liuyao_engine import LiuYaoEngine

# Basic mode
engine = LiuYaoEngine(strict_mode=False)
plate = engine.build_liuyao_plate(hexagram_num=1, changing_lines=[2, 4])
print(engine.format_plate(plate))
```

### Strict NaJia Mode

```python
# Strict mode with full NaJia system
strict_engine = LiuYaoEngine(strict_mode=True)
plate = strict_engine.build_liuyao_plate(hexagram_num=1, changing_lines=[1, 3, 5])

# Includes Fei/Fu markers and complete Earthly Branch mappings
print(strict_engine.format_plate(plate))
```

### Text Retrieval

```python
# Get hexagram text
hex_text = engine.get_hexagram_text(1)
print(f"Name: {hex_text['name']}")
print(f"Statement: {hex_text['guaci']}")
print(f"Line 1: {hex_text['yaoci']['1']}")
```

## Data Format

### Zhouyi Text Database (`textdb/zhouyi_text.json`)

```json
{
  "1": {
    "name": "乾",
    "guaci": "乾：元，亨，利，贞。",
    "yaoci": {
      "1": "初九：潜龙，勿用。",
      "2": "九二：见龙在田，利见大人。",
      ...
    }
  },
  ...
}
```

### NaJia Strict Data (`data/na_jia_strict.json`)

```json
{
  "strict": true,
  "trigram_branches": {
    "乾": ["子", "寅", "辰"],
    "兑": ["丁", "亥", "丑"],
    ...
  },
  "shi_ying": {
    "1": {"shi": 6, "ying": 3},
    ...
  },
  "feifu": {
    "enable": true,
    "rules": { ... }
  }
}
```

## Testing

Run the smoke test to validate all data and functionality:

```bash
python scripts/smoke_test.py
```

This validates:
- All 64 hexagrams present with complete text
- NaJia data structure and completeness
- Engine integration and functionality
- Strict mode features

## Traditional Chinese Divination Elements

### NaJia (纳甲) System Elements
- **世应 (Shi/Ying)**: World and Response positions showing key interaction points
- **飞伏 (Fei/Fu)**: Flying and Hidden spirits representing active/latent energies
- **旬空 (Xunkong)**: Empty/void positions based on the divination day
- **地支 (Earthly Branches)**: Twelve-branch system mapped to trigrams

### Markers in Output
- `[世]` - Shi (World) position
- `[应]` - Ying (Response) position  
- `[飞]` - Fei (Flying spirit)
- `[伏]` - Fu (Hidden spirit)

## License

This project uses public domain traditional Chinese texts. The code is available under standard open source terms.