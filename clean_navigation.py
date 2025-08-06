#!/usr/bin/env python3
"""
Script to clean navigation content from processed JSONL files
"""
import json
import re

def is_navigation_content(text):
    """Check if text contains navigation/webpage content"""
    navigation_indicators = [
        "skip to main content", 
        "microsoft security", 
        "home * explore", 
        "solutions +", 
        "ai-powered cybersecurity", 
        "cloud security", 
        "data security & governance", 
        "privacy & risk management",
        "* products +",
        "* partners * resources"
    ]
    
    text_lower = text.lower()
    return any(indicator in text_lower for indicator in navigation_indicators)

def clean_jsonl_file(input_file, output_file):
    """Clean navigation content from JSONL file"""
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Clean sentences
    cleaned_sentences = []
    for i, sentence in enumerate(data.get('sentences', [])):
        sentence_text = sentence.get('text', '')
        if not is_navigation_content(sentence_text):
            cleaned_sentences.append(sentence)
        else:
            print(f"Removing navigation content from sentence {i}: {sentence_text[:100]}...")
    
    # Update data
    data['sentences'] = cleaned_sentences
    
    # Clean main text by removing first part if it's navigation content
    if 'text' in data:
        full_text = data['text']
        # Split by sentences and check first sentence
        sentences = re.split(r'(?<=[.!?])\s+', full_text)
        if sentences and is_navigation_content(sentences[0]):
            # Remove first sentence and rebuild text
            cleaned_text = ' '.join(sentences[1:])
            data['text'] = cleaned_text
            print("Cleaned main text by removing navigation content")
    
    # Clean graph nodes that reference removed sentences
    if 'graph_nodes' in data:
        cleaned_nodes = []
        for node in data['graph_nodes']:
            if node.get('meta', {}).get('sent_index') == 0:
                # Check if this node references navigation content
                node_text = node.get('meta', {}).get('text', '')
                if is_navigation_content(node_text) or node_text.lower() == 'attacker':
                    print(f"Removing navigation node: {node_text}")
                    continue
            cleaned_nodes.append(node)
        data['graph_nodes'] = cleaned_nodes
    
    # Save cleaned data
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"Cleaned file saved to: {output_file}")

if __name__ == "__main__":
    input_file = "data/campaign/output/thyphoon.jsonl"
    output_file = "data/campaign/output/thyphoon_cleaned.jsonl"
    clean_jsonl_file(input_file, output_file)