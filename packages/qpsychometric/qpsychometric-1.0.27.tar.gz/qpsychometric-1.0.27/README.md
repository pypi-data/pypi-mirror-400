# The `qpsychometric` Package

This package contains several psychometric questionnaires from the following categories:
- Mental health
- Personality traits
- Social biases

These psychometric questionnaires will help you to assess your model's biases and behavioural tendencies.
Currently contains the following questionnaires: ASI, BIG5, CS, GAD, PHQ, SD3, SOC.

## Environment Setup for Reproducibility

To reproduce the exact results and ensure consistency with the validation studies, we recommend using the provided conda environment file:

```bash
# Create the environment from the yml file
conda env create -f env_qpsychometric.yml

# Activate the environment
conda activate qpsychometric_env
```

**Important:** Different versions of dependencies (especially transformers, torch, sentence-transformers, and pingouin) may produce slightly different results due to implementation changes across versions. Using the provided environment file ensures you have the exact package versions used during development and validation.

## List of questionnaires are available for running
* ASI:
  * asi_questionnaire (all questions of ASI in QMNLI & QMLM format)
* BIG5:
  * big5_questionnaire (all questions of BIG5 in QMNLI & QMLM format)
* GAD:
  * gad_questionnaire (all questions of GAD in QMNLI & QMLM format)
* PHQ:
  * phq_questionnaire (all questions of PHQ in QMNLI & QMLM format)
* CS:
  * compassion_scale_questionnaire (all questions of CS in QMNLI format)
* SD3:
  * sd3_questionnaire (all questions of SD3 in QMNLI format)
* SOC:
  * soc_questionnaire (all questions of SOC in QMNLI & QMLM format)

## Structure of the qpsychometric package:
qpsychometric<br>
|-mental_health<br>
| |-generalized_anxiety_disorder (GAD)<br>
| |-patient_health_questionnaire (PHQ)<br>
| |-sense_of_coherence (SOC)<br>
|-personality_traits<br>
| |-big5 (BIG5)<br>
| |-compassion_scale (Compassion Scale)<br>
| |-sd3 (SD3)<br>
|-social_biases<br>
| |-ambivalent_sexism_inventory (ASI)<br>

## Commands and steps for running a questionnaire:

* How to install the qlatent package:
  ```python
  %pip install qlatent
  ```
* How to import the classes of the questionnaires:
  ```python
  from qlatent.qmnli.qmnli import *
  ```
* How to load an NLI model from huggingface.com into a pipeline a few simple steps:
  ```python
  device = 0 if torch.cuda.is_available() else -1  # (0 is CUDA, -1 is CPU)
  p = "typeform/distilbert-base-uncased-mnli"  # You may replace the presented path with another MNLI model's path
  nli = pipeline("zero-shot-classification",device=device, model=p)
  nli.model_identifier = p
  ```
* How to load a questionnaire:
  ```python
  """
  The format for importing a questionnaire is the following:
   from qpsychometric.<category_with_underscores>.<full_questionnaire_name_with_underscores> import <questionnaire_name>
   Each questionnaire is a Data Frame (df) containing the columns: [category_name, questionnaire_name, questionnaire_task, question].
  For example:
  """
  
  from qpsychometric.mental_health.generalized_anxiety_disorder import gad_questionnaire
  from qpsychometric.personality_traits.compassion_scale import compassion_scale_questionnaire
  from qpsychometric.social_biases.ambivalent_sexism_inventory import asi_questionnaire

  # to view the questionnaire df
  print(gad_questionnaire)
  ```
* How to load category questionnaires:
  ```python
  """
  The format for importing category questionnaires is the following:
   from qpsychometric.<category_with_underscores> import *
   All the questionnaires within the same categoery get stored in the same df.
  For example:
  """
  # Gets stored in `mental_health_questionnaires` as a df.
  from qpsychometric.mental_health import *
  # Gets stored in `personality_traits_questionnaires` as a df.
  from qpsychometric.personality_traits import *
  # Gets stored in `social_biases_questionnaires` as a df.
  from qpsychometric.social_biases import *
  ```
