import pandas as pd

def evaluate_matches(qrels_file, match_results_csv):
    print(f"Evaluating {match_results_csv} against {qrels_file}...")
    
    # Load qrels: topic_id 0 nct_id relevance
    qrels = []
    with open(qrels_file, 'r') as f:
        for line in f:
            parts = line.split()
            if len(parts) >= 4:
                qrels.append({
                    'topic_id': int(parts[0]),
                    'nct_id': parts[2],
                    'relevance': int(parts[3])
                })
    df_qrels = pd.DataFrame(qrels)
    
    # Load match results
    df_matches = pd.read_csv(match_results_csv)
    
    # Merge to see if our matches are in qrels
    # Note: topic_id in match_results might be string or int, let's normalize
    df_matches['topic_id'] = df_matches['topic_id'].astype(int)
    
    merged = pd.merge(df_matches, df_qrels, on=['topic_id', 'nct_id'], how='left')
    merged['relevance'] = merged['relevance'].fillna(-1) # -1 means not in qrels for that topic
    
    # Calculate some stats
    found_relevant = merged[merged['relevance'] > 0]
    total_matches = len(df_matches)
    
    print(f"Total matches analyzed: {total_matches}")
    print(f"Matches found in qrels with relevance > 0: {len(found_relevant)}")
    
    if len(found_relevant) > 0:
        print("\nSample of successful matches:")
        print(found_relevant[['topic_id', 'nct_id', 'score', 'relevance']].head(10))
    else:
        print("\nNo relevant matches found in the sample. This is expected if the sample of 2000 trials doesn't overlap much with the qrels.")
        # Let's see how many matches are at least IN the qrels (even if relevance 0)
        found_in_qrels = merged[merged['relevance'] >= 0]
        print(f"Matches found in qrels (any relevance): {len(found_in_qrels)}")

if __name__ == "__main__":
    import os
    # Default to qrels2021.txt, but could be parameterizable
    qrels_file = "./data/qrels2021.txt"
    match_results = "./output/match_results.csv"
    
    if os.path.exists(qrels_file):
        if os.path.exists(match_results):
            evaluate_matches(qrels_file, match_results)
        else:
            print(f"Match results file {match_results} not found. Run match_trials.py first.")
    else:
        print(f"Qrels file {qrels_file} not found.")
