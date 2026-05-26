import os

def evaluate_precision(file_path):
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return

    total_rows = 0
    exact_matches = 0
    binary_matches = 0

    with open(file_path, 'r') as f:
        for line_num, line in enumerate(f, 1):
            parts = line.strip().split()
            if len(parts) < 5:
                # Skip lines that don't have the LLM decision yet
                continue

            try:
                gold = int(parts[3])
                llm = int(parts[4])
            except (ValueError, IndexError):
                print(f"Warning: Could not parse values at line {line_num}: {line.strip()}")
                continue

            total_rows += 1
            
            # Metric 1: Exact value match
            if gold == llm:
                exact_matches += 1
            
            # Metric 2: Success (2) vs not success (0 or 1)
            # Success is 2, Not Success is 0 or 1.
            gold_success = (gold == 2)
            llm_success = (llm == 2)
            
            if gold_success == llm_success:
                binary_matches += 1

    if total_rows == 0:
        print("No valid rows found for evaluation.")
        return

    exact_match_pct = (exact_matches / total_rows) * 100
    binary_match_pct = (binary_matches / total_rows) * 100

    print(f"Evaluation Results for {file_path}:")
    print(f"Total rows evaluated: {total_rows}")
    print(f"1. Exact value match: {exact_matches}/{total_rows} ({exact_match_pct:.2f}%)")
    print(f"2. Success (2) vs Not Success (0 or 1) match: {binary_matches}/{total_rows} ({binary_match_pct:.2f}%)")

if __name__ == "__main__":
    file_path = 'data/results/openai-anthropic-short/selected_qrels2021.txt'
    evaluate_precision(file_path)
