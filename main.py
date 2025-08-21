#!/usr/bin/env python3
"""
I Ching Divination System - Main Entry Point
Dual-engine system with A-engine (Liu Yao) and B-engine (Takashima)
"""

import random
import sys
from engines.liuyau_engine import LiuyauEngine
from engines.takashima_engine import TakashimaEngine


def generate_hexagram():
    """Generate a random hexagram (1-64) for testing purposes."""
    return random.randint(1, 64)


def main():
    """Main menu system for choosing between engines."""
    print("=== I Ching Divination System ===")
    print("1. A-engine (Liu Yao with strict NaJia)")
    print("2. B-engine (Takashima with Zhouyi texts)")
    print("0. Exit")
    
    while True:
        try:
            choice = input("\nSelect engine (0-2): ").strip()
            
            if choice == "0":
                print("Goodbye!")
                sys.exit(0)
            elif choice == "1":
                print("\n=== A-engine (Liu Yao) ===")
                hexagram = generate_hexagram()
                engine = LiuyauEngine()
                engine.process_hexagram(hexagram)
            elif choice == "2":
                print("\n=== B-engine (Takashima) ===")
                hexagram = generate_hexagram()
                engine = TakashimaEngine()
                engine.process_hexagram(hexagram)
            else:
                print("Invalid choice. Please select 0, 1, or 2.")
                
        except KeyboardInterrupt:
            print("\nGoodbye!")
            sys.exit(0)
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    main()