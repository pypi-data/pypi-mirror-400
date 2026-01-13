#!/usr/bin/env python3
"""Analyze OrKa trace files for deployment safety assessment"""

import json
import os
from pathlib import Path
from collections import defaultdict

def analyze_trace_file(file_path):
    """Analyze a single trace file"""
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    analysis = {
        'file': os.path.basename(file_path),
        'errors': 0,
        'successes': 0,
        'timeouts': 0,
        'error_messages': [],
        'blob_count': 0,
        'size_reduction': 0,
        'execution_times': [],
    }
    
    # Get metadata
    metadata = data.get('_metadata', {})
    analysis['blob_count'] = metadata.get('total_blobs_stored', 0)
    analysis['size_reduction'] = metadata.get('stats', {}).get('size_reduction', 0)
    
    # Analyze blob store
    blob_store = data.get('blob_store', {})
    
    def check_nested(obj, path=''):
        """Recursively check nested structures"""
        if isinstance(obj, dict):
            # Check status
            if 'status' in obj:
                if obj['status'] == 'error':
                    analysis['errors'] += 1
                    error_msg = obj.get('error', 'Unknown error')
                    if error_msg:
                        analysis['error_messages'].append(f"{path}: {error_msg}")
                elif obj['status'] == 'success':
                    analysis['successes'] += 1
            
            # Check execution time
            if 'execution_time_ms' in obj:
                exec_time = obj['execution_time_ms']
                if exec_time and exec_time > 60000:
                    analysis['timeouts'] += 1
                    analysis['execution_times'].append(exec_time)
            
            # Recurse
            for key, value in obj.items():
                check_nested(value, f"{path}.{key}" if path else key)
        
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                check_nested(item, f"{path}[{i}]")
    
    check_nested(blob_store)
    
    return analysis

def main():
    logs_dir = Path(__file__).parent
    trace_files = sorted(logs_dir.glob('orka_trace_*.json'))
    
    print(f"Analyzing {len(trace_files)} trace files...\n")
    
    total_errors = 0
    total_successes = 0
    total_timeouts = 0
    files_with_errors = []
    all_error_messages = []
    
    for trace_file in trace_files:
        try:
            analysis = analyze_trace_file(trace_file)
            
            if analysis['errors'] > 0:
                files_with_errors.append(analysis)
                all_error_messages.extend(analysis['error_messages'])
            
            total_errors += analysis['errors']
            total_successes += analysis['successes']
            total_timeouts += analysis['timeouts']
            
        except Exception as e:
            print(f"ERROR analyzing {trace_file}: {e}")
    
    # Print summary
    print("=" * 70)
    print("DEPLOYMENT SAFETY ASSESSMENT - TRACE FILE ANALYSIS")
    print("=" * 70)
    print(f"\nTotal files analyzed: {len(trace_files)}")
    print(f"Total error statuses: {total_errors}")
    print(f"Total success statuses: {total_successes}")
    print(f"Files with execution times > 60s: {total_timeouts}")
    print(f"\nFiles containing errors: {len(files_with_errors)}")
    
    if total_errors > 0:
        print(f"\nSuccess rate: {total_successes / (total_successes + total_errors) * 100:.2f}%")
    else:
        print(f"\nSuccess rate: 100.00%")
    
    # Error details
    if files_with_errors:
        print("\n" + "=" * 70)
        print("ERROR DETAILS")
        print("=" * 70)
        for file_analysis in files_with_errors:
            print(f"\nFile: {file_analysis['file']}")
            print(f"  Errors: {file_analysis['errors']}")
            print(f"  Error messages:")
            for msg in file_analysis['error_messages']:
                print(f"    - {msg}")
    
    # Categorize errors
    error_categories = defaultdict(int)
    for msg in all_error_messages:
        if 'No agent list at path' in msg:
            error_categories['Missing agent list'] += 1
        elif 'timeout' in msg.lower():
            error_categories['Timeout'] += 1
        elif not msg.strip() or msg == ': ':
            error_categories['Empty error (likely timeout)'] += 1
        else:
            error_categories['Other'] += 1
    
    if error_categories:
        print("\n" + "=" * 70)
        print("ERROR CATEGORIES")
        print("=" * 70)
        for category, count in sorted(error_categories.items(), key=lambda x: -x[1]):
            print(f"  {category}: {count}")
    
    # Recommendations
    print("\n" + "=" * 70)
    print("RECOMMENDATIONS")
    print("=" * 70)
    
    if total_errors == 0:
        print("✓ No errors detected - system appears stable")
    elif total_errors <= 5:
        print("⚠ Minor errors detected - review and fix before deployment")
    else:
        print("✗ Multiple errors detected - address issues before deployment")
    
    if total_timeouts > 0:
        print(f"⚠ {total_timeouts} operations exceeded 60s timeout - consider optimization")
    
    if error_categories.get('Missing agent list', 0) > 0:
        print("⚠ Agent list path errors detected - check workflow configuration")
    
    if error_categories.get('Empty error (likely timeout)', 0) > 0:
        print("⚠ Silent timeouts detected - likely LLM connection issues")

if __name__ == '__main__':
    main()
