# STM (Science Traceability Matrix) Data Extraction Implementation

## Overview

The STM data extraction system automatically extracts structured Science Traceability Matrix data from Jupyter notebooks using markdown bold formatting (`**KEY:**`) to identify content sections. This implementation provides seamless integration with the existing DISRA notebook evaluation workflow.

## Architecture

### Components

- **`STMExtractor`** (`hwo_disra/api/stm_extractor.py`): Core extraction engine
- **`STMData`** (`hwo_disra/Types.py`): Data structure for STM content
- **`DisraNBEvaluator`** (`hwo_disra/api/notebook_eval.py`): STM extraction during evaluation

## STM Data Structure

### Supported Fields

```python
@dataclass
class STMData:
    goal: Optional[str] = None                      # Science goal
    objective: Optional[str] = None                 # Specific objective
    physical_parameters: Optional[str] = None       # Physical parameters
    observations: Optional[str] = None              # Required observations
    instrument_requirements: Optional[str] = None   # Instrument needs
    mission_requirements: Optional[str] = None      # Mission needs
    expected_performance: Optional[str] = None      # Expected performance
```

### Required Fields

Complete STM entries require: `goal`, `objective`, `physical_parameters`, and `observations`.

## Markdown Format

### Key Syntax

STM data is extracted from markdown cells using bolded keys:

```markdown
**GOAL:** How did the seeds of Solar System planets first come together?

**OBJECTIVE:** Discover Kuiper Belt Objects (KBOs) down to sizes that distinguish
between different planetesimal formation scenarios.

**PHYSICAL_PARAMETERS:** KBO size distribution characterized by luminosity
function parameters including broken power law slopes and exponential
taper parameters.

**OBSERVATIONS:** R band imaging survey with depth (R_lim) and sky coverage (Ω)
sufficient to detect enough KBOs to distinguish between luminosity function
models at 99.7% confidence.

Analysis shows required parameters:
- Survey depth: 31.6 mag
- Sky coverage: 0.0033 sq. deg
- Total survey time: 2.0 days
```

### Content Extraction Rules

1. **Key Recognition**: Pattern `**[A-Z_]+:**` followed by content
2. **Content Boundaries**: Text from key until next key or double empty line
3. **Normalization**: Line endings normalized, whitespace trimmed
4. **Static Text Only**: No variable substitution or template processing

### Supported Keys

| Markdown Key                   | STMData Field             | Required |
|--------------------------------|---------------------------|----------|
| `**GOAL:**`                    | `goal`                    | ✓ |
| `**OBJECTIVE:**`               | `objective`               | ✓ |
| `**PHYSICAL_PARAMETERS:**`     | `physical_parameters`     | ✓ |
| `**OBSERVATIONS:**`            | `observations`            | ✓ |
| `**INSTRUMENT_REQUIREMENTS:**` | `instrument_requirements` | |
| `**MISSION_REQUIREMENTS:**`    | `mission_requirements`    | |
| `**EXPECTED_PERFORMANCE:**`    | `expected_performance`    | |
| `**CODE PURPOSE:**`            | `code_purpose`            | |

## API Usage

### Evaluation API

```python
from hwo_disra.api.notebook_eval import DisraNBEvaluator

# Create evaluator
evaluator = DisraNBEvaluator(verbose=True)

# Evaluate notebook (automatically extracts STM data)
results = evaluator.evaluate_notebook('notebook.ipynb')

# Access extracted STM data
stm_data = results.stm_data
print(f"Goal: {stm_data.goal}")
print(f"Complete: {stm_data.is_complete()}")
print(f"Missing: {stm_data.get_missing_fields()}")
```

### Direct Extraction

```python
from hwo_disra.api.stm_extractor import STMExtractor

# Create extractor
extractor = STMExtractor()

# Extract from notebook file
stm_data = extractor.extract_to_stm_data('notebook.ipynb')

# Extract from markdown cell
cell_content = "**GOAL:** Science goal here"
extracted = extractor.extract_from_cell(cell_content)
# Result: {'goal': 'Science goal here'}

# Validate keys in content
unrecognized = extractor.validate_keys(cell_content)
```