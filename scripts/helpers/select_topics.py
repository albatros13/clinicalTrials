import os
import xml.etree.ElementTree as ET

# Path configuration
QRELS_FILE = 'data/qrels2021.txt'
TOPICS_FILE = 'data/topics2021.xml'
SELECTED_TRIALS_DIR = 'data/selected_trials'
OUTPUT_TOPICS_FILE = 'data/selected_topics.xml'

def main():
    # 1. Get selected trial IDs
    if not os.path.exists(SELECTED_TRIALS_DIR):
        print(f"Error: {SELECTED_TRIALS_DIR} does not exist. Run select_trials.py first.")
        return

    selected_trial_ids = set()
    for filename in os.listdir(SELECTED_TRIALS_DIR):
        if filename.endswith('.xml'):
            trial_id = filename[:-4]
            selected_trial_ids.add(trial_id)
    
    print(f"Found {len(selected_trial_ids)} selected trials.")

    # 2. Find topic IDs associated with these trials in qrels
    relevant_topic_ids = set()
    if not os.path.exists(QRELS_FILE):
        print(f"Error: {QRELS_FILE} not found.")
        return

    with open(QRELS_FILE, 'r') as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) >= 3:
                topic_id = parts[0]
                trial_id = parts[2]
                if trial_id in selected_trial_ids:
                    relevant_topic_ids.add(topic_id)
    
    print(f"Found {len(relevant_topic_ids)} relevant topic IDs.")

    # 3. Extract topics from topics2021.xml
    if not os.path.exists(TOPICS_FILE):
        print(f"Error: {TOPICS_FILE} not found.")
        return

    tree = ET.parse(TOPICS_FILE)
    root = tree.getroot()
    
    # Create a new root for selected topics
    new_root = ET.Element('topics', root.attrib)
    
    count = 0
    for topic in root.findall('topic'):
        topic_number = topic.get('number')
        if topic_number in relevant_topic_ids:
            new_root.append(topic)
            count += 1
    
    # 4. Save to file
    new_tree = ET.ElementTree(new_root)
    # Using 'utf-8' and xml_declaration=True to maintain a standard XML format
    new_tree.write(OUTPUT_TOPICS_FILE, encoding='utf-8', xml_declaration=True)
    
    print(f"Successfully saved {count} topics to {OUTPUT_TOPICS_FILE}")

if __name__ == "__main__":
    main()