* How to load all categories:
  ```python
  """
  To import all categories you need to do:
  All Data Frames from all categories get stored in the same df.
  """
  # Gets stored in `all_psychometrics` as a df.
  from qpsychometric import *

  ```
* How to filter questionnaires:<br>
  ```python
  """
  To filter specific questionnaires you can use indexing valid values from the columns.
  If you wish to filter 2 or more values from a column, it must be in a nested list: [['value1_to_filter','value2_to_filter','value3_to_filter'...]]
  For example:
  """
  from qpsychometric.mental_health.generalized_anxiety_disorder import gad_questionnaire
  # filter by 'QMLM' task
  filtered_gad_questionnaire = gad_questionnaire['QMLM']

  from qpsychometric.mental_health import *
  # filter 2 questionnaires from the category by 'QMNLI' task.
  filtered_mental_health_questionnaires = mental_health_questionnaires[['GAD7','SOC']]['QMNLI']

  # filter 2 categories by 'QMLM' task.
  from qpsychometric import *
  filtered_all_psychometrics = all_psychometrics[['mental_health','personality_traits']]['QMLM']
  ``` 
* How to get the questionnaires questions:<br>
  ```python
  """
  To get the questions in a list you can use the method `get_questions()`
  Returns a list of questions from the filtered DataFrame.
  The df is grouped by ["questionnaire_name", "questionnaire_task"] so each unique group is a pair of questionnaire with its task.
    - If grouped by multiple tasks, returns a nested list (one list per group).
    - Otherwise, returns a flat list of questions.
  For example:
  """
  from qpsychometric.mental_health.generalized_anxiety_disorder import gad_questionnaire
  filtered_gad_questionnaire = gad_questionnaire['QMLM']
  # 1D list containing the GAD QMLM questions.
  gad_questions_qmlm = filtered_gad_questionnaire.get_questions()

  from qpsychometric.mental_health import *
  # filter 2 questionnaires from the category by 'QMNLI' task.
  filtered_mental_health_questionnaires = mental_health_questionnaires[['GAD7','SOC']]['QMNLI']
  # 2D list where each list contains the QMNLI questions of the questionnaire.
  soc_gad_questions_qmnli = filtered_mental_health_questionnaires.get_questions()

  ``` 
* How to run a question from a questionnaire through an MNLI pipeline:<br>
   This package includes (as it relies on) the package qlatent.<br>
   The qlatent package contains a description that explains how to run QMNLI questions.<br>
   Look at these descriptions for the info you need.<br>
* How to run a questionnaire:
  ```python
  """
  Simply iterate through the questionnaire (as it is a list of questions),
  and apply the code for running a question on each question individually.
  """
  from qpsychometric.social_biases.ambivalent_sexism_inventory import asi_questionnaire
  asi_qmnli = asi_questionnaire['QMNLI'].get_questions()
  for Q in tqdm(asi_qmnli):
    Qs = split_question(Q,
                        index=Q.q_index,
                        scales=[Q.q_scale],
                        softmax=[True],
                        filters={'unfiltered':{},
                                "positiveonly":Q().get_filter_for_postive_keywords()
                                },
                        )
    print(Qs[0]._descriptor['Ordinal'])
    Qs[0].run(mnli)  # you may add .mean_score() or .report() after the run() function.
  ```


# questionnaire_validator.py

A general-purpose validation module for psychometric questionnaires based on the QMNLI framework.

## Overview

This module provides a `QuestionnaireValidator` class that automates the validation process for any QMNLI-based questionnaire. It handles question splitting, model evaluation, linguistic validation, and statistical analysis.

## Class: QuestionnaireValidator

### Initialization Parameters

#### Required Parameters

```python
QuestionnaireValidator(
    questionnaire_name,      # str: Short name (e.g., "CS", "ASI", "GAD7")
    questions,               # list: Question objects from questionnaire
    factors,                 # list: Factor names in the questionnaire
)
```

