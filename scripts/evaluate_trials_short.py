import csv
import sys
import os
import xml.etree.ElementTree as ET
import json

# Add project root to sys.path to allow importing from api
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from api.openai import OpenAIClient
from api.anthropic import AnthropicClient

def parse_topics(topics_path):
    topics = {}
    tree = ET.parse(topics_path)
    root = tree.getroot()
    for topic in root.findall('topic'):
        number = topic.get('number')
        text = topic.text.strip()
        topics[number] = text
    return topics

def load_eligibility_criteria(json_path):
    if not os.path.exists(json_path):
        return {}
    with open(json_path, 'r') as f:
        data = json.load(f)
    # Convert list to dictionary for O(1) lookup
    return {item['id']: item['criteria'] for item in data}

def get_llm_response(client, topic_text, criteria_list):
    criteria_text = "\n".join([f"- {c}" for c in criteria_list])
    
    prompt = f"""Evaluate if the following clinical trial topic satisfies the requirements of the clinical trial based on the criteria provided.

### Topic Description:
{topic_text}

### Clinical Trial Eligibility Criteria:
{criteria_text}

### Instructions:
Answer only with a single integer (2, 1, or 0) followed by a newline and then your justification.
- **2**: Yes, the topic satisfies the requirements.
- **1**: No, the topic does not satisfy the requirements because the patient matches exclusion criteria.
- **0**: No, the topic is irrelevant to the trial.

Only use the information provided in the topic description and criteria. Do not make up any additional information.
If the topic description does not provide enough information to make a decision, respond with 2.
Format:
Score: [0, 1, or 2]
Explanation: [Your justification]
"""
    messages = [{"role": "user", "content": prompt}]
    response = client.chat(messages)
    return response

def match_trials_to_patients(args):
    topics_path = args.get('topics_path', 'data/eval/topics2021.xml')
    qrels_path = args.get('qrels_path', 'data/eval/selected_qrels2021.txt')
    criteria_json_path = args.get('criteria_json_path', 'data/eval/eligibility_criteria.json')
    justification_path = args.get('justification_path', 'data/output/evaluation_justifications.csv')

    topics = parse_topics(topics_path)
    eligibility_map = load_eligibility_criteria(criteria_json_path)
    
    if args["api"] == "anthropic":
        client = OpenAIClient()
    else:
        client = AnthropicClient()

    all_rows = []
    with open(qrels_path, 'r') as f:
        for line in f:
            if line.strip():
                all_rows.append(line.strip())

    updated_rows = all_rows.copy()
    
    start_index = args.get("start_index", 0)
    processed_count = 0
    batch_size = 10

    for i in range(start_index, len(all_rows)):
        if processed_count >= args["limit"]:
            break
            
        line = all_rows[i]
        parts = line.split()
        if len(parts) < 3:
            continue
        
        topic_id = parts[0]
        trial_id = parts[2]
        
        topic_text = topics.get(topic_id)
        criteria_list = eligibility_map.get(trial_id)
        
        if not topic_text or criteria_list is None:
            # Skip if trial is not in the JSON
            print(f"Row {i}: Missing topic or criteria. Skipping LLM evaluation")
            continue
            
        print(f"Evaluating Row {i}: Topic {topic_id} and Trial {trial_id} (using short criteria)...")
        llm_output = get_llm_response(client, topic_text, criteria_list)
        
        # Parse score and explanation
        lines = llm_output.strip().split('\n')
        score = "0"
        explanation = llm_output
        for l in lines:
            if l.startswith("Score:"):
                score = l.replace("Score:", "").strip()
            elif l.startswith("Explanation:"):
                explanation = l.replace("Explanation:", "").strip()
        
        # Save justification
        file_exists = os.path.isfile(justification_path)
        with open(justification_path, 'a', newline='') as f_just:
            writer = csv.writer(f_just)
            if not file_exists:
                writer.writerow(['topic_id', 'trial_id', 'decision', 'llm', 'justification'])
            writer.writerow([topic_id, trial_id, score, "short/" + args["api"], explanation])
            
        # Update original row with the score
        updated_rows[i] = f"{line.strip()} {score}"
        processed_count += 1

        # Batch save every 10 rows or at the end
        if processed_count % batch_size == 0 or processed_count == args["limit"] or i == len(all_rows) - 1:
            print(f"Saving batch at row {i}...")
            with open(qrels_path, 'w') as f:
                for row in updated_rows:
                    f.write(row + "\n")

def main():
    # Define configuration object here
    args = {
        "api": "openai",
        "limit": 200,
        "start_index": 0
    }
    match_trials_to_patients(args)

if __name__ == "__main__":
    main()
