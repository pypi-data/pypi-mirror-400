"""
cgd-validator CLI

Validate Clarity-Gated Document (.cgd) files from the command line
"""

import argparse
import json
import sys
from pathlib import Path
from typing import List

from . import validate, __version__


def main(args: List[str] = None) -> int:
    """Main entry point for CLI"""
    parser = argparse.ArgumentParser(
        description='Validate Clarity-Gated Document (.cgd) files for LLM-safe ingestion',
        epilog='Part of the Clarity Gate ecosystem: https://github.com/frmoretto/clarity-gate'
    )
    
    parser.add_argument(
        'files',
        nargs='*',
        help='Files to validate'
    )
    
    parser.add_argument(
        '-v', '--version',
        action='version',
        version=f'cgd-validator {__version__}'
    )
    
    parser.add_argument(
        '-q', '--quiet',
        action='store_true',
        help='Only output errors (no warnings)'
    )
    
    parser.add_argument(
        '--json',
        action='store_true',
        help='Output results as JSON'
    )
    
    parsed = parser.parse_args(args)
    
    if not parsed.files:
        parser.print_help()
        return 0
    
    has_errors = False
    results = []
    
    for file_path in parsed.files:
        path = Path(file_path)
        
        if not path.exists():
            print(f'Error: File not found: {file_path}', file=sys.stderr)
            has_errors = True
            continue
        
        try:
            content = path.read_text(encoding='utf-8')
        except Exception as e:
            print(f'Error reading {file_path}: {e}', file=sys.stderr)
            has_errors = True
            continue
        
        result = validate(content)
        
        result_dict = {
            'file': str(file_path),
            'valid': result.valid,
            'errors': [{'code': e.code, 'message': e.message, 'line': e.line} for e in result.errors],
            'warnings': [{'code': w.code, 'message': w.message, 'line': w.line} for w in result.warnings],
            'frontmatter': result.frontmatter,
            'version': result.version
        }
        results.append(result_dict)
        
        if not result.valid:
            has_errors = True
        
        if not parsed.json:
            if result.valid and not result.warnings:
                print(f'✓ {file_path}: PASS')
            elif result.valid:
                print(f'⚠ {file_path}: PASS with warnings')
                if not parsed.quiet:
                    for w in result.warnings:
                        print(f'  Warning: {w.message}')
            else:
                print(f'✗ {file_path}: FAIL')
                for e in result.errors:
                    print(f'  Error: {e.message}')
                if not parsed.quiet:
                    for w in result.warnings:
                        print(f'  Warning: {w.message}')
    
    if parsed.json:
        print(json.dumps(results, indent=2))
    
    return 1 if has_errors else 0


if __name__ == '__main__':
    sys.exit(main())
