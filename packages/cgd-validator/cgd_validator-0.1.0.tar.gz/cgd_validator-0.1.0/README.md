# cgd-validator

Validator for Clarity-Gated Document (`.cgd`) files — documents verified and annotated for safe LLM ingestion.

[![PyPI version](https://badge.fury.io/py/cgd-validator.svg)](https://pypi.org/project/cgd-validator/)
[![License: CC BY 4.0](https://img.shields.io/badge/License-CC_BY_4.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)

## What is a .cgd file?

A **Clarity-Gated Document** (`.cgd`) file is a markdown document that has passed epistemic verification and contains inline annotations ensuring safe interpretation by LLMs.

Part of the [Clarity Gate](https://github.com/frmoretto/clarity-gate) ecosystem for epistemic quality verification.

## Installation

```bash
pip install cgd-validator
```

## CLI Usage

```bash
# Validate a single file
cgd-validator document.cgd

# Validate multiple files
cgd-validator docs/*.cgd

# Output as JSON
cgd-validator document.cgd --json

# Quiet mode (errors only)
cgd-validator document.cgd -q
```

## Python API

```python
from cgd_validator import validate, is_valid, detect, validate_file

# Full validation with errors and warnings
result = validate(file_content)
print(result.valid)       # bool
print(result.errors)      # list of ValidationError
print(result.warnings)    # list of ValidationError
print(result.frontmatter) # parsed YAML frontmatter dict

# Quick check
if is_valid(file_content):
    print('Document passes validation')

# Detect if content is .cgd format
if detect(file_content):
    print('This appears to be a .cgd file')

# Validate from file path
result = validate_file('document.cgd')
```

## Validation Rules

### Required Elements
- YAML frontmatter with:
  - `clarity-gate-version`
  - `verified-date`
  - `verified-by`
  - `hitl-status`
- `## Clarity Gate Verification` section

### Warnings
- HITL status not "CONFIRMED"
- Projections ("will be") without `*(projected)*` marker
- Vague quantifiers without annotation

## Related

- [Clarity Gate](https://github.com/frmoretto/clarity-gate) - Pre-ingestion verification for RAG systems
- [Source of Truth Creator](https://github.com/frmoretto/source-of-truth-creator) - Create .sot files
- [sot-validator](https://pypi.org/project/sot-validator/) - Validate .sot files

## File Format Specification

See the [SOT and CGD File Format Specification](https://github.com/frmoretto/clarity-gate/blob/main/docs/FILE_FORMAT_SPEC.md).

## License

CC BY 4.0 — Use freely with attribution.

## Author

Francesco Marinoni Moretto  
GitHub: [@frmoretto](https://github.com/frmoretto)
