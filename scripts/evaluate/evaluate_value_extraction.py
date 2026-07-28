import json
import re
import sys
import os
import csv

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from api.openai import OpenAIClient
from api.anthropic import AnthropicClient

def load_dataset(path, num_entries):
    with open(path, 'r') as f:
        data = json.load(f)
    return data[:num_entries]

def extract_tags(masked_text):
    # Extract tags like {{ORGANIZATION}}, {{STREET_ADDRESS}}
    return re.findall(r'\{\{(.*?)\}\}', masked_text)

def build_prompt(full_text, masked_text):
    tags = extract_tags(masked_text)
    tags_str = ", ".join(set(tags))
    
    prompt = f"""You are an information extraction assistant.
I will provide you with a 'Full Text' and a 'Masked Text' containing tags like {{TAG_NAME}}.
Your task is to extract the exact values from the 'Full Text' that correspond to each mask in the 'Masked Text'.

Full Text:
{full_text}

Masked Text:
{masked_text}

Return the results as a JSON object where keys are the tag names and values are the extracted strings. 
If a tag appears multiple times, return a list of values in order of appearance.
Only return the JSON object, nothing else.
"""
    return prompt

def parse_llm_response(response):
    try:
        # Try to find JSON in the response if it's wrapped in code blocks or has extra text
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
        return json.loads(response)
    except Exception as e:
        print(f"Error parsing response: {e}")
        print(f"Raw response: {response}")
        return {}

def main():
    num_entries = 100
    dataset_path = 'data/synth_dataset_v2.json'
    data = load_dataset(dataset_path, num_entries)

    openai_client = OpenAIClient()
    anthropic_client = AnthropicClient()

    results = {
        'openai': {'matches': 0, 'mismatches': 0, 'data': []},
        'anthropic': {'matches': 0, 'mismatches': 0, 'data': []}
    }

    for i, entry in enumerate(data):
        print(f"Processing entry {i+1}/{len(data)}...")
        prompt = build_prompt(entry['full_text'], entry['masked'])
        messages = [{"role": "user", "content": prompt}]

        # OpenAI
        try:
            oa_resp = openai_client.chat(messages)
            oa_vals = parse_llm_response(oa_resp)
            
            # Store for CSV and accuracy
            spans = entry.get('spans', [])
            for span in spans:
                etype = span['entity_type']
                evalue = span['entity_value']
                ext_vals = oa_vals.get(etype, [])
                if isinstance(ext_vals, str):
                    ext_vals = [ext_vals]
                
                # Check if ground truth is in the extracted values
                is_match = evalue in ext_vals
                
                if is_match:
                    results['openai']['matches'] += 1
                else:
                    results['openai']['mismatches'] += 1

                results['openai']['data'].append({
                    'entry_id': i,
                    'tag': etype,
                    'ground_truth': evalue,
                    'llm_response': str(ext_vals),
                    'is_match': is_match
                })
        except Exception as e:
            print(f"OpenAI error on entry {i}: {e}")

        # Anthropic
        try:
            ant_resp = anthropic_client.chat(messages)
            ant_vals = parse_llm_response(ant_resp)
            
            # Store for CSV and accuracy
            spans = entry.get('spans', [])
            for span in spans:
                etype = span['entity_type']
                evalue = span['entity_value']
                ext_vals = ant_vals.get(etype, [])
                if isinstance(ext_vals, str):
                    ext_vals = [ext_vals]
                
                # Check if ground truth is in the extracted values
                is_match = evalue in ext_vals
                
                if is_match:
                    results['anthropic']['matches'] += 1
                else:
                    results['anthropic']['mismatches'] += 1

                results['anthropic']['data'].append({
                    'entry_id': i,
                    'tag': etype,
                    'ground_truth': evalue,
                    'llm_response': str(ext_vals),
                    'is_match': is_match
                })
        except Exception as e:
            print(f"Anthropic error on entry {i}: {e}")

    # Save to CSV
    results_dir = 'data/results'
    os.makedirs(results_dir, exist_ok=True)
    for model in ['openai', 'anthropic']:
        filename = os.path.join(results_dir, f'value_extraction_{model}.csv')
        with open(filename, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['entry_id', 'tag', 'ground_truth', 'llm_response', 'is_match'])
            writer.writeheader()
            writer.writerows(results[model]['data'])
        print(f"Saved results to {filename}")

    print("\n--- Benchmark Results ---")
    for model in ['openai', 'anthropic']:
        m = results[model]['matches']
        mm = results[model]['mismatches']
        acc = m / (m + mm) if (m + mm) > 0 else 0
        print(f"{model.capitalize()}: Matches={m}, Mismatches={mm}, Accuracy={acc:.2%}")

if __name__ == "__main__":
    main()
