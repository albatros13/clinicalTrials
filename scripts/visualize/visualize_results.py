import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
import re
import os

def parse_results(file_path):
    with open(file_path, 'r') as f:
        lines = f.readlines()

    results = []
    current_method = None
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Match "Claude extraction, Claude matching" etc.
        if "extraction" in line and "matching" in line:
            current_method = line
        # Match "1. Exact value match: 85/200 (42.50%)"
        elif current_method and "Exact value match" in line:
            match = re.search(r'(\d+\.?\d*)%', line)
            if match:
                percentage = float(match.group(1))
                results.append({
                    'Method': current_method,
                    'Metric': '3-class (Exact)',
                    'Success Rate (%)': percentage,
                    'Type': 'Extraction'
                })
        # Match "2. Success (2) vs Not Success (0 or 1) match: 56/100 (56.00%)"
        elif current_method and "Success (2) vs Not Success" in line:
            match = re.search(r'(\d+\.?\d*)%', line)
            if match:
                percentage = float(match.group(1))
                results.append({
                    'Method': current_method,
                    'Metric': '2-class (Binary)',
                    'Success Rate (%)': percentage,
                    'Type': 'Extraction'
                })
        # Handle the overall success rates at the end (Base methods)
        elif "Success Rate" in line and ":" in line and "(" in line and "extraction" not in line.lower():
            is_binary = "Binary" in line
            match = re.search(r'(?:Binary )?Success Rate (.*?): (\d+\.?\d*)%', line)
            if match:
                model = match.group(1).strip()
                percentage = float(match.group(2))
                results.append({
                    'Method': f"Full {model}",
                    'Metric': '2-class (Binary)' if is_binary else '3-class (Exact)',
                    'Success Rate (%)': percentage,
                    'Type': 'Base'
                })
    
    return pd.DataFrame(results)

def plot_results(df, output_path):
    import numpy as np
    
    # Prepare Data
    base_df = df[df['Type'] == 'Base'].copy()
    ext_df = df[df['Type'] == 'Extraction'].copy()
    
    # Unique methods
    base_methods = sorted(base_df['Method'].unique())
    ext_methods = sorted(ext_df['Method'].unique())
    
    plt.figure(figsize=(14, 6))
    
    # We will plot Base methods first, then Extraction methods
    # For all methods, we have two bars each (Exact and Binary)
    
    all_labels = []
    x_positions = []
    curr_x = 0
    bar_width = 0.35
    
    bars_exact = []
    bars_binary = []
    
    # Plot Base Methods
    for i, method in enumerate(base_methods):
        exact_val = base_df[(base_df['Method'] == method) & (base_df['Metric'] == '3-class (Exact)')]['Success Rate (%)'].values[0]
        binary_val = base_df[(base_df['Method'] == method) & (base_df['Metric'] == '2-class (Binary)')]['Success Rate (%)'].values[0]
        
        b1 = plt.bar(curr_x - bar_width/2, exact_val, width=bar_width, color='#ff9999', label='Full Trial (Exact)' if i == 0 else "")
        b2 = plt.bar(curr_x + bar_width/2, binary_val, width=bar_width, color='#cc0000', label='Full Trial (Binary)' if i == 0 else "")
        
        bars_exact.append(b1)
        bars_binary.append(b2)
        
        all_labels.append(method)
        x_positions.append(curr_x)
        curr_x += 2.0
    
    curr_x += 0.5 # Gap between groups
    
    # Plot Extraction Methods
    for i, method in enumerate(ext_methods):
        exact_val = ext_df[(ext_df['Method'] == method) & (ext_df['Metric'] == '3-class (Exact)')]['Success Rate (%)'].values[0]
        binary_val = ext_df[(ext_df['Method'] == method) & (ext_df['Metric'] == '2-class (Binary)')]['Success Rate (%)'].values[0]
        
        b1 = plt.bar(curr_x - bar_width/2, exact_val, width=bar_width, color='#66b3ff', label='2-Stage Extraction (Exact)' if i == 0 else "")
        b2 = plt.bar(curr_x + bar_width/2, binary_val, width=bar_width, color='#2c7bb6', label='2-Stage Extraction (Binary)' if i == 0 else "")
        
        bars_exact.append(b1)
        bars_binary.append(b2)
        
        all_labels.append(method.replace(', ', '\n'))
        x_positions.append(curr_x)
        curr_x += 2.0
        
    plt.ylabel('Success Rate (%)')
    plt.title('Clinical Trial Matching: Full Trial vs 2-Stage Extraction')
    plt.xticks(x_positions, all_labels, rotation=0, ha='center')
    plt.ylim(0, 105)
    
    # Add values on top
    for bar_group in [bars_exact, bars_binary]:
        for bar in bar_group:
            yval = bar[0].get_height()
            plt.text(bar[0].get_x() + bar[0].get_width()/2, yval + 1, f'{yval}%', ha='center', va='bottom', fontsize=9)
    
    plt.legend(loc='upper left')
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    
    plt.tight_layout()
    plt.savefig(output_path)
    print(f"Plot saved to {output_path}")

if __name__ == "__main__":
    input_file = 'data/results/overview-res.txt'
    output_image = 'data/results/evaluation_plot.png'
    
    if os.path.exists(input_file):
        df_results = parse_results(input_file)
        if not df_results.empty:
            plot_results(df_results, output_image)
        else:
            print("No results found to plot.")
    else:
        print(f"Input file {input_file} not found.")