#### Optional Parameters (with defaults)

```python
    index=["index"],                 # list: Index dimensions
    scales=["frequency"],            # list: Scale dimensions
    result_path,                     # str/Path: Output directory
    mnli_pipelines=None,             # list: MNLI model identifiers (uses 2 default models if None)
    softmax_settings=[True, False],  # list: Softmax configurations
    filters=None,                    # dict: Filter functions (uses default if None)
    device=None,                     # int: GPU device (-1 for CPU, auto-detect if None)
    q_range=[5, 0],                  # list: Question score range
    update=True                      # bool: Re-evaluate existing results
```

### Methods

#### `run_validation(output_filename=None)`
Executes complete validation pipeline:
1. Model evaluation on MNLI pipelines
2. Content validity calculation
3. Cronbach's alpha calculation
4. Factor correlation analysis

Returns dictionary with:
- `results_csv`: Path to results file
- `content_validity`: DataFrame with linguistic metrics
- `cronbach_alpha`: Dict with alpha values
- `correlations`: DataFrame with correlations

#### `run_model_evaluation(output_filename=None)`
Runs questionnaire on configured MNLI models.

Returns: Path to results CSV

#### `calc_content_validity(results_csv, softmax=None, output_filename=None)`
Calculates linguistic acceptability metrics from results.

Returns: DataFrame with semantic_similarity, cola_score, silhouette_score

#### `calc_cronbach_alpha(results_csv, softmax=None, positiveonly=True)`
Calculates internal consistency metrics.

Returns: Dict with:
- `data_df`: DataFrame with mean scores per model and question (pivot table)
- `overall`: Overall Cronbach's alpha for entire questionnaire
- `factors`: Dict of Cronbach's alpha per factor

#### `test_question_affect_on_cronbach_alpha(data_df, specific_factors=None)`
Tests how removing individual questions affects Cronbach's alpha reliability.

Parameters:
- `data_df`: DataFrame from calc_cronbach_alpha results
- `specific_factors`: List of factor names to test, "all" for all factors, or None for analyzing all questions together without grouping by factors

Prints alpha with and without each question to identify problematic items.

#### `get_semantic_similarity(q=None)`
Calculate semantic similarity score for a question or all questions without running full MNLI evaluation.

Parameters:
- `q`: Question object with _descriptor, _context_template, _answer_template, and _keywords_map (optional)
  - If provided: calculates for single question
  - If None: calculates for all raw questions

Returns:
- If q is provided: float (75th percentile semantic similarity score)
- If q is None: DataFrame with question names as index and 'semantic_similarity' column

Use this to quickly evaluate semantic similarity between question permutations and the original question using sentence embeddings.

#### `get_cola_score(q=None)`
Calculate COLA (linguistic acceptability) score for a question or all questions without running full MNLI evaluation.

Parameters:
- `q`: Question object with _context_template, _answer_template, and _keywords_map (optional)
  - If provided: calculates for single question
  - If None: calculates for all raw questions

Returns:
- If q is provided: float (mean COLA score across all permutations)
- If q is None: DataFrame with question names as index and 'cola_score' column

Use this to quickly evaluate grammaticality/linguistic acceptability of question permutations.

#### `calc_correlations(results_csv, softmax=None, positiveonly=True, method='spearman')`
Calculates factor correlations.

Returns: Correlation matrix DataFrame

#### `load_results(csv_path, softmax, positiveonly, value='score', index='model', columns='Q')`
Loads and filters results from CSV into pivot table.

Returns: Pivot table DataFrame

## Output Files

### Directory Structure
```
result_path/
├── {questionnaire_name}_mnli_results.csv
├── linguistic_acceptability.csv
##└── linguistic_acceptabilities.csv (optional)
```

### File Contents

**{questionnaire_name}_mnli_results.csv**
- Main results with columns: questionnair, factor, ordinal, scale, index, filter, softmax, original, Q, context_template, answer_template, dimensions, model, mean_score, cola_score, silhouette_score, semantic_similarity, epoch, train_process, dataset, run, mnli_score, range, score, mlm_epoch, mnli_checkpoint

