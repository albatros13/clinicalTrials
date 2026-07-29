import os
import xml.etree.ElementTree as ET
from glob import glob
import statistics
import re

def generate_text_histogram(data, bins=10):
    if not data:
        return "No data for histogram."
    
    min_val = min(data)
    max_val = max(data)
    if min_val == max_val:
        return f"{min_val}: {'#' * 20}"
    
    bin_size = (max_val - min_val) / bins
    hist = [0] * bins
    
    for val in data:
        bin_idx = int((val - min_val) / bin_size)
        if bin_idx == bins:
            bin_idx -= 1
        hist[bin_idx] += 1
    
    max_count = max(hist) if hist else 0
    scale = 40 / max_count if max_count > 0 else 1
    
    lines = ["Word Count Histogram:"]
    for i in range(bins):
        start = min_val + i * bin_size
        end = min_val + (i + 1) * bin_size
        bar = "#" * int(hist[i] * scale)
        lines.append(f"{start:8.2f} - {end:8.2f}: {bar} ({hist[i]})")
    return "\n".join(lines)

def compute_stats(directory, output_file=None):
    xml_files = glob(os.path.join(directory, "*.xml"))
    if not xml_files:
        print(f"No XML files found in {directory}")
        return

    words_list = []
    tags_list = []
    distinct_tags_list = []
    nums_list = []
    
    processed_files = 0
    
    number_pattern = re.compile(r'\d+(?:\.\d+)?')

    for file_path in xml_files:
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
            
            file_words = 0
            file_tags = 0
            file_distinct_tags = set()
            file_nums = 0
            
            for elem in root.iter():
                file_tags += 1
                file_distinct_tags.add(elem.tag)
                
                if elem.text:
                    file_words += len(elem.text.split())
                    file_nums += len(number_pattern.findall(elem.text))
                if elem.tail:
                    file_words += len(elem.tail.split())
                    file_nums += len(number_pattern.findall(elem.tail))
            
            words_list.append(file_words)
            tags_list.append(file_tags)
            distinct_tags_list.append(len(file_distinct_tags))
            nums_list.append(file_nums)
            processed_files += 1
            
        except Exception as e:
            print(f"Error parsing {file_path}: {e}")

    if processed_files == 0:
        print("No valid XML files processed.")
        return

    avg_words = statistics.mean(words_list)
    var_words = statistics.variance(words_list) if processed_files > 1 else 0
    std_words = statistics.stdev(words_list) if processed_files > 1 else 0
    med_words = statistics.median(words_list)
    min_words = min(words_list)
    max_words = max(words_list)
    q_words = statistics.quantiles(words_list, n=100) if processed_files > 1 else [med_words]*99
    iqr_words = statistics.quantiles(words_list, n=4)[2] - statistics.quantiles(words_list, n=4)[0] if processed_files > 3 else 0
    p95_words = q_words[94]
    p99_words = q_words[98]
    
    avg_tags = statistics.mean(tags_list)
    var_tags = statistics.variance(tags_list) if processed_files > 1 else 0
    std_tags = statistics.stdev(tags_list) if processed_files > 1 else 0
    med_tags = statistics.median(tags_list)
    min_tags = min(tags_list)
    max_tags = max(tags_list)
    q_tags = statistics.quantiles(tags_list, n=100) if processed_files > 1 else [med_tags]*99
    iqr_tags = statistics.quantiles(tags_list, n=4)[2] - statistics.quantiles(tags_list, n=4)[0] if processed_files > 3 else 0
    p95_tags = q_tags[94]
    p99_tags = q_tags[98]
    
    avg_distinct_tags = statistics.mean(distinct_tags_list)
    var_distinct_tags = statistics.variance(distinct_tags_list) if processed_files > 1 else 0
    std_distinct_tags = statistics.stdev(distinct_tags_list) if processed_files > 1 else 0
    med_distinct_tags = statistics.median(distinct_tags_list)
    min_distinct_tags = min(distinct_tags_list)
    max_distinct_tags = max(distinct_tags_list)
    q_distinct_tags = statistics.quantiles(distinct_tags_list, n=100) if processed_files > 1 else [med_distinct_tags]*99
    iqr_distinct_tags = statistics.quantiles(distinct_tags_list, n=4)[2] - statistics.quantiles(distinct_tags_list, n=4)[0] if processed_files > 3 else 0
    p95_distinct_tags = q_distinct_tags[94]
    p99_distinct_tags = q_distinct_tags[98]
    
    avg_nums = statistics.mean(nums_list)
    var_nums = statistics.variance(nums_list) if processed_files > 1 else 0
    std_nums = statistics.stdev(nums_list) if processed_files > 1 else 0
    med_nums = statistics.median(nums_list)
    min_nums = min(nums_list)
    max_nums = max(nums_list)
    q_nums = statistics.quantiles(nums_list, n=100) if processed_files > 1 else [med_nums]*99
    iqr_nums = statistics.quantiles(nums_list, n=4)[2] - statistics.quantiles(nums_list, n=4)[0] if processed_files > 3 else 0
    p95_nums = q_nums[94]
    p99_nums = q_nums[98]

    results = [
        f"Processed {processed_files} files.",
        f"Words: Mean={avg_words:.2f}, Var={var_words:.2f}, Std={std_words:.2f}, Median={med_words:.2f}, Min={min_words}, Max={max_words}, IQR={iqr_words:.2f}, 95th={p95_words:.2f}, 99th={p99_words:.2f}",
        f"Numeric Measurements: Mean={avg_nums:.2f}, Var={var_nums:.2f}, Std={std_nums:.2f}, Median={med_nums:.2f}, Min={min_nums}, Max={max_nums}, IQR={iqr_nums:.2f}, 95th={p95_nums:.2f}, 99th={p99_nums:.2f}",
        f"XML Tags: Mean={avg_tags:.2f}, Var={var_tags:.2f}, Std={std_tags:.2f}, Median={med_tags:.2f}, Min={min_tags}, Max={max_tags}, IQR={iqr_tags:.2f}, 95th={p95_tags:.2f}, 99th={p99_tags:.2f}",
        f"Distinct XML Tags: Mean={avg_distinct_tags:.2f}, Var={var_distinct_tags:.2f}, Std={std_distinct_tags:.2f}, Median={med_distinct_tags:.2f}, Min={min_distinct_tags}, Max={max_distinct_tags}, IQR={iqr_distinct_tags:.2f}, 95th={p95_distinct_tags:.2f}, 99th={p99_distinct_tags:.2f}",
        "",
        generate_text_histogram(words_list)
    ]

    for line in results:
        print(line)

    if output_file:
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, 'w') as f:
            for line in results:
                f.write(line + '\n')
        print(f"Results saved to {output_file}")

if __name__ == "__main__":
    target_dir = "data/eval/selected_trials"
    output_path = "data/results/trial_stats.txt"
    compute_stats(target_dir, output_path)
