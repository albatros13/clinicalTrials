import zipfile
import xml.etree.ElementTree as ET
import pandas as pd
import os
import io

def extract_trial_info(xml_content):
    try:
        root = ET.fromstring(xml_content)
        nct_id = root.find('.//nct_id').text if root.find('.//nct_id') is not None else "Unknown"
        title = root.find('.//brief_title').text if root.find('.//brief_title') is not None else ""
        summary = root.find('.//brief_summary/textblock').text if root.find('.//brief_summary/textblock') is not None else ""
        detailed = root.find('.//detailed_description/textblock').text if root.find('.//detailed_description/textblock') is not None else ""
        
        # Eligibility criteria can be very important
        eligibility = root.find('.//eligibility/criteria/textblock').text if root.find('.//eligibility/criteria/textblock') is not None else ""
        
        full_text = f"{title} {summary} {detailed} {eligibility}".strip()
        return {'nct_id': nct_id, 'text': full_text}
    except Exception as e:
        return None

def process_zips(data_dir, output_file, limit_per_zip=1000):
    all_trials = []
    zip_files = [f for f in os.listdir(data_dir) if f.endswith('.zip') and 'ClinicalTrials' in f]
    
    for zip_name in zip_files:
        zip_path = os.path.join(data_dir, zip_name)
        print(f"Processing {zip_name}...")
        with zipfile.ZipFile(zip_path, 'r') as z:
            count = 0
            for file_info in z.infolist():
                if file_info.filename.endswith('.xml'):
                    with z.open(file_info) as f:
                        trial_data = extract_trial_info(f.read())
                        if trial_data:
                            all_trials.append(trial_data)
                            count += 1
                    if limit_per_zip and count >= limit_per_zip:
                        break
            print(f"Extracted {count} trials from {zip_name}")
            
    if all_trials:
        df = pd.DataFrame(all_trials)
        df.to_csv(output_file, index=False)
        print(f"Saved {len(df)} trials to {output_file}")

if __name__ == "__main__":
    # We might want to filter trials that are actually in qrels to save space/time during vibe-coding
    # But for now, let's just take a sample from each zip.
    process_zips("../data", "../output/processed_trials_sample.csv", limit_per_zip=500)