**linguistic_acceptability.csv**
- Summary metrics per question
- Columns: Q, semantic_similarity, cola_score, silhouette_score

**linguistic_acceptabilities.csv**
- Detailed metrics per question permutation
- Columns: student_id, question_name, original_question, param, question_permutation, cola_score, semantic_similarity, silhouette_score

## Running Example

### Basic Usage (Minimal Configuration)

```python
from qpsychometric.questionnaire_validator import QuestionnaireValidator
from qpsychometric.personality_traits.compassion_scale import compassion_scale_questionnaire

# Load questions
cs_qmnli_df = compassion_scale_questionnaire['QMNLI']
cs_questions = cs_qmnli_df.get_questions()

# Extract factors automatically from question descriptors
cs_factors = list(set([q()._descriptor['Factor'] for q in cs_questions]))

# Create validator (only required parameters)
validator = QuestionnaireValidator(
    questionnaire_name="CS",
    questions=cs_questions,
    factors=cs_factors,
    result_path="results_cs/",
)

# Run validation
results = validator.run_validation()

# Access results
print(f"Results saved to: {results['results_csv']}")
print(f"Cronbach's alpha: {results['cronbach_alpha']}")
print(f"Correlations:\n{results['correlations']}")

# Test individual question impact on Cronbach's alpha
data_df = results['cronbach_alpha']['data_df']
validator.test_question_affect_on_cronbach_alpha(data_df, specific_factors=["Common Humanity"])
```

### With Optional Parameters

```python
# Create validator with custom configuration
validator = QuestionnaireValidator(
    questionnaire_name="CS",
    questions=cs_questions,
    factors=cs_factors,
    result_path="results_cs/",
    index=["index"],
    scales=["frequency"],
    mnli_pipelines=[
        'typeform/distilbert-base-uncased-mnli',
        'typeform/mobilebert-uncased-mnli',
    ],
    device=0,  # Force GPU 0
    update=True
)

results = validator.run_validation()
```

## Internal Processing

### Question Splitting
Each question is split into variants based on:
- Softmax settings (True/False)
- Filter types (unfiltered/positiveonly)
- Dimension combinations (index, scale, index+scale)

Default generates 8 variants per question per filter type.

### Model Evaluation
For each question variant:
1. Run through MNLI pipeline
2. Calculate mean score from model outputs
3. Compute linguistic acceptability metrics
4. Extract question attributes
5. Store results

### Validation Metrics
- **COLA Score**: Linguistic acceptability via DeBERTa-v3 COLA model
- **Semantic Similarity**: Cosine similarity between original and permutations via sentence-transformers
- **Silhouette Score**: Internal consistency via clustering metric
- **Cronbach's Alpha**: Reliability coefficient using pingouin
- **Correlations**: Spearman or Pearson correlations between factors

## Default Configuration

```python
# Default MNLI pipelines - These models' performance were tested on the mnli matched validation dataset.
[
    'typeform/distilbert-base-uncased-mnli',
    'typeform/mobilebert-uncased-mnli',
    'cross-encoder/nli-roberta-base',
    'cross-encoder/nli-deberta-base',
    'cross-encoder/nli-distilroberta-base',
    'cross-encoder/nli-MiniLM2-L6-H768',
    'navteca/bart-large-mnli',
    'digitalepidemiologylab/covid-twitter-bert-v2-mnli',
    'joeddav/bart-large-mnli-yahoo-answers',
    'Narsil/deberta-large-mnli-zero-cls',
    'microsoft/deberta-large-mnli',
    'microsoft/deberta-base-mnli',
    'Alireza1044/albert-base-v2-mnli',
    'yoshitomo-matsubara/bert-large-uncased-mnli',
    'yoshitomo-matsubara/bert-base-uncased-mnli',
    'yoshitomo-matsubara/bert-base-uncased-mnli_from_bert-large-uncased-mnli',
    'valhalla/distilbart-mnli-12-6',
]

# Default filters
{
    'unfiltered': {},
    'positiveonly': lambda q: q.get_filter_for_postive_keywords(scales)
}

# Default models for validation
sentence_embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
cola = pipeline("text-classification", "mrm8488/deberta-v3-small-finetuned-cola")
```

