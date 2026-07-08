# Clinical Trial Matching Scripts

This directory contains scripts for matching clinical trial eligibility criteria with patient profiles (topics) using Large Language Models (LLMs) and formal policies.

## Matching Approaches

We have implemented two primary approaches for evaluating if a patient is eligible for a clinical trial:

### 1. Basic Matching (Full Criteria)
In this approach, the LLM is provided with the full text of the clinical trial's eligibility criteria and the patient's profile in a single prompt. The LLM is asked to make a direct decision.

- **Pros**: Simple, captures context from the entire criteria block.
- **Cons**: Large prompts, potential for missing specific constraints in long texts, lack of granularity in explanations.
- **Key Scripts**:
  - `evaluate_trials_binary.py`: Basic evaluation of Topic vs Trial using full criteria text.
  - `evaluate_trials_3_categories.py`: Alternative evaluation script with slightly different prompting and output logging.

### 2. Advanced Extraction-based Matching
This is a more granular two-step process that first structures the trial requirements before evaluation.

#### Step A: Extraction
The LLM extracts individual eligibility conditions from the trial's criteria text, categorizing them as "Inclusion" or "Exclusion".
- **Script**: `extract_eligibility.py`
- **Output**: JSON file (e.g., `data/eval/eligibility_criteria.json`) containing a list of discrete statements for each trial.

#### Step B: Separate Evaluation
The LLM evaluates the patient profile against the *extracted* list of conditions.
- **Script**: `evaluate_trials_short.py`
- **Pros**: More focused evaluation, potentially higher accuracy by forcing the LLM to consider individual statements, easier to trace which specific condition was met or violated.
- **Cons**: Two-step process (higher latency/cost), depends on the quality of the initial extraction.

---

## Additional Tools

### Formal Demographic Matching (OPA)
For deterministic criteria like age and gender, we use **Open Policy Agent (OPA)** to ensure 100% accuracy on these specific constraints.
- `generate_opa_files.py`: Generates Rego policies from trial XMLs and patient input JSONs.
- `evaluate_opa-gender-age.py`: Executes OPA to evaluate patients against the generated demographic policies.

### Syntactic Matching
Basic text-similarity matching using TF-IDF.
- Located in `scripts/syntactic/`.
- Useful for initial filtering before applying more expensive LLM-based matching.

