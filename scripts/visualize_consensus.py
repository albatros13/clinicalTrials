import matplotlib.pyplot as plt
import os
import re

def parse_consensus_file(file_path):
    comparisons = []
    agreements = []
    kappas = []

    with open(file_path, 'r') as f:
        content = f.read()

    # Split by blocks (Consensus between ...)
    blocks = re.split(r'\n(?=Consensus between|onsensus between)', content)
    
    for block in blocks:
        if not block.strip():
            continue
            
        # Extract title
        title_match = re.search(r'(?:Consensus|onsensus) between (.*?):', block)
        if title_match:
            title = title_match.group(1)
            # Shorten title for display
            title = title.replace(' Judge', '').replace(' extraction', '')
            comparisons.append(title)
            
            # Extract Exact Agreement percentage
            agree_match = re.search(r'Exact Agreement: \d+/\d+ \((\d+\.\d+)%\)', block)
            if agree_match:
                agreements.append(float(agree_match.group(1)))
            
            # Extract Cohen's Kappa
            kappa_match = re.search(r"Cohen's Kappa: (\d+\.\d+)", block)
            if kappa_match:
                kappas.append(float(kappa_match.group(1)))

    return comparisons, agreements, kappas

def visualize(comparisons, agreements, kappas):
    results_dir = 'data/results'
    os.makedirs(results_dir, exist_ok=True)

    # Use a horizontal layout: 1 row, 2 columns
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

    # 1. Exact Agreement Bar Chart
    y_pos = range(len(comparisons))
    ax1.barh(y_pos, agreements, color='seagreen', alpha=0.8)
    ax1.set_yticks(y_pos)
    ax1.set_yticklabels(comparisons, fontsize=9)
    ax1.set_xlabel('Exact Agreement (%)', fontsize=10)
    ax1.set_title('Exact Agreement', fontsize=12)
    ax1.set_xlim(0, 100)
    ax1.grid(axis='x', linestyle='--', alpha=0.7)

    # 2. Cohen's Kappa Bar Chart
    ax2.barh(y_pos, kappas, color='royalblue', alpha=0.8)
    ax2.set_yticks(y_pos)
    ax2.set_yticklabels([], fontsize=9) # Hide labels on second plot to save space
    ax2.set_xlabel("Cohen's Kappa", fontsize=10)
    ax2.set_title("Cohen's Kappa", fontsize=12)
    ax2.set_xlim(0, 1.0)
    ax2.grid(axis='x', linestyle='--', alpha=0.7)

    plt.suptitle('LLM Judge Consensus Metrics', fontsize=14, y=1.02)
    plt.tight_layout()
    plt.savefig(os.path.join(results_dir, 'llm_consensus_visualization_horizontal.png'), dpi=300, bbox_inches='tight')
    plt.close()

    print(f"Horizontal consensus visualization saved to {results_dir}")

if __name__ == "__main__":
    file_path = 'data/results/llm_consensus.txt'
    if os.path.exists(file_path):
        comparisons, agreements, kappas = parse_consensus_file(file_path)
        if comparisons:
            visualize(comparisons, agreements, kappas)
        else:
            print("No consensus data found in file.")
    else:
        print(f"File not found: {file_path}")
