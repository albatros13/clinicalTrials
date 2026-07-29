import json
import re
import statistics

def collect_stats(file_path):
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error reading JSON file: {e}")
        return

    num_entries = len(data)
    if num_entries == 0:
        print("Dataset is empty.")
        return

    full_text_lengths = []
    span_counts = []
    masked_tags = set()
    
    # Regex to find tags like {{TAG_NAME}}
    tag_pattern = re.compile(r'\{\{([A-Z_]+)\}\}')

    for entry in data:
        # Length of full_text
        text = entry.get('full_text', '')
        full_text_lengths.append(len(text))
        
        # Number of spans
        spans = entry.get('spans', [])
        span_counts.append(len(spans))
        
        # Unique masked tags
        masked_text = entry.get('masked', '')
        tags = tag_pattern.findall(masked_text)
        for tag in tags:
            masked_tags.add(tag)

    print(f"Number of entries: {num_entries}")
    
    if full_text_lengths:
        print(f"--- Full Text Length ---")
        print(f"Mean:   {statistics.mean(full_text_lengths):.2f}")
        print(f"Median: {statistics.median(full_text_lengths):.2f}")
        print(f"Max:    {max(full_text_lengths)}")
        print(f"Min:    {min(full_text_lengths)}")
    
    if span_counts:
        print(f"--- Number of Spans ---")
        print(f"Total:  {sum(span_counts)}")
        print(f"Mean:   {statistics.mean(span_counts):.2f}")
        print(f"Median: {statistics.median(span_counts):.2f}")
        print(f"Max:    {max(span_counts)}")
        print(f"Min:    {min(span_counts)}")

    print(f"--- Masked Tags ---")
    print(f"Number of unique masked tags: {len(masked_tags)}")
    print(f"Tags: {sorted(list(masked_tags))}")

if __name__ == "__main__":
    collect_stats('data/synth_dataset_v2.json')
