import matplotlib.pyplot as plt
import os
import re

def parse_comparison_file(file_path):
    trial_ids = []
    anthropic_counts = []
    openai_counts = []
    differences = []

    with open(file_path, 'r') as f:
        lines = f.readlines()

    for line in lines:
        # Skip header and separator lines
        if line.startswith('Trial ID') or line.startswith('---') or not line.strip():
            continue
        
        # Stop at the summary statistics
        if line.startswith('Total Trials:'):
            break
        
        parts = [p.strip() for p in line.split('|')]
        if len(parts) == 4:
            trial_ids.append(parts[0])
            anthropic_counts.append(int(parts[1]))
            openai_counts.append(int(parts[2]))
            # The difference might have + or - prefix
            diff_str = parts[3].replace('+', '')
            differences.append(int(diff_str))

    return trial_ids, anthropic_counts, openai_counts, differences

def visualize(anthropic_counts, openai_counts, differences):
    results_dir = 'data/results'
    os.makedirs(results_dir, exist_ok=True)

    # 1. Compact Histogram of Differences
    plt.figure(figsize=(8, 4))
    plt.hist(differences, bins=30, color='skyblue', edgecolor='black', alpha=0.8)
    plt.title('Distribution of Differences (Anthropic - OpenAI)', fontsize=12)
    plt.xlabel('Difference in Count', fontsize=10)
    plt.ylabel('Frequency', fontsize=10)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig(os.path.join(results_dir, 'extraction_differences_hist.png'), dpi=300)
    plt.close()

    # 2. Compact Scatter Plot: Anthropic vs OpenAI
    plt.figure(figsize=(6, 5))
    plt.scatter(openai_counts, anthropic_counts, alpha=0.4, s=20, c='navy')
    
    # Add identity line
    max_val = max(max(anthropic_counts), max(openai_counts))
    plt.plot([0, max_val], [0, max_val], 'r--', linewidth=1, label='Identity (y=x)')
    
    plt.title('Requirement Counts: Anthropic vs OpenAI', fontsize=12)
    plt.xlabel('OpenAI Count', fontsize=10)
    plt.ylabel('Anthropic Count', fontsize=10)
    plt.legend(fontsize=9)
    plt.grid(True, linestyle=':', alpha=0.6)
    plt.tight_layout()
    plt.savefig(os.path.join(results_dir, 'extraction_counts_scatter.png'), dpi=300)
    plt.close()

    print(f"Compact visualizations saved to {results_dir}")

if __name__ == "__main__":
    file_path = 'data/eval/eligibility_criteria_extraction/extraction_counts_comparison.txt'
    if os.path.exists(file_path):
        trial_ids, ant_counts, oa_counts, diffs = parse_comparison_file(file_path)
        visualize(ant_counts, oa_counts, diffs)
    else:
        print(f"File not found: {file_path}")
