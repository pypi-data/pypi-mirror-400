"""
cgd-validator

Validator for Clarity-Gated Document (.cgd) files
Documents verified and annotated for safe LLM ingestion

Part of the Clarity Gate ecosystem:
- .sot (Source of Truth) - Authoritative reference documents
- .cgd (Clarity-Gated Document) - Verified for LLM ingestion

https://github.com/frmoretto/clarity-gate
"""

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from pathlib import Path

__version__ = "0.1.0"


@dataclass
class ValidationError:
    """A validation error"""
    code: str
    message: str
    line: Optional[int] = None


@dataclass
class ValidationResult:
    """Result of validating a .cgd file"""
    valid: bool
    errors: List[ValidationError] = field(default_factory=list)
    warnings: List[ValidationError] = field(default_factory=list)
    frontmatter: Optional[Dict[str, str]] = None
    version: str = __version__


def parse_frontmatter(content: str) -> Optional[Dict[str, str]]:
    """
    Parse YAML frontmatter from CGD file
    
    Args:
        content: The file content
        
    Returns:
        Parsed frontmatter dict or None
    """
    match = re.match(r'^---\n([\s\S]*?)\n---', content)
    if not match:
        return None
    
    frontmatter = {}
    lines = match.group(1).split('\n')
    
    for line in lines:
        if ':' in line:
            key, *value_parts = line.split(':')
            frontmatter[key.strip()] = ':'.join(value_parts).strip()
    
    return frontmatter


def validate(content: str) -> ValidationResult:
    """
    Validate a Clarity-Gated Document (.cgd) file
    
    Args:
        content: The file content to validate
        
    Returns:
        ValidationResult with errors and warnings
    """
    errors = []
    warnings = []
    
    # Required: YAML frontmatter
    frontmatter = parse_frontmatter(content)
    if not frontmatter:
        errors.append(ValidationError(
            code='MISSING_FRONTMATTER',
            message='Document must contain YAML frontmatter (--- block)',
            line=1
        ))
    else:
        # Required frontmatter fields
        if 'clarity-gate-version' not in frontmatter:
            errors.append(ValidationError(
                code='MISSING_VERSION',
                message='Frontmatter must contain "clarity-gate-version"',
                line=1
            ))
        
        if 'verified-date' not in frontmatter:
            errors.append(ValidationError(
                code='MISSING_VERIFIED_DATE',
                message='Frontmatter must contain "verified-date"',
                line=1
            ))
        
        if 'verified-by' not in frontmatter:
            errors.append(ValidationError(
                code='MISSING_VERIFIED_BY',
                message='Frontmatter must contain "verified-by"',
                line=1
            ))
        
        if 'hitl-status' not in frontmatter:
            errors.append(ValidationError(
                code='MISSING_HITL_STATUS',
                message='Frontmatter must contain "hitl-status"',
                line=1
            ))
        
        # Warning: HITL not confirmed
        if frontmatter.get('hitl-status') and frontmatter['hitl-status'] != 'CONFIRMED':
            warnings.append(ValidationError(
                code='HITL_NOT_CONFIRMED',
                message=f'HITL status is "{frontmatter["hitl-status"]}" - should be "CONFIRMED" for full validation',
                line=1
            ))
    
    # Required: Verification summary at end
    if '## Clarity Gate Verification' not in content:
        errors.append(ValidationError(
            code='MISSING_VERIFICATION_SUMMARY',
            message='Document must contain "## Clarity Gate Verification" section'
        ))
    
    # Warning: Projections without markers
    if re.search(r'will be|will reach|will reduce', content, re.IGNORECASE):
        if not re.search(r'\*\(projected', content, re.IGNORECASE):
            warnings.append(ValidationError(
                code='UNMARKED_PROJECTION',
                message='Document contains "will be/reach/reduce" without *(projected)* marker'
            ))
    
    # Warning: Vague quantifiers without annotation
    vague_quantifiers = re.findall(r'\b(several|many|most|some)\b(?!\s*\*\()', content, re.IGNORECASE)
    if vague_quantifiers:
        warnings.append(ValidationError(
            code='UNMARKED_VAGUE_QUANTIFIER',
            message=f'Found {len(vague_quantifiers)} vague quantifier(s) without annotation (several, many, most, some)'
        ))
    
    return ValidationResult(
        valid=len(errors) == 0,
        errors=errors,
        warnings=warnings,
        frontmatter=frontmatter
    )


def is_valid(content: str) -> bool:
    """
    Check if content is a valid .cgd file
    
    Args:
        content: The file content to check
        
    Returns:
        True if valid
    """
    return validate(content).valid


def detect(content: str) -> bool:
    """
    Detect if a file is a .cgd file based on content
    
    Args:
        content: The file content
        
    Returns:
        True if appears to be .cgd format
    """
    frontmatter = parse_frontmatter(content)
    return frontmatter is not None and 'clarity-gate-version' in frontmatter


def validate_file(path: str | Path) -> ValidationResult:
    """
    Validate a .cgd file from disk
    
    Args:
        path: Path to the file
        
    Returns:
        ValidationResult with errors and warnings
    """
    path = Path(path)
    content = path.read_text(encoding='utf-8')
    return validate(content)
