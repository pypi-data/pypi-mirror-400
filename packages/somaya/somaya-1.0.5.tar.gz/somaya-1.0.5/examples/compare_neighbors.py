"""
Compare neighbors from feature-based and hybrid embeddings.

This script compares the overlap between search results from:
- Feature-based embeddings (results_feature.json)
- Hybrid embeddings (results_hybrid.json)

It calculates the overlap percentage for each probe term and the average overlap.
"""

import json
import os
import sys
from pathlib import Path

def load_json_file(filepath):
    """Load JSON file with error handling."""
    try:
        if not os.path.exists(filepath):
            print(f"[ERROR] File not found: {filepath}")
            return None
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        print(f"[ERROR] Invalid JSON in {filepath}: {e}")
        return None
    except Exception as e:
        print(f"[ERROR] Failed to load {filepath}: {e}")
        return None

def main():
    """Main function to compare neighbors."""
    # Get script directory
    script_dir = Path(__file__).parent
    
    # Load JSON files
    feature_file = script_dir / 'results_feature.json'
    hybrid_file = script_dir / 'results_hybrid.json'
    
    print("[INFO] Loading feature-based results...")
    f = load_json_file(feature_file)
    if f is None:
        print("[ERROR] Cannot continue without feature results")
        sys.exit(1)
    
    print("[INFO] Loading hybrid results...")
    h = load_json_file(hybrid_file)
    if h is None:
        print("[ERROR] Cannot continue without hybrid results")
        sys.exit(1)
    
    # Get probes
    probes = list(f.keys())
    if not probes:
        print("[ERROR] No probes found in feature results")
        sys.exit(1)
    
    print(f"\n[INFO] Comparing {len(probes)} probes...")
    print("-" * 60)
    
    total_overlap = 0.0
    valid_probes = 0
    
    for p in probes:
        try:
            # Get feature results
            feature_results = f.get(p, [])
            if not isinstance(feature_results, list):
                print(f"[WARNING] Invalid data for probe '{p}' in feature results")
                continue
            
            # Get hybrid results
            hybrid_results = h.get(p, [])
            if not isinstance(hybrid_results, list):
                print(f"[WARNING] Invalid data for probe '{p}' in hybrid results")
                continue
            
            # Calculate overlap
            setf = set([x.get('text', '') for x in feature_results if isinstance(x, dict)])
            seth = set([x.get('text', '') for x in hybrid_results if isinstance(x, dict)])
            
            # Calculate overlap percentage (assuming top 10 results)
            if len(setf) > 0:
                overlap = len(setf & seth) / max(len(setf), 1.0)
                overlap_percentage = overlap * 100.0
                print(f"{p:20s} overlap: {overlap_percentage:6.2f}% ({len(setf & seth)}/{len(setf)} common)")
                total_overlap += overlap
                valid_probes += 1
            else:
                print(f"{p:20s} overlap: N/A (no feature results)")
        except Exception as e:
            print(f"[ERROR] Error processing probe '{p}': {e}")
            continue
    
    # Calculate average overlap
    if valid_probes > 0:
        avg_overlap = (total_overlap / valid_probes) * 100.0
        print("-" * 60)
        print(f"Average overlap: {avg_overlap:.2f}% ({valid_probes} valid probes)")
    else:
        print("[ERROR] No valid probes processed")

if __name__ == "__main__":
    main()
