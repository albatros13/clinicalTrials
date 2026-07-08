import os
import subprocess
import json
import glob

# Paths
POLICIES_DIR = 'data/output/policies'
INPUTS_DIR = 'data/output/policy_inputs'

def evaluate_opa():
    input_files = glob.glob(os.path.join(INPUTS_DIR, '*.json'))
    results = []

    print(f"Found {len(input_files)} input files for evaluation.\n")

    for input_path in sorted(input_files):
        filename = os.path.basename(input_path)
        # Expected format: topic_{topic_id}_trial_{trial_id}.json
        # Extract trial_id
        try:
            parts = filename.replace('.json', '').split('_')
            topic_id = parts[1]
            trial_id = parts[3]
        except (IndexError, ValueError):
            print(f"Skipping {filename}: unexpected filename format.")
            continue

        policy_path = os.path.join(POLICIES_DIR, f"trial_{trial_id}.rego")
        
        if not os.path.exists(policy_path):
            print(f"Warning: Policy file {policy_path} not found for {filename}.")
            continue

        # Run opa eval
        # Query: data.clinical_trial_{trial_id}.allow
        query = f"data.clinical_trial_{trial_id}.allow"
        
        cmd = [
            "opa", "eval",
            "-d", policy_path,
            "-i", input_path,
            query
        ]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            output = json.loads(result.stdout)
            
            allow = False
            if 'result' in output and len(output['result']) > 0:
                allow = output['result'][0]['expressions'][0]['value']
            
            print(f"Topic: {topic_id}, Trial: {trial_id} -> allow: {allow}")
            results.append({
                "topic_id": topic_id,
                "trial_id": trial_id,
                "allow": allow
            })
        except subprocess.CalledProcessError as e:
            print(f"Error evaluating {filename}: {e.stderr}")
        except Exception as e:
            print(f"An unexpected error occurred for {filename}: {e}")

    # Optionally save results to a file
    output_results_path = 'data/results/opa_evaluation_results.json'
    os.makedirs(os.path.dirname(output_results_path), exist_ok=True)
    with open(output_results_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nEvaluation complete. Results saved to {output_results_path}")

if __name__ == "__main__":
    evaluate_opa()
