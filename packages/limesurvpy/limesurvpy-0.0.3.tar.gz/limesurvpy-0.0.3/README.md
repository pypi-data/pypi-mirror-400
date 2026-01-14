# limesurvpy

A Python package to support evaluating LimeSurvey questionnaires. The package provides support for various types of questions (e.g., lists, multiple choice questions, rankings, matrix questions, text questions, etc.). For supported question types, the tool compiles dataframes of responses, and generates a number of pre-defined plots to support interpretation. For multi-lingual surveys, the tool supports presenting information in a specific locale.

## Features

- **Import LimeSurvey structure files** (.lss format)
- **Import response data** from CSV files
- **Describe** responses using appropriate visualizations
- **Multi-language support** to show responses in any locale included in the questionnaire
- **Export** of processed data to Excel and CSV formats
- **Automatic translation** of text to user-defined language

## Installation

```bash
pip install limesurvpy
```

## Quick Start

### 1. Import and Create Survey Object

```python
from limesurvpy import Survey

# Create survey from LimeSurvey structure file
my_survey = Survey.from_lss(structure_filename='path/to/survey.lss')

# Get basic information about the survey
my_survey.summary()
my_survey.list_questions()
```

### 2. Import responses

```python
# Import responses from CSV file
# Note: Export responses from Limesurvey with question codes and response codes (not labels)
my_survey.import_responses('path/to/responses.csv', sep=',')
```

### 3. Analyze Questions

```python
# Get question details
my_survey.print_details(question_code='Q001', include_attributes=True)

# Compile responses and automatically plot results for convenience
responses = my_survey.describe(question_code='Q001')
```

### 4. Export Results

```python
# Export single question responses
Survey.export(responses, target='xlsx', excel_filename='results.xlsx')

# batch-export: If questions is None, export all
my_survey.export_questions(questions=None, target='xlsx', path=export_path, index=False)

```

## Multi-language Support

Compiled dataframes and plots will include labels for responses for the specified language. Text items are translated into the specified language using *deep-translator*.

```python
# Specify language for labels and responses
responses = my_survey.describe(question_code='Q001', lang='vi')  
```

