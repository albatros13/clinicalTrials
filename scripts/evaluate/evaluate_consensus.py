import os

def load_qrels(file_path):
    data = {}
    with open(file_path, 'r') as f:
        for line in f:
            parts = line.split()
            if len(parts) >= 5:
                # Key: (TopicID, NCTID)
                key = (parts[0], parts[2])
                val = int(parts[4])
                data[key] = val
    return data

def cohen_kappa(y1, y2):
    # Map to classes
    classes = sorted(list(set(y1) | set(y2)))
    n_classes = len(classes)
    label_map = {label: i for i, label in enumerate(classes)}
    
    y1 = [label_map[y] for y in y1]
    y2 = [label_map[y] for y in y2]
    
    n = len(y1)
    if n == 0: return 0.0
    
    # Confusion matrix
    cm = [[0] * n_classes for _ in range(n_classes)]
    for a, b in zip(y1, y2):
        cm[a][b] += 1
    
    observed_agreement = sum(cm[i][i] for i in range(n_classes)) / n
    
    row_sums = [sum(cm[i]) for i in range(n_classes)]
    col_sums = [sum(cm[i][j] for i in range(n_classes)) for j in range(n_classes)]
    
    expected_agreement = 0
    for i in range(n_classes):
        expected_agreement += (row_sums[i] * col_sums[i]) / (n * n)
    
    if expected_agreement == 1:
        return 1.0
    
    return (observed_agreement - expected_agreement) / (1 - expected_agreement)

def evaluate_consensus(data1, data2, label1, label2):
    common_keys = sorted(set(data1.keys()) & set(data2.keys()))
    if not common_keys:
        print(f"No common keys between {label1} and {label2}")
        return

    y1 = [data1[k] for k in common_keys]
    y2 = [data2[k] for k in common_keys]

    agreement = sum(1 for a, b in zip(y1, y2) if a == b)
    n = len(y1)
    acc = agreement / n
    kappa = cohen_kappa(y1, y2)

    print(f"Consensus between {label1} and {label2}:")
    print(f"  Common pairs: {n}")
    print(f"  Exact Agreement: {agreement}/{n} ({acc:.2%})")
    print(f"  Cohen's Kappa: {kappa:.4f}")
    print()

def main():
    base_path = "data/results"
    folders = [
        "openai-openai-short",
        "openai-anthropic-short",
        "anthropic-openai-short",
        "anthropic-anthropic-short"
    ]
    
    results = {}
    for folder in folders:
        path = os.path.join(base_path, folder, "selected_qrels2021.txt")
        if os.path.exists(path):
            results[folder] = load_qrels(path)
        else:
            print(f"Warning: File not found {path}")

    # 1. Consensus on OpenAI Extraction: OpenAI judge vs Anthropic judge
    if "openai-openai-short" in results and "openai-anthropic-short" in results:
        evaluate_consensus(
            results["openai-openai-short"], 
            results["openai-anthropic-short"],
            "OpenAI Judge (on OpenAI extraction)",
            "Anthropic Judge (on OpenAI extraction)"
        )

    # 2. Consensus on Anthropic Extraction: OpenAI judge vs Anthropic judge
    if "anthropic-openai-short" in results and "anthropic-anthropic-short" in results:
        evaluate_consensus(
            results["anthropic-openai-short"], 
            results["anthropic-anthropic-short"],
            "OpenAI Judge (on Anthropic extraction)",
            "Anthropic Judge (on Anthropic extraction)"
        )

    # 4. Consensus on Same judge across extractions
    if "openai-openai-short" in results and "anthropic-openai-short" in results:
        evaluate_consensus(
            results["openai-openai-short"],
            results["anthropic-openai-short"],
            "OpenAI Judge (on OpenAI extraction)",
            "OpenAI Judge (on Anthropic extraction)"
        )
    
    if "openai-anthropic-short" in results and "anthropic-anthropic-short" in results:
        evaluate_consensus(
            results["openai-anthropic-short"],
            results["anthropic-anthropic-short"],
            "Anthropic Judge (on OpenAI extraction)",
            "Anthropic Judge (on Anthropic extraction)"
        )

    # 3. Overall Consensus: All OpenAI judge results vs All Anthropic judge results
    openai_judge_all = {}
    if "openai-openai-short" in results:
        for k, v in results["openai-openai-short"].items():
            openai_judge_all[("O_ext", k[0], k[1])] = v
    if "anthropic-openai-short" in results:
        for k, v in results["anthropic-openai-short"].items():
            openai_judge_all[("A_ext", k[0], k[1])] = v

    anthropic_judge_all = {}
    if "openai-anthropic-short" in results:
        for k, v in results["openai-anthropic-short"].items():
            anthropic_judge_all[("O_ext", k[0], k[1])] = v
    if "anthropic-anthropic-short" in results:
        for k, v in results["anthropic-anthropic-short"].items():
            anthropic_judge_all[("A_ext", k[0], k[1])] = v

    if openai_judge_all and anthropic_judge_all:
        evaluate_consensus(
            openai_judge_all,
            anthropic_judge_all,
            "OpenAI Judge (Total)",
            "Anthropic Judge (Total)"
        )

if __name__ == "__main__":
    main()
