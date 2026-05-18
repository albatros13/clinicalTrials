import os
import xml.etree.ElementTree as ET
import csv
from collections import Counter

def analyze_xml_structure():
    trials_dir = 'data/eval/selected_trials'
    
    unique_tags_per_file = Counter()
    total_tags_count = Counter()
    total_files = 0
    
    if not os.path.exists(trials_dir):
        print(f"Directory {trials_dir} not found.")
        return

    xml_files = [f for f in os.listdir(trials_dir) if f.endswith('.xml')]
    total_files = len(xml_files)
    
    for filename in xml_files:
        file_path = os.path.join(trials_dir, filename)
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
            
            file_tags = set()
            
            for elem in root.iter():
                tag = elem.tag
                # Flatten semantically irrelevant tags like <textblock>
                if tag == 'textblock':
                    continue
                
                file_tags.add(tag)
                total_tags_count[tag] += 1
            
            for tag in file_tags:
                unique_tags_per_file[tag] += 1
                
        except Exception as e:
            print(f"Error parsing {filename}: {e}")

    output_file = 'data/xml_structure_analysis.csv'
    
    # Sort tags by percentage occurrence (unique_tags_per_file) descending
    sorted_tags = sorted(unique_tags_per_file.items(), key=lambda x: x[1], reverse=True)

    with open(output_file, 'w', newline='') as csvfile:
        fieldnames = ['Tag', 'Files included', 'Percentage', 'Total occurrences']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for tag, file_count in sorted_tags:
            file_percentage = (file_count / total_files) * 100
            total_count = total_tags_count[tag]
            writer.writerow({
                'Tag': tag,
                'Files included': file_count,
                'Percentage': f"{file_percentage:.1f}%",
                'Total occurrences': total_count
            })

    print(f"\nAnalysis complete. Processed {total_files} files.")
    print(f"Results saved to {output_file}")

if __name__ == "__main__":
    analyze_xml_structure()