## Dependencies

Required packages:
- torch
- pandas
- numpy
- transformers
- sentence-transformers
- pingouin
- tqdm
- qlatent
- qpsychometric

## GPU Support

The module auto-detects GPU availability. To force CPU or specific GPU:

```python
validator = QuestionnaireValidator(
    ...,
    device=-1  # CPU
    # device=0   # GPU 0
    # device=1   # GPU 1
)
```

## Resume Capability

Set `update=False` to skip already-evaluated question-model combinations:

```python
validator = QuestionnaireValidator(
    ...,
    update=False  # Skip existing evaluations
)
```

## Running Individual Steps

```python
# Initialize
validator = QuestionnaireValidator(...)

# Step 1: Model evaluation only
results_csv = validator.run_model_evaluation()

# Step 2: Content validity only (requires results_csv)
content_validity = validator.calc_content_validity(results_csv)

# Step 3: Cronbach's alpha only
alpha = validator.calc_cronbach_alpha(results_csv)

# Step 3b: Test question impact on alpha (optional)
data_df = alpha['data_df']
validator.test_question_affect_on_cronbach_alpha(data_df)  # Analyze all questions together without grouping
validator.test_question_affect_on_cronbach_alpha(data_df, specific_factors="all")  # Test all factors
validator.test_question_affect_on_cronbach_alpha(data_df, specific_factors=["Factor1", "Factor2"])  # Test specific factors

# Step 4: Correlations only
correlations = validator.calc_correlations(results_csv)
```

## Quick Metric Calculation for Individual Questions

If you want to calculate semantic similarity or COLA scores for specific questions without running the full MNLI evaluation pipeline:

```python
# Initialize validator (models will be loaded)
validator = QuestionnaireValidator(
    questionnaire_name="CS",
    questions=cs_questions,
    factors=cs_factors,
)

# Get quick metrics for a single question
question = cs_questions[0]()  # Get first question instance

# Calculate semantic similarity (75th percentile)
similarity_score = validator.get_semantic_similarity(question)
print(f"Semantic Similarity: {similarity_score}")

# Calculate COLA score (mean across permutations)
cola_score = validator.get_cola_score(question)
print(f"COLA Score: {cola_score}")

# Or calculate for all questions at once
all_semantic_scores = validator.get_semantic_similarity()  # Returns DataFrame
print(all_semantic_scores)

all_cola_scores = validator.get_cola_score()  # Returns DataFrame
print(all_cola_scores)

# Useful for quick validation during question development
```

## Re-evaluating Specific Questions

To re-evaluate just one or a few specific questions and update the results:

```python
# Load all questions
cs_questions = cs_qmnli_df.get_questions()

# Re-evaluate only the first question
validator = QuestionnaireValidator(
    questionnaire_name="CS",
    questions=[cs_questions[0]],  # Single question
    factors=cs_factors,            # Keep all factors
    result_path="results_cs/",
    update=True  # Important: must be True to replace existing results
)

# Run evaluation - will replace results for this question only
results = validator.run_model_evaluation()

# The duplicate removal keeps the latest results
# Other questions in the CSV remain untouched
```


Shield: [![CC BY-SA 4.0][cc-by-sa-shield]][cc-by-sa]

This work is licensed under a
[Creative Commons Attribution-ShareAlike 4.0 International License][cc-by-sa].

[![CC BY-SA 4.0][cc-by-sa-image]][cc-by-sa]

[cc-by-sa]: http://creativecommons.org/licenses/by-sa/4.0/
[cc-by-sa-image]: https://licensebuttons.net/l/by-sa/4.0/88x31.png
[cc-by-sa-shield]: https://img.shields.io/badge/License-CC%20BY--SA%204.0-lightgrey.svg
