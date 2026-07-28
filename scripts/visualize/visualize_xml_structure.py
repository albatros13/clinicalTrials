import pandas as pd
import matplotlib.pyplot as plt
import os

def visualize_xml_structure(csv_path, output_path):
    # Load the CSV
    df = pd.read_csv(csv_path)
    
    # Remove '%' and convert Percentage to float
    df['Percentage'] = df['Percentage'].str.rstrip('%').astype('float')
    
    # Sort by percentage and total occurrences
    # We want to see which sections are most common
    df_sorted = df.sort_values(by=['Percentage', 'Total occurrences'], ascending=False)
    
    # Take top 25 most common tags
    top_n = 220
    df_plot = df_sorted.head(top_n).iloc[::-1] # Reverse for horizontal bar chart
    
    plt.figure(figsize=(12, 40))
    
    # Create horizontal bar chart
    bars = plt.barh(df_plot['Tag'], df_plot['Percentage'], color='lightseagreen', alpha=0.8)
    
    # Add percentage labels on the bars
    for bar in bars:
        width = bar.get_width()
        plt.text(width + 1, bar.get_y() + bar.get_height()/2, 
                 f'{width:.1f}%', 
                 va='center', fontsize=9)

    plt.xlabel('Percentage of Files Included (%)', fontsize=12)
    plt.ylabel('XML Tag (Section)', fontsize=12)
    plt.title(f'Top {top_n} Most Common Sections in Clinical Trial Descriptions', fontsize=14)
    plt.xlim(0, 110) # Leave space for labels
    plt.grid(axis='x', linestyle='--', alpha=0.6)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()
    
    print(f"Visualization saved to {output_path}")

if __name__ == "__main__":
    input_file = 'data/output/helpers/xml_structure_analysis.csv'
    output_dir = 'data/results/images'
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, 'xml_structure_analysis.png')
    
    if os.path.exists(input_file):
        visualize_xml_structure(input_file, output_file)
    else:
        print(f"Error: Input file {input_file} not found.")
