import xml.etree.ElementTree as ET
import pandas as pd
import os

def parse_topics(file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()
    topics = []
    for topic in root.findall('topic'):
        number = topic.get('number')
        text = topic.text.strip() if topic.text else ""
        topics.append({'topic_id': number, 'description': text})
    return pd.DataFrame(topics)

if __name__ == "__main__":
    data_dir = "../data"
    all_topics = []
    for year in ['2021', '2022']: # 2023 might have different format but let's stick to these for now
        file_path = os.path.join(data_dir, f"topics{year}.xml")
        if os.path.exists(file_path):
            print(f"Parsing {file_path}...")
            df = parse_topics(file_path)
            df['year'] = year
            all_topics.append(df)
    
    if all_topics:
        combined_df = pd.concat(all_topics, ignore_index=True)
        combined_df.to_csv("processed_topics.csv", index=False)
        print(f"Saved {len(combined_df)} topics to processed_topics.csv")
    else:
        print("No topic files found.")
