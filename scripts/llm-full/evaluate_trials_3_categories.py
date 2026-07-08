import os
import xml.etree.ElementTree as ET
import sys

# Add project root to sys.path to allow importing from api
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

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

def parse_qrels(qrels_path):
    qrels = []
    with open(qrels_path, 'r') as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) >= 4:
                topic_id = parts[0]
                trial_id = parts[2]
                score = int(parts[3])
                qrels.append((topic_id, trial_id, score))
    return qrels

def extract_eligibility(xml_path):
    if not os.path.exists(xml_path):
        return None
    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()
        eligibility = root.find('eligibility')
        if eligibility is not None:
            # Get the whole eligibility XML element as a string
            # We use tostring to get all child elements content too
            eligibility_str = ET.tostring(eligibility, encoding='unicode', method='text')
            # Clean up extra whitespace/newlines
            lines = [line.strip() for line in eligibility_str.split('\n') if line.strip()]
            return "\n".join(lines)
    except Exception as e:
        print(f"Error parsing {xml_path}: {e}")
    return None

def get_llm_decision(client, topic_text, eligibility_text):
    prompt = f"""You are a clinical trial eligibility expert. 
Evaluate if the patient described below is eligible for the clinical trial based on the provided criteria.

### Patient Profile:
{topic_text}

### Clinical Trial Eligibility Criteria:
{eligibility_text}

### Instructions:
Evaluate the patient's eligibility and provide a score:
- **2**: ELIGIBLE. The patient satisfies all inclusion criteria and no exclusion criteria.
- **1**: NOT ELIGIBLE. The patient matches one or more exclusion criteria.
- **0**: NOT RELEVANT. The topic is irrelevant to this trial's condition at all.

Provide your answer in the following format:
Score: [0, 1, or 2]
Reason: [Short explanation]
"""
    messages = [{"role": "user", "content": prompt}]
    try:
        response = client.chat(messages)
        return response
    except Exception as e:
        return f"Error: {e}"

def main():
    # Configuration
    limit = 100
    api = "openai"
    output_path = f"data/results/evaluation_results-{api}.txt"

    output_f = None
    if output_path:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        output_f = open(output_path, 'w')

    def log(message):
        print(message)
        if output_f:
            output_f.write(str(message) + "\n")

    topics_path = 'data/all/topics2021.xml'
    qrels_path = 'data/all/selected_qrels2021.txt'
    trials_dir = 'data/eval/selected_trials'

    log("Loading topics...")
    topics = parse_topics(topics_path)
    log("Loading qrels...")
    qrels = parse_qrels(qrels_path)

    if api == "openai":
        client = OpenAIClient() # Uses default gpt-5
    else:
        client = AnthropicClient() # Uses default claude-sonnet-4-6

    results = []
    processed = 0
    
    # We want a mix of eligible and non-eligible if possible, or just the first few
    for topic_id, trial_id, ground_truth in qrels:
        if processed >= limit:
            break
        
        xml_path = os.path.join(trials_dir, f"{trial_id}.xml")
        eligibility_text = extract_eligibility(xml_path)
        
        if not eligibility_text or not topics.get(topic_id):
            continue
            
        log(f"\n--- Evaluating Topic {topic_id} vs Trial {trial_id} ---")
        log(f"Ground Truth Score: {ground_truth}")
        
        llm_output = get_llm_decision(client, topics[topic_id], eligibility_text)
        log(f"LLM Output:\n{llm_output}")
        
        # Parse decision
        score = 0
        for line in llm_output.split('\n'):
            if line.startswith("Score:"):
                try:
                    score = int(line.replace("Score:", "").strip())
                except:
                    score = 0
                break
        
        # Ground truth check
        # Exact match (3 categories)
        is_exact_correct = (score == ground_truth)
        
        # Binary match: 2 is success/relevant, 0 or 1 is not
        gt_relevant = ground_truth > 1
        llm_relevant = score > 1
        is_binary_correct = (gt_relevant == llm_relevant)
        
        results.append({
            'exact': is_exact_correct,
            'binary': is_binary_correct
        })
        
        # Print eligibility section as requested
        log("\n[Eligibility Section from Trial]")
        log(eligibility_text)
        log("-" * 40)
        
        processed += 1

    if results:
        exact_success_rate = sum(r['exact'] for r in results) / len(results)
        binary_success_rate = sum(r['binary'] for r in results) / len(results)
        log(f"\nOverall Exact Success Rate (3 categories): {exact_success_rate:.2%} ({sum(r['exact'] for r in results)}/{len(results)})")
        log(f"Overall Binary Success Rate (Eligible/Not): {binary_success_rate:.2%} ({sum(r['binary'] for r in results)}/{len(results)})")
    else:
        log("No trials were processed.")

    if output_f:
        output_f.close()

if __name__ == "__main__":
    main()
