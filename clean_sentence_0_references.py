#!/usr/bin/env python3
"""
Script to clean sentence 0 references from existing JSONL files
"""
import json
import os
import glob

def clean_sentence_0_from_jsonl(file_path):
    """Remove all sentence 0 references from a JSONL file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        changes_made = False
        
        # Clean sentences array - remove sentence with id 0
        if 'sentences' in data:
            original_count = len(data['sentences'])
            data['sentences'] = [s for s in data['sentences'] if s.get('id', -1) != 0]
            if len(data['sentences']) != original_count:
                changes_made = True
                print(f"  Removed {original_count - len(data['sentences'])} sentence(s) with id=0")
        
        # Clean graph_nodes - remove nodes with sent_index 0
        if 'graph_nodes' in data:
            original_count = len(data['graph_nodes'])
            data['graph_nodes'] = [node for node in data['graph_nodes'] 
                                 if node.get('meta', {}).get('sent_index', -1) != 0]
            if len(data['graph_nodes']) != original_count:
                changes_made = True
                print(f"  Removed {original_count - len(data['graph_nodes'])} graph node(s) with sent_index=0")
        
        # Clean graph_edges - remove edges referencing removed nodes
        if 'graph_edges' in data:
            original_count = len(data['graph_edges'])
            # Remove edges that reference nodes with IDs 0-999 (sentence 0 node IDs)
            data['graph_edges'] = [edge for edge in data['graph_edges'] 
                                 if not (0 <= edge.get('source', -1) <= 999 or 0 <= edge.get('dest', -1) <= 999)]
            if len(data['graph_edges']) != original_count:
                changes_made = True
                print(f"  Removed {original_count - len(data['graph_edges'])} graph edge(s) referencing sentence 0 nodes")
        
        if changes_made:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"  Updated: {file_path}")
            return True
        else:
            print(f"  No changes needed: {file_path}")
            return False
            
    except Exception as e:
        print(f"  Error processing {file_path}: {e}")
        return False

def main():
    # Find all JSONL files in campaign output directory
    pattern = "data/campaign/output/*.jsonl"
    files = glob.glob(pattern)
    
    if not files:
        print(f"No JSONL files found matching pattern: {pattern}")
        return
    
    print(f"Found {len(files)} JSONL files to process:")
    
    total_updated = 0
    for file_path in files:
        print(f"\nProcessing: {file_path}")
        if clean_sentence_0_from_jsonl(file_path):
            total_updated += 1
    
    print(f"\nSummary: Updated {total_updated} out of {len(files)} files")

if __name__ == "__main__":
    main()