### Evaluation & Analytics
- `scripts/benchmark_llms.py`: Benchmarks OpenAI and Anthropic models on value extraction tasks. It compares LLM-extracted values against ground truth spans in `data/synth_dataset_v2.json`.
- `evaluate_consensus.py`: Compares decisions made by different LLMs (e.g., OpenAI vs Anthropic) or different matching methods.
- `compare_extraction_counts.py`: Compares how many individual criteria were extracted by different models.
- `evaluate_precision.py`: Calculates precision metrics against ground truth (qrels).
- `scripts/visualize_extraction_counts.py`: Visualizes the differences in the number of criteria extracted by Anthropic vs OpenAI.
- `scripts/visualize_consensus.py`: Generates visualizations for LLM judge consensus metrics (Exact Agreement and Cohen's Kappa).

## LLM Benchmarking (Value Extraction)

The `scripts/benchmark_llms.py` script evaluates the accuracy of different LLMs in extracting specific data points (entities) from text.

### How it works:
1. **Dataset**: Uses `data/synth_dataset_v2.json`, which contains "Full Text", "Masked Text" (with tags like `{{ORGANIZATION}}`), and "Spans" (ground truth values).
2. **Task**: Instructs LLMs (OpenAI `gpt-4o` and Anthropic `claude-3-5-sonnet-20241022` by default) to fill in the masks by extracting the correct values from the full text.
3. **Evaluation**: Compares the LLM's JSON response against the ground truth values in the dataset's spans.
4. **Output**:
   - Detailed CSV reports: `data/results/value_extraction_openai.csv` and `data/results/value_extraction_anthropic.csv`.
   - Summary statistics: Total matches, mismatches, and overall accuracy percentage printed to console.

### CSV Report Columns:
- `entry_id`: Index of the entry in the dataset.
- `tag`: The entity type (e.g., `NAME`, `DATE`, `US_SSN`).
- `ground_truth`: The correct value from the dataset.
- `llm_response`: The value(s) extracted by the model.
- `is_match`: Boolean indicating if the ground truth was successfully extracted.

## Visualization of Results

The project includes scripts to visualize evaluation results and compare model performance.

### 1. Extraction Counts Visualization
The `scripts/visualize_extraction_counts.py` script compares the number of eligibility criteria extracted by Anthropic and OpenAI models.
- **Input**: `data/eval/eligibility_criteria_extraction/extraction_counts_comparison.txt`
- **Outputs**:
  - `data/results/extraction_differences_hist.png`: Histogram of the differences in extraction counts (Anthropic - OpenAI).
  - `data/results/extraction_counts_scatter.png`: Scatter plot comparing the number of requirements extracted by both models for each trial.

### 2. Consensus Visualization
The `scripts/visualize_consensus.py` script visualizes the agreement between different LLM judges (OpenAI and Anthropic) when evaluating the same extractions.
- **Input**: `data/results/llm_consensus.txt`
- **Output**:
  - `data/results/llm_consensus_visualization_horizontal.png`: A horizontal comparison of Exact Agreement (%) and Cohen's Kappa across different judge/extraction pairs.

## Prompt Documentation

### 1. Straightforward Trial/Patient Match
Used in `evaluate_trials_3_categories.py`. This prompt provides the full eligibility text and asks for a 3-category score.

**Prompt Snippet:**
```text
Evaluate if the patient described below is eligible for the clinical trial based on the provided criteria.

### Patient Profile:
{topic_text}

### Clinical Trial Eligibility Criteria:
{eligibility_text}

### Instructions:
Evaluate the patient's eligibility and provide a score:
- 2: ELIGIBLE. The patient satisfies all inclusion criteria and no exclusion criteria.
- 1: NOT ELIGIBLE. The patient matches one or more exclusion criteria.
- 0: NOT RELEVANT. The topic is irrelevant to this trial's condition at all.

Format:
Score: [0, 1, or 2]
Reason: [Short explanation]
```

### 2. Data Extraction
Used in `extract_eligibility.py`. This prompt breaks down the raw criteria text into discrete, actionable statements.

**Prompt Snippet:**
```text
Extract the individual eligibility conditions from the following clinical trial criteria.
Return the result ONLY as a JSON array of strings.
Each string should represent one condition.
IMPORTANT: Add the prefix "Inclusion: " or "Exclusion: " to each condition.

Criteria Text:
{criteria_text}
```

### 3. Extraction-Based Rule Match (2-Stage)
Used in `evaluate_trials_short.py`. This prompt evaluates the patient against the pre-extracted list of discrete conditions.

**Prompt Snippet:**
```text
Evaluate if the following clinical trial topic satisfies the requirements of the clinical trial based on the criteria provided.

### Topic Description:
{topic_text}

### Clinical Trial Eligibility Criteria:
{criteria_text} (List of extracted strings)

### Instructions:
Answer only with a single integer (2, 1, or 0) followed by a newline and then your justification.
- 2: Yes, the topic satisfies the requirements.
- 1: No, the topic matches exclusion criteria.
- 0: No, the topic is irrelevant.
```

### 4. Value Extraction Benchmark
Used in `scripts/benchmark_llms.py`. This prompt asks the LLM to extract values for specific tags from a given text.

**Prompt Snippet:**
```text
You are an information extraction assistant.
I will provide you with a 'Full Text' and a 'Masked Text' containing tags like {TAG_NAME}.
Your task is to extract the exact values from the 'Full Text' that correspond to each mask in the 'Masked Text'.

Full Text:
{full_text}

Masked Text:
{masked_text}

Return the results as a JSON object where keys are the tag names and values are the extracted strings. 
If a tag appears multiple times, return a list of values in order of appearance.
Only return the JSON object, nothing else.
```

## Data Flow
1. **Raw Data**: Clinical trial XMLs in `data/eval/selected_trials/` and topics in `data/all/topics2021.xml`.
2. **Preprocessing**: (Optional) Run `extract_eligibility.py` to get structured criteria.
3. **Execution**: Run `evaluate_trials.py` (Basic) or `evaluate_trials_short.py` (Advanced). Use `scripts/benchmark_llms.py` for value extraction benchmarking.
4. **Results**: Scores are saved back to qrels files and detailed justifications are recorded in `data/output/evaluation_justifications.csv`. Benchmark results are stored in `data/results/value_extraction_{model}.csv`.
