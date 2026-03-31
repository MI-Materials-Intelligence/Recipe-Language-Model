# RecipeQA Layer

## Overview

Domain-specific corpora are extracted from robotic recipe reports and converted into semantically structured RecipeQA for model training. 

Key Atomic Skills:
- **Corpus Generation Coordination**: Manages generation workflows for multiple corpus types
- **Optimized Recipe Corpora**: Extracts recipe-performance Q&A pairs from complete experimental records
- **Single-Variable Corpora**: Generates comparative analysis Q&A for single variable effects
- **Database Integration**: Directly reads experimental records from database and updates processing status

## Layer Structure with Atomic Skills

```
RecipeQA/
├── data/
│  
└── src/
    ├── distillation/                   # Knowledge distillation module
    │   └── optimized.py                # Optimized corpus generation
    ├── report_to_qa/                   # Report to Q&A module
    │   └── single_v2_db.py             # Single-variable corpus generation v2
    ├── corpus_coordinator.py           # Corpus coordinator (main entry)
    └── __init__.py
```

## Database Requirements

Requires access to the master experimental records table containing recipe information, performance metrics, synthesis conditions, and other fields.

Configuration Example:
```toml
[database]
host = "localhost"
port = 13330
user = "root"
password = "your_password"
database = "rlm_agent"

[recipeqa]
batch_size = 50
num_thres = 100
```

## Output Data

Outputs optimized recipe corpora, single-variable corpora, and task status tracking data.

## Basic Usage

### Environment Setup

```bash
conda activate rlm_agent
cd seven_layers/RecipeQA
```

### Usage Example

```python
from src.corpus_coordinator import CorpusGenerator

# Initialize corpus generator
generator = CorpusGenerator(workspace_root="path/to/RecipeQA")

# Generate optimized recipe corpus
result = generator.generate_optimized()

# Generate single-variable corpus
result = generator.generate_single()

# Generate all types of corpora simultaneously
result = generator.generate_all()
```

### Asynchronous Generation

```python
import asyncio

async def main():
    generator = CorpusGenerator()
    results = await generator.generate_all_async()
    print(results)

asyncio.run(main())
```

### Convenience Functions

```python
from src.corpus_coordinator import generate_corpora

# Quickly generate specified type of corpus
result = generate_corpora(
    corpora_type="all",  # "optimized", "single", or "all"
    workspace_root="/path/to/RecipeQA"
)
```

### Key Modules for Executing Task

- **corpus_coordinator.py**: Unified corpus generation coordinator
- **distillation/optimized.py**: Optimized recipe corpus generation
- **report_to_qa/single_v2_db.py**: Single-variable corpus generation
