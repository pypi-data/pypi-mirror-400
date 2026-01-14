"""
sot-verify CLI

Quick pass/fail verification for CI/CD pipelines
For detailed output with warnings, use sot-validator instead.
"""

import argparse
import sys
from pathlib import Path
from typing import List

from sot_validator import validate, __version__


def main(args: List[str] = None) -> int:
    """Main entry point for CLI"""
    parser = argparse.ArgumentParser(
        description='Quick pass/fail verification for Source of Truth (.sot) files',
        epilog='For detailed validation, use: sot-validator'
    )
    
    parser.add_argument(
        'files',
        nargs='*',
        help='Files to verify'
    )
    
    parser.add_argument(
        '-v', '--version',
        action='version',
        version=f'sot-verify {__version__}'
    )
    
    parser.add_argument(
        '-s', '--silent',
        action='store_true',
        help='No output, only exit code'
    )
    
    parsed = parser.parse_args(args)
    
    if not parsed.files:
        parser.print_help()
        return 0
    
    all_valid = True
    
    for file_path in parsed.files:
        path = Path(file_path)
        
        if not path.exists():
            if not parsed.silent:
                print(f'✗ {file_path}: NOT FOUND')
            all_valid = False
            continue
        
        try:
            content = path.read_text(encoding='utf-8')
        except Exception:
            if not parsed.silent:
                print(f'✗ {file_path}: READ ERROR')
            all_valid = False
            continue
        
        result = validate(content)
        
        if result.valid:
            if not parsed.silent:
                print(f'✓ {file_path}')
        else:
            if not parsed.silent:
                print(f'✗ {file_path}')
            all_valid = False
    
    return 0 if all_valid else 1


if __name__ == '__main__':
    sys.exit(main())
