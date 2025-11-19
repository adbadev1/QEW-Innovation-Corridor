"""
Standalone Database Watcher Script
Monitors the FastAPI backend camera database and automatically exports to webapp

Usage:
    python watch_database.py              # Start watching with initial export
    python watch_database.py --no-export  # Start watching without initial export
    python watch_database.py --export-only # Export once and exit
"""
import sys
import argparse
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from fastapi_backend.watchers import DatabaseWatcher


def main():
    parser = argparse.ArgumentParser(
        description='Watch camera database and auto-export to webapp'
    )
    parser.add_argument(
        '--no-export',
        action='store_true',
        help='Skip initial export on startup'
    )
    parser.add_argument(
        '--export-only',
        action='store_true',
        help='Export once and exit (no watching)'
    )
    
    args = parser.parse_args()
    
    watcher = DatabaseWatcher()
    
    if args.export_only:
        # Just export and exit
        print("Export-only mode: Exporting latest collection...")
        result = watcher.export_now()
        if result:
            print(f"\n✓ Export completed successfully")
            sys.exit(0)
        else:
            print(f"\n✗ Export failed")
            sys.exit(1)
    
    # Normal watching mode
    if not args.no_export:
        print("Performing initial export before starting watcher...")
        watcher.export_now()
        print()
    
    # Start watching
    watcher.start()


if __name__ == '__main__':
    main()

