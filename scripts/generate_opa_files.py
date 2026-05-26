import os
import sys
import xml.etree.ElementTree as ET
import json
import re

# Add project root to sys.path to allow importing from api
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from api.openai import OpenAIClient
from api.anthropic import AnthropicClient

# Paths
QRELS_PATH = 'data/all/selected_qrels2021.txt'
TOPICS_PATH = 'data/eval/topics2021.xml'
TRIALS_DIR = 'data/eval/selected_trials'
POLICIES_DIR = 'data/output/policies'
INPUTS_DIR = 'data/output/policy_inputs'

os.makedirs(POLICIES_DIR, exist_ok=True)
os.makedirs(INPUTS_DIR, exist_ok=True)

def parse_qrels(path, start_index, limit):
    selected = []
    with open(path, 'r') as f:
        lines = f.readlines()
        
    end_index = start_index + limit
    for line in lines[start_index:end_index]:
        parts = line.strip().split()
        if len(parts) >= 3:
            topic_id = parts[0]
            trial_id = parts[2]
            selected.append((topic_id, trial_id))
    return selected

def parse_topics(path):
    topics = {}
    tree = ET.parse(path)
    root = tree.getroot()
    for topic in root.findall('topic'):
        topic_num = topic.get('number')
        text = topic.text.strip()
        topics[topic_num] = text
    return topics

def generate_input_json(client, topic_id, text, trial_id):
    prompt = f"""Based on the following patient topic description, extract structured information for a clinical trial OPA policy input.
The trial ID is {trial_id}.

Topic Description:
{text}

Return the result ONLY as a JSON object with the following fields:
- age (integer, use 0 if not found)
- gender (string, "male", "female", or "unknown")
- conditions (list of strings representing medical conditions or symptoms)
- drugs (list of strings representing current medications)
- other_attributes (dictionary of any other relevant key-value pairs)

JSON Output:"""

    messages = [{"role": "user", "content": prompt}]
    response = client.chat(messages)

    try:
        # Clean response if LLM adds markdown backticks
        cleaned_response = response.strip()
        if cleaned_response.startswith("```json"):
            cleaned_response = cleaned_response[7:]
        if cleaned_response.endswith("```"):
            cleaned_response = cleaned_response[:-3]
        cleaned_response = cleaned_response.strip()
        
        data = json.loads(cleaned_response)
        data["topic_id"] = topic_id
        data["trial_id"] = trial_id
        
        output_path = os.path.join(INPUTS_DIR, f"topic_{topic_id}_trial_{trial_id}.json")
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2)
        return data
    except Exception as e:
        print(f"Error parsing LLM response for topic {topic_id}: {e}")
        # Fallback to simple extraction
        data = {
            "topic_id": topic_id,
            "trial_id": trial_id,
            "patient_description": text,
            "age": 0,
            "gender": "unknown"
        }
        output_path = os.path.join(INPUTS_DIR, f"topic_{topic_id}_trial_{trial_id}.json")
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2)
        return data

def generate_rego_policy(trial_id):
    trial_path = os.path.join(TRIALS_DIR, f"{trial_id}.xml")
    if not os.path.exists(trial_path):
        print(f"Warning: Trial file {trial_path} not found.")
        return

    try:
        tree = ET.parse(trial_path)
        root = tree.getroot()
        
        eligibility = root.find('eligibility')
        criteria_text = ""
        gender = "All"
        min_age = "N/A"
        max_age = "N/A"
        
        if eligibility is not None:
            criteria = eligibility.find('criteria')
            if criteria is not None:
                textblock = criteria.find('textblock')
                if textblock is not None:
                    criteria_text = textblock.text.strip()
            
            gender_elem = eligibility.find('gender')
            if gender_elem is not None:
                gender = gender_elem.text.strip()
            
            min_age_elem = eligibility.find('minimum_age')
            if min_age_elem is not None:
                min_age = min_age_elem.text.strip()

            max_age_elem = eligibility.find('maximum_age')
            if max_age_elem is not None:
                max_age = max_age_elem.text.strip()

        # Sanitize criteria_text for rego comments
        sanitized_criteria = criteria_text.replace('\n', '\n# ')
        
        rego_content = f"""package clinical_trial_{trial_id}

default allow := false

# Eligibility Criteria:
# {sanitized_criteria}

allow if {{
    input_matches_gender
    input_matches_age
}}

input_matches_gender if {{
    "{gender}" == "All"
}}
input_matches_gender if {{
    lower(input.gender) == lower("{gender}")
}}

input_matches_age if {{
    age := input.age
    age_in_range(age)
}}

age_in_range(age) if {{
    min_val := parse_age("{min_age}")
    max_val := parse_age("{max_age}")
    age >= min_val
    age <= max_val
}}

parse_age(s) = res if {{
    s == "N/A"
    res := 0 # Or a very high number for max_age, but we'll handle it
}}
parse_age(s) = res if {{
    s != "N/A"
    parts := split(s, " ")
    res := to_number(parts[0])
}}

# Overriding age_in_range for N/A cases
age_in_range(age) if {{
    "{min_age}" == "N/A"
    "{max_age}" == "N/A"
}}
age_in_range(age) if {{
    "{min_age}" != "N/A"
    "{max_age}" == "N/A"
    parts := split("{min_age}", " ")
    age >= to_number(parts[0])
}}
age_in_range(age) if {{
    "{min_age}" == "N/A"
    "{max_age}" != "N/A"
    parts := split("{max_age}", " ")
    age <= to_number(parts[0])
}}
"""
        print(f"Generating policy for {trial_id}...")
        # Note: The above Rego is a bit simplified and might need refinement for actual OPA execution, 
        # but it follows the logic requested.
        
        output_path = os.path.join(POLICIES_DIR, f"trial_{trial_id}.rego")
        with open(output_path, 'w') as f:
            f.write(rego_content)
            
    except Exception as e:
        print(f"Error processing trial {trial_id}: {e}")

def main():
    args = {
        "api": "anthropic",
        "limit": 5,
        "start_index": 0
    }

    if args["api"] == "openai":
        client = OpenAIClient()
    else:
        client = AnthropicClient()

    qrels = parse_qrels(QRELS_PATH, args["start_index"], args["limit"])
    topics_text = parse_topics(TOPICS_PATH)
    
    processed_trials = set()
    
    for topic_id, trial_id in qrels:
        print(f"Processing row: Topic {topic_id}, Trial {trial_id}")
        
        # Generate input JSON for this specific topic-trial pair
        if topic_id in topics_text:
            generate_input_json(client, topic_id, topics_text[topic_id], trial_id)
        else:
            print(f"Warning: Topic {topic_id} not found in topics XML.")
        
        # Generate Rego policy if not already done
        if trial_id not in processed_trials:
            generate_rego_policy(trial_id)
            processed_trials.add(trial_id)

if __name__ == "__main__":
    main()
