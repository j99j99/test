# I Ching Divination System

A dual-engine I Ching divination system with comprehensive Zhouyi texts and strict NaJia data support.

## Features

### B-engine (Takashima Engine)
- Uses `textdb/zhouyi_text.json` for complete Zhouyi text database
- Provides public-domain Chinese texts for all 64 hexagrams (384 line texts)
- Displays classical guaci (hexagram statements) and yaoci (line statements)

### A-engine (Liu Yao Engine)  
- Supports strict mode with data loaded from `data/na_jia_strict.json`
- Full eight-trigram NaJia mapping with three Earthly Branches per trigram
- Shi/Ying positions for all 64 hexagrams per standard six-yao practice
- Fei/Fu (flying/hidden spirit) markers when applicable
- Graceful fallback to simplified mode if strict data is unavailable

## Usage

Run the main program:
```bash
python main.py
```

Select between:
- **A-engine (1)**: Liu Yao divination with strict NaJia analysis
- **B-engine (2)**: Classical Zhouyi text display

## Data Sources

### Zhouyi Texts (textdb/zhouyi_text.json)
Contains public-domain Chinese I Ching texts based on Wang Bi edition (王弼本通行文本). Includes:
- Hexagram names (卦名)
- Hexagram statements (卦辞) 
- Line statements for all 6 lines (爻辞)

### Strict NaJia Data (data/na_jia_strict.json)
Traditional Liu Yao divination data including:
- Trigram to Earthly Branch mappings for all 8 trigrams
- Shi/Ying (world/response) positions for all 64 hexagrams
- Fei/Fu (flying/hidden spirit) configuration and rules
- Replace with your preferred lineage data if needed

## Testing

Run the smoke test to validate data integrity:
```bash
python scripts/smoke_test.py
```

This validates JSON structure and ensures all 64 hexagrams with 384 line texts are present.

## Project Structure

```
├── main.py                    # Main entry point
├── engines/
│   ├── liuyau_engine.py      # A-engine (Liu Yao with strict NaJia)
│   └── takashima_engine.py   # B-engine (Zhouyi texts)
├── data/
│   └── na_jia_strict.json    # Strict NaJia mappings and rules
├── textdb/
│   └── zhouyi_text.json      # Complete Zhouyi text database
└── scripts/
    └── smoke_test.py         # Data validation tests
```