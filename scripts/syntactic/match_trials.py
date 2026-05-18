import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

def match_topics_to_trials(topics_csv, trials_csv, output_csv):
    print("Loading data...")
    df_topics = pd.read_csv(topics_csv)
    df_trials = pd.read_csv(trials_csv)
    
    # Ensure no NaN values in text fields
    df_topics['description'] = df_topics['description'].fillna('')
    df_trials['text'] = df_trials['text'].fillna('')
    
    print("Vectorizing text...")
    vectorizer = TfidfVectorizer(stop_words='english', max_features=10000)
    
    # Combine all text to build vocabulary
    all_text = pd.concat([df_topics['description'], df_trials['text']])
    vectorizer.fit(all_text)
    
    topic_vectors = vectorizer.transform(df_topics['description'])
    trial_vectors = vectorizer.transform(df_trials['text'])
    
    print("Calculating similarities...")
    similarities = cosine_similarity(topic_vectors, trial_vectors)
    
    results = []
    for i, topic_id in enumerate(df_topics['topic_id']):
        # Get top 10 matches for each topic
        top_indices = np.argsort(similarities[i])[::-1][:10]
        for idx in top_indices:
            results.append({
                'topic_id': topic_id,
                'nct_id': df_trials.iloc[idx]['nct_id'],
                'score': similarities[i][idx]
            })
            
    df_results = pd.DataFrame(results)
    df_results.to_csv(output_csv, index=False)
    print(f"Matching complete. Results saved to {output_csv}")

if __name__ == "__main__":
    match_topics_to_trials("./output/processed_topics.csv", "./output/processed_trials_sample.csv", "./output/match_results.csv")
