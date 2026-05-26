import json
import os

def load_json(filepath):
    if not os.path.exists(filepath):
        print(f"Error: {filepath} not found.")
        return None
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def get_counts(data):
    return {item['id']: len(item['criteria']) for item in data}

def main():
    anthropic_path = 'data/eval/eligibility_criteria_extraction/eligibility_criteria-anthropic.json'
    openai_path = 'data/eval/eligibility_criteria_extraction/eligibility_criteria-openai.json'
    output_path = 'data/eval/eligibility_criteria_extraction/extraction_counts_comparison.txt'

    anthropic_data = load_json(anthropic_path)
    openai_data = load_json(openai_path)

    if anthropic_data is None or openai_data is None:
        return

    anthropic_counts = get_counts(anthropic_data)
    openai_counts = get_counts(openai_data)

    common_ids = set(anthropic_counts.keys()).intersection(set(openai_counts.keys()))
    common_ids = sorted(list(common_ids))

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        header = f"{'Trial ID':<15} | {'Anthropic':<10} | {'OpenAI':<10} | {'Difference':<10}"
        print(header)
        f.write(header + "\n")
        
        separator = "-" * 55
        print(separator)
        f.write(separator + "\n")

        diffs = []
        total_anthropic = 0
        total_openai = 0

        for tid in common_ids:
            a_count = anthropic_counts[tid]
            o_count = openai_counts[tid]
            diff = a_count - o_count
            diffs.append(diff)
            total_anthropic += a_count
            total_openai += o_count
            line = f"{tid:<15} | {a_count:<10} | {o_count:<10} | {diff:<+10}"
            print(line)
            f.write(line + "\n")

        print(separator)
        f.write(separator + "\n")
        
        summary = []
        summary.append(f"Total Trials: {len(common_ids)}")
        if common_ids:
            summary.append(f"Avg Anthropic: {total_anthropic / len(common_ids):.2f}")
            summary.append(f"Avg OpenAI:    {total_openai / len(common_ids):.2f}")
            summary.append(f"Avg Diff:      {sum(diffs) / len(common_ids):.2f}")
        
        for s_line in summary:
            print(s_line)
            f.write(s_line + "\n")

    print(f"\nResults saved to {output_path}")

if __name__ == "__main__":
    main()
