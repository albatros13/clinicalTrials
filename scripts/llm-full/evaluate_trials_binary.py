import csv
import sys
import os
import xml.etree.ElementTree as ET

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

def parse_trial(trial_path):
    if not os.path.exists(trial_path):
        return None
    tree = ET.parse(trial_path)
    root = tree.getroot()
    
    title = root.findtext('brief_title', '')
    summary = root.find('brief_summary/textblock').text.strip() if root.find('brief_summary/textblock') is not None else ""
    description = root.find('detailed_description/textblock').text.strip() if root.find('detailed_description/textblock') is not None else ""
    criteria = root.find('eligibility/criteria/textblock').text.strip() if root.find('eligibility/criteria/textblock') is not None else ""
    
    return {
        'title': title,
        'summary': summary,
        'description': description,
        'criteria': criteria
    }

def get_llm_response(client, topic_text, trial_data):
    prompt = f"""Evaluate if the following clinical trial topic satisfies the requirements of the clinical trial.

### Topic Description:
{topic_text}

### Clinical Trial:
**Title:** {trial_data['title']}
**Summary:** {trial_data['summary']}
**Criteria:** {trial_data['criteria']}

### Instructions:
Answer only with a single integer (2, 1, or 0) followed by a newline and then your justification.
- **2**: Yes, the topic satisfies the requirements.
- **1**: No, the topic does not satisfy the requirements because the patient matches exclusion criteria.
- **0**: No, the topic is irrelevant to the trial.

Format:
Score: [0, 1, or 2]
Explanation: [Your justification]
"""
    messages = [{"role": "user", "content": prompt}]
    response = client.chat(messages)
    return response

def match_trials_to_patients(args):
    topics_path = 'data/eval/topics2021.xml'
    qrels_path = 'data/eval/selected_qrels2021.txt'
    trials_dir = 'data/eval/selected_trials'
    justification_path = 'data/output/evaluation_justifications.csv'
    
    topics = parse_topics(topics_path)
    
    if args["api"] == "openai":
        client = OpenAIClient()
    else:
        client = AnthropicClient()

    all_rows = []
    with open(qrels_path, 'r') as f:
        for line in f:
            if line.strip():
                all_rows.append(line.strip())

    updated_rows = all_rows.copy()
    
    for i in range(min(args["limit"], len(all_rows))):
        line = all_rows[i]
        parts = line.split()
        if len(parts) < 3:
            continue
        
        topic_id = parts[0]
        trial_id = parts[2]
        
        topic_text = topics.get(topic_id)
        trial_path = os.path.join(trials_dir, f"{trial_id}.xml")
        trial_data = parse_trial(trial_path)
        
        if not topic_text or not trial_data:
            print(f"Missing data for Topic {topic_id} or Trial {trial_id}")
            continue
            
        print(f"Evaluating Topic {topic_id} and Trial {trial_id}...")
        llm_output = get_llm_response(client, topic_text, trial_data)
        
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
                writer.writerow(['topic_id', 'trial_id', 'decision', 'method', 'justification'])
            writer.writerow([topic_id, trial_id, score, "full/" + args["api"], explanation])
            
        # Update original row with the score
        updated_rows[i] = f"{line} {score}"

    # Save all rows back to selected_qrels2021.txt
    with open(qrels_path, 'w') as f:
        for row in updated_rows:
            f.write(row + "\n")

def main():
    # Define configuration object here
    args = {
        "api": "anthropic",
        "limit": 10
    }
    match_trials_to_patients(args)

if __name__ == "__main__":
    main()
