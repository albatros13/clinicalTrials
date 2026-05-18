import os

def filter_qrels():
    selected_trials_dir = 'data/eval/selected_trials'
    qrels_path = 'data/qrels2021.txt'
    output_path = 'data/selected_qrels2021.txt'

    # Get list of trial IDs from filenames (remove .xml extension)
    selected_ids = set()
    if os.path.exists(selected_trials_dir):
        for filename in os.listdir(selected_trials_dir):
            if filename.endswith('.xml'):
                trial_id = filename[:-4]
                selected_ids.add(trial_id)
    else:
        print(f"Directory {selected_trials_dir} not found.")
        return

    print(f"Found {len(selected_ids)} selected trials.")

    # Filter qrels file
    count = 0
    with open(qrels_path, 'r') as f_in, open(output_path, 'w') as f_out:
        for line in f_in:
            parts = line.strip().split()
            if len(parts) >= 3:
                trial_id = parts[2]
                if trial_id in selected_ids:
                    f_out.write(line)
                    count += 1
    
    print(f"Filtered {count} rows. Saved to {output_path}")

if __name__ == "__main__":
    filter_qrels()
