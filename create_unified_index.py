"""
Create unified index from Cortellis and Google Patents data
Lightweight version without large file operations
"""
import json
import os
import sys
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')

def create_unified_index():
    """Create unified index combining all data sources"""

    print("\n" + "=" * 80)
    print("UNIFIED INDEX CREATION")
    print("=" * 80)

    # Load existing data
    master_index = {}

    # Check Cortellis data
    if os.path.exists('processed_data/master_index.json'):
        with open('processed_data/master_index.json', 'r', encoding='utf-8') as f:
            cortellis_index = json.load(f)

        master_index['cortellis'] = {
            'available': True,
            'statistics': cortellis_index.get('statistics', {}),
            'files': cortellis_index.get('files', {}),
            'path': 'processed_data/'
        }
        print("\n✅ Cortellis data available")
        print(f"   Patents: {cortellis_index.get('statistics', {}).get('total_patents', 0)}")
        print(f"   Drugs: {cortellis_index.get('statistics', {}).get('total_drugs', 0)}")
    else:
        master_index['cortellis'] = {'available': False}
        print("\n⚠️  Cortellis data not found")

    # Check Google Patents cache
    google_cache_dir = 'cache/google_patents'
    if os.path.exists(google_cache_dir):
        cached_files = [f for f in os.listdir(google_cache_dir) if f.endswith('.json')]
        master_index['google_patents'] = {
            'available': True,
            'cached_searches': len(cached_files),
            'cache_dir': google_cache_dir
        }
        print("\n✅ Google Patents cache available")
        print(f"   Cached searches: {len(cached_files)}")
    else:
        master_index['google_patents'] = {'available': False}
        print("\n⚠️  Google Patents cache not found")

    # Create unified index
    master_index['metadata'] = {
        'created': datetime.now().isoformat(),
        'version': '2.0',
        'data_sources': []
    }

    if master_index['cortellis']['available']:
        master_index['metadata']['data_sources'].append('Cortellis')
    if master_index['google_patents']['available']:
        master_index['metadata']['data_sources'].append('Google Patents')

    # Save unified index
    os.makedirs('unified_patent_data', exist_ok=True)
    index_file = 'unified_patent_data/master_index.json'

    with open(index_file, 'w', encoding='utf-8') as f:
        json.dump(master_index, f, ensure_ascii=False, indent=2)

    print(f"\n✅ Unified index created: {index_file}")
    print(f"   Data sources: {', '.join(master_index['metadata']['data_sources'])}")

    # Create lightweight merged data reference (without copying large files)
    if master_index['cortellis']['available']:
        # Copy small files
        import shutil

        small_files = [
            'relationships.json',
            'patent_statistics.json',
            'drug_statistics.json',
            'master_index.json'
        ]

        for filename in small_files:
            src = f'processed_data/{filename}'
            dst = f'unified_patent_data/{filename}'
            if os.path.exists(src):
                shutil.copy2(src, dst)
                print(f"   Copied: {filename}")

        # Create symlinks or references for large files
        large_files_ref = {
            'patents': 'processed_data/patents_processed.json',
            'drugs': 'processed_data/drugs_processed.json'
        }

        ref_file = 'unified_patent_data/data_references.json'
        with open(ref_file, 'w', encoding='utf-8') as f:
            json.dump(large_files_ref, f, indent=2)

        print(f"   Created data references: data_references.json")

    print("\n" + "=" * 80)
    print("✅ UNIFIED INDEX COMPLETE!")
    print("=" * 80)

    return master_index

if __name__ == "__main__":
    create_unified_index()
