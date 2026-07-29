import xml.etree.ElementTree as ET
import re
import math
import statistics

def calculate_stats(file_path):
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()
    except Exception as e:
        print(f"Error parsing XML: {e}")
        return

    topics = root.findall('topic')
    if not topics:
        print("No topics found in the XML.")
        return

    word_counts = []
    num_counts = []

    # Regex for numbers: integers, decimals
    number_pattern = re.compile(r'\d+(?:\.\d+)?')

    for topic in topics:
        text = topic.text.strip() if topic.text else ""
        
        # Word count
        words = text.split()
        word_counts.append(len(words))
        
        # Count numbers
        numbers = number_pattern.findall(text)
        num_counts.append(len(numbers))

    def print_metrics(name, data):
        if not data:
            print(f"No data for {name}")
            return
        
        mean = statistics.mean(data)
        median = statistics.median(data)
        stdev = statistics.stdev(data) if len(data) > 1 else 0
        minimum = min(data)
        maximum = max(data)
        
        print(f"--- {name} ---")
        print(f"Mean:   {mean:.2f}")
        print(f"Median: {median:.2f}")
        print(f"Stdev:  {stdev:.2f}")
        print(f"Min:    {minimum}")
        print(f"Max:    {maximum}")
        print()

    print(f"Total topics: {len(topics)}\n")
    print_metrics("Word Counts", word_counts)
    print_metrics("Numeric Measurements", num_counts)

if __name__ == "__main__":
    calculate_stats('data/eval/topics2021.xml')
