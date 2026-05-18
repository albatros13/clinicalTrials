import os
import random
import shutil
from collections import defaultdict

# Path configuration
QRELS_FILE = 'data/qrels2021.txt'
DATA_DIR = 'data/ClinicalTrials.2021-04-27.part1'
OUTPUT_DIR = 'data/selected_trials'
OUTPUT_QRELS = 'data/selected_qrels.txt'
TARGET_COUNT = 1000
MIN_PERCENTAGE_2 = 0.3

def main():
    # 1. Analyze qrels2021.txt
    trial_scores = defaultdict(list)
    all_qrel_rows = []
    with open(QRELS_FILE, 'r') as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) >= 4:
                trial_id = parts[2]
                relevance = int(parts[3])
                trial_scores[trial_id].append(relevance)
                all_qrel_rows.append(line)

    # 2. Identify trial IDs with at least 30% of relevance scores equal to 2
    eligible_trial_ids = []
    for trial_id, scores in trial_scores.items():
        count_2 = scores.count(2)
        percentage_2 = count_2 / len(scores)
        if percentage_2 >= MIN_PERCENTAGE_2:
            eligible_trial_ids.append(trial_id)

    print(f"Found {len(eligible_trial_ids)} eligible trial IDs.")

    # 3. Locate files for eligible trial IDs
    found_files = {} # trial_id -> path
    for root, dirs, files in os.walk(DATA_DIR):
        for file in files:
            if file.endswith('.xml'):
                trial_id = file[:-4]
                if trial_id in eligible_trial_ids:
                    found_files[trial_id] = os.path.join(root, file)

    print(f"Found {len(found_files)} matching files in data directory.")

    # 4. Select 1000 files
    selected_ids = list(found_files.keys())
    if len(selected_ids) > TARGET_COUNT:
        selected_ids = random.sample(selected_ids, TARGET_COUNT)
    else:
        print(f"Warning: Only {len(selected_ids)} eligible files found, which is less than {TARGET_COUNT}.")

    # 5. Create output directory and copy files
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        print(f"Created directory: {OUTPUT_DIR}")
    else:
        print(f"Directory {OUTPUT_DIR} already exists.")

    copy_count = 0
    for trial_id in selected_ids:
        src_path = found_files[trial_id]
        dst_path = os.path.join(OUTPUT_DIR, f"{trial_id}.xml")
        shutil.copy2(src_path, dst_path)
        copy_count += 1

    print(f"Successfully copied {copy_count} files to {OUTPUT_DIR}")

    # 6. Store selected qrels rows
    selected_ids_set = set(selected_ids)
    with open(OUTPUT_QRELS, 'w') as f:
        for line in all_qrel_rows:
            parts = line.strip().split()
            if parts[2] in selected_ids_set:
                f.write(line)
    
    print(f"Successfully saved selected qrels to {OUTPUT_QRELS}")

if __name__ == "__main__":
    random.seed(42) # For reproducibility
    main()
