import os
import xml.etree.ElementTree as ET
import json
import re

# Paths
QRELS_PATH = 'data/all/selected_qrels2021.txt'
TOPICS_PATH = 'data/eval/topics2021.xml'
TRIALS_DIR = 'data/eval/selected_trials'
POLICIES_DIR = 'data/policies'
INPUTS_DIR = 'data/output/inputs'

os.makedirs(POLICIES_DIR, exist_ok=True)
os.makedirs(INPUTS_DIR, exist_ok=True)

def parse_qrels(path):
    selected = []
    with open(path, 'r') as f:
        for line in f:
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

def generate_input_json(topic_id, text):
    # Simple extraction of age and gender if possible, otherwise just the text
    data = {
        "topic_id": topic_id,
        "patient_description": text
    }
    
    # Try to find age and gender
    age_match = re.search(r'(\d+)[-\s]year[-\s]old|(\d+)\syo|(\d+)\s[MF]', text, re.I)
    if age_match:
        age = next(g for g in age_match.groups() if g is not None)
        data["age"] = int(age)
    
    if re.search(r'\bman\b|\bmale\b|\b M \b', text, re.I):
        data["gender"] = "male"
    elif re.search(r'\bwoman\b|\bfemale\b|\b F \b', text, re.I):
        data["gender"] = "female"
        
    output_path = os.path.join(INPUTS_DIR, f"topic_{topic_id}.json")
    with open(output_path, 'w') as f:
        json.dump(data, f, indent=2)

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

default allow = false

# Eligibility Criteria:
# {sanitized_criteria}

allow {{
    input_matches_gender
    input_matches_age
}}

input_matches_gender {{
    "{gender}" == "All"
}}
input_matches_gender {{
    lower(input.gender) == lower("{gender}")
}}

input_matches_age {{
    age := input.age
    age_in_range(age)
}}

age_in_range(age) {{
    min_val := parse_age("{min_age}")
    max_val := parse_age("{max_age}")
    age >= min_val
    age <= max_val
}}

parse_age(s) = res {{
    s == "N/A"
    res := 0 # Or a very high number for max_age, but we'll handle it
}}
parse_age(s) = res {{
    s != "N/A"
    parts := split(s, " ")
    res := to_number(parts[0])
}}

# Overriding age_in_range for N/A cases
age_in_range(age) {{
    "{min_age}" == "N/A"
    "{max_age}" == "N/A"
}}
age_in_range(age) {{
    "{min_age}" != "N/A"
    "{max_age}" == "N/A"
    parts := split("{min_age}", " ")
    age >= to_number(parts[0])
}}
age_in_range(age) {{
    "{min_age}" == "N/A"
    "{max_age}" != "N/A"
    parts := split("{max_age}", " ")
    age <= to_number(parts[0])
}}
"""
        # Note: The above Rego is a bit simplified and might need refinement for actual OPA execution, 
        # but it follows the logic requested.
        
        output_path = os.path.join(POLICIES_DIR, f"trial_{trial_id}.rego")
        with open(output_path, 'w') as f:
            f.write(rego_content)
            
    except Exception as e:
        print(f"Error processing trial {trial_id}: {e}")

def main():
    qrels = parse_qrels(QRELS_PATH)
    topics_text = parse_topics(TOPICS_PATH)
    
    processed_topics = set()
    processed_trials = set()
    
    for topic_id, trial_id in qrels:
        if topic_id not in processed_topics:
            if topic_id in topics_text:
                generate_input_json(topic_id, topics_text[topic_id])
                processed_topics.add(topic_id)
        
        if trial_id not in processed_trials:
            generate_rego_policy(trial_id)
            processed_trials.add(trial_id)

if __name__ == "__main__":
    main()
