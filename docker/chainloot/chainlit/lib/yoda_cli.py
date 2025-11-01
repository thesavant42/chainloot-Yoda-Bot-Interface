#!/usr/bin/env python3
"""
Yoda Translator CLI - Command-line interface for translating text to Yoda-speak

This script can:
1. Translate sentences provided as command-line arguments
2. Translate text files containing dialogue
3. Be used as a microservice for fast translation
"""

import argparse
import sys
import os
from pathlib import Path

# Import the yoda translator
try:
    from yoda import translate
except ImportError as e:
    print(f"Error: Unable to import yoda translator: {e}")
    print("Make sure yoda.py and its dependencies are available.")
    sys.exit(1)


def translate_sentence(sentence):
    """Translate a single sentence to Yoda-speak."""
    try:
        return translate(sentence)
    except Exception as e:
        print(f"Error translating sentence '{sentence}': {e}")
        return None


def translate_file(file_path):
    """Translate all lines in a text file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        translated_lines = []
        for i, line in enumerate(lines, 1):
            line = line.strip()
            if line:  # Skip empty lines
                translated = translate_sentence(line)
                if translated:
                    translated_lines.append(f"Line {i}: {line}")
                    translated_lines.append(f"Yoda:   {translated}")
                    translated_lines.append("")  # Empty line for readability
                else:
                    translated_lines.append(f"Line {i}: {line}")
                    translated_lines.append(f"Error:  Failed to translate")
                    translated_lines.append("")
        
        return "\n".join(translated_lines)
    
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        return None
    except Exception as e:
        print(f"Error reading file '{file_path}': {e}")
        return None


def main():
    parser = argparse.ArgumentParser(
        description="Translate English text to Yoda-speak",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --sentence "This is a normal sentence."
  %(prog)s --file dialogue.txt
  %(prog)s --sentence "You are strong with the Force."
  
For microservice use, pipe input:
  echo "Hello there" | %(prog)s --stdin
        """
    )
    
    # Create mutually exclusive group for input methods
    input_group = parser.add_mutually_exclusive_group(required=True)
    
    input_group.add_argument(
        '--sentence', '-s',
        type=str,
        help='Translate a single sentence'
    )
    
    input_group.add_argument(
        '--file', '-f',
        type=str,
        help='Path to a text file containing dialogue to translate'
    )
    
    input_group.add_argument(
        '--stdin',
        action='store_true',
        help='Read input from stdin (for piping)'
    )
    
    parser.add_argument(
        '--output', '-o',
        type=str,
        help='Output file path (default: print to stdout)'
    )
    
    parser.add_argument(
        '--quiet', '-q',
        action='store_true',
        help='Suppress extra output, only show translations'
    )

    args = parser.parse_args()
    
    # Process input based on arguments
    result = None
    
    if args.sentence:
        if not args.quiet:
            print(f"Original: {args.sentence}")
        translated = translate_sentence(args.sentence)
        if translated:
            result = f"Yoda: {translated}" if not args.quiet else translated
        else:
            print("Translation failed.")
            sys.exit(1)
    
    elif args.file:
        if not os.path.exists(args.file):
            print(f"Error: File '{args.file}' does not exist.")
            sys.exit(1)
        
        if not args.quiet:
            print(f"Translating file: {args.file}")
            print("-" * 50)
        
        result = translate_file(args.file)
        if result is None:
            sys.exit(1)
    
    elif args.stdin:
        try:
            lines = sys.stdin.read().strip().split('\n')
            translated_lines = []
            
            for line in lines:
                line = line.strip()
                if line:
                    translated = translate_sentence(line)
                    if translated:
                        if args.quiet:
                            translated_lines.append(translated)
                        else:
                            translated_lines.append(f"Original: {line}")
                            translated_lines.append(f"Yoda:     {translated}")
                            translated_lines.append("")
            
            result = "\n".join(translated_lines)
        
        except KeyboardInterrupt:
            print("\nOperation cancelled.")
            sys.exit(1)
        except Exception as e:
            print(f"Error reading from stdin: {e}")
            sys.exit(1)
    
    # Output result
    if result:
        if args.output:
            try:
                with open(args.output, 'w', encoding='utf-8') as f:
                    f.write(result)
                if not args.quiet:
                    print(f"Output saved to: {args.output}")
            except Exception as e:
                print(f"Error writing to output file '{args.output}': {e}")
                sys.exit(1)
        else:
            print(result)


if __name__ == "__main__":
    main()