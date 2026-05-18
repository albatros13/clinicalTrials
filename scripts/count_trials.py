import json
import os

def count_trials(json_path):
    if not os.path.exists(json_path):
        print(f"File not found: {json_path}")
        return
    
    with open(json_path, 'r') as f:
        data = json.load(f)
    
    if isinstance(data, list):
        count = len(data)
        print(f"Number of trials in {json_path}: {count}")
    else:
        print(f"Expected a list of trials in {json_path}, but got {type(data)}")

if __name__ == "__main__":
    count_trials('data/eval/eligibility_criteria.json')
