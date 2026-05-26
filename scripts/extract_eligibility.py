import sys
import os
import xml.etree.ElementTree as ET
import json

# Add project root to sys.path to allow importing from api
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from api.openai import OpenAIClient
from api.anthropic import AnthropicClient

def parse_criteria(trial_path):
    if not os.path.exists(trial_path):
        return None
    try:
        tree = ET.parse(trial_path)
        root = tree.getroot()
        criteria = root.find('eligibility/criteria/textblock')
        if criteria is not None and criteria.text:
            return criteria.text.strip()
    except Exception as e:
        print(f"Error parsing {trial_path}: {e}")
    return ""

def extract_conditions_with_llm(client, criteria_text):
    prompt = f"""Extract the individual eligibility conditions from the following clinical trial criteria.
Return the result ONLY as a JSON array of strings.
Each string should represent one condition.
IMPORTANT: Add the prefix "Inclusion: " or "Exclusion: " to each condition whenever it is explicitly stated or clearly belongs to that category in the text.

Criteria Text:
{criteria_text}

JSON Output:"""
    
    messages = [{"role": "user", "content": prompt}]
    response = client.chat(messages)
    
    # Try to parse JSON from response
    try:
        # Clean response if LLM adds markdown backticks
        cleaned_response = response.strip()
        if cleaned_response.startswith("```json"):
            cleaned_response = cleaned_response[7:]
        if cleaned_response.endswith("```"):
            cleaned_response = cleaned_response[:-3]
        cleaned_response = cleaned_response.strip()
        
        return json.loads(cleaned_response)
    except Exception as e:
        print(f"Error parsing LLM response as JSON: {e}")
        print(f"Raw response: {response}")
        return [criteria_text] # Fallback to original text in a list if parsing fails

def main():
    config = {
        "api": "openai",
        "limit": 1000,
        "trials_dir": "data/eval/selected_trials",
        "input_file": "data/eval/eligibility_criteria.json",
        "output_file": "data/eval/eligibility_criteria.json",
        "batch_size": 10
    }
    
    if config["api"] == "openai":
        client = OpenAIClient()
    else:
        client = AnthropicClient() # Anthropic client uses its default model

    # Ensure output directory exists
    output_dir = os.path.dirname(config["output_file"])
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    results = []
    processed_ids = set()
    
    # Load existing entries to skip
    if os.path.exists(config["input_file"]):
        try:
            with open(config["input_file"], 'r', encoding='utf-8') as f:
                results = json.load(f)
                processed_ids = {r['id'] for r in results}
                print(f"Skipping {len(results)} existing entries from {config['input_file']}.")
        except Exception as e:
            print(f"Error loading existing input file: {e}. Starting fresh.")
            results = []
    
    trial_files = [f for f in os.listdir(config["trials_dir"]) if f.endswith('.xml')]
    trial_files.sort() # Ensure consistent order
    
    count = 0
    # Set limit to a small number for testing if needed
    limit = min(config["limit"], len(trial_files))
    
    # We want to process exactly 'limit' NEW trials, or all if less than limit
    new_to_process = []
    for filename in trial_files:
        trial_id = filename[:-4]
        if trial_id not in processed_ids:
            new_to_process.append(filename)
        if len(new_to_process) >= config["limit"]:
            break

    print(f"Found {len(new_to_process)} new trials to process.")

    try:
        for filename in new_to_process:
            trial_id = filename[:-4]
                
            trial_path = os.path.join(config["trials_dir"], filename)
            
            print(f"Processing {trial_id}...")
            try:
                criteria_text = parse_criteria(trial_path)
                
                if not criteria_text:
                    print(f"No criteria found for {trial_id}")
                    conditions = []
                else:
                    conditions = extract_conditions_with_llm(client, criteria_text)
                    
                results.append({
                    "id": trial_id,
                    "criteria": conditions
                })
                count += 1
            except Exception as e:
                print(f"Error processing {trial_id}: {e}. Skipping...")
                continue
            
            if count % config["batch_size"] == 0:
                with open(config["output_file"], 'w', encoding='utf-8') as f:
                    json.dump(results, f, indent=2, ensure_ascii=False)
                print(f"Batch saved: {len(results)} total entries.")

    except KeyboardInterrupt:
        print("\nInterrupted by user. Saving current progress...")
    except Exception as e:
        print(f"\nAn error occurred: {e}. Saving current progress...")
    finally:
        with open(config["output_file"], 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"Extraction complete. Results saved to {config['output_file']}")

if __name__ == "__main__":
    main()
