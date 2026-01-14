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
from datetime import date

__version__ = "0.1.1"

# Valid Clarity Gate versions
VALID_VERSIONS = ['1.0', '1.1', '1.2', '1.3', '1.4', '1.5', '1.6']


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
    # BUG FIX #3: Strip BOM and leading whitespace
    clean_content = content.lstrip('\ufeff').lstrip()
    
    match = re.match(r'^---\r?\n([\s\S]*?)\r?\n---', clean_content)
    if not match:
        return None
    
    frontmatter = {}
    lines = match.group(1).split('\n')
    
    for line in lines:
        line = line.rstrip('\r')  # Handle CRLF
        colon_index = line.find(':')
        if colon_index > 0:
            key = line[:colon_index].strip()
            value = line[colon_index + 1:].strip()
            if key:
                frontmatter[key] = value
    
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
    
    # Strip BOM if present
    clean_content = content.lstrip('\ufeff')
    
    # Required: YAML frontmatter
    frontmatter = parse_frontmatter(clean_content)
    if not frontmatter:
        errors.append(ValidationError(
            code='MISSING_FRONTMATTER',
            message='Document must contain YAML frontmatter (--- block)',
            line=1
        ))
    else:
        # Required: clarity-gate-version
        if not frontmatter.get('clarity-gate-version'):
            errors.append(ValidationError(
                code='MISSING_VERSION',
                message='Frontmatter must contain "clarity-gate-version"',
                line=1
            ))
        else:
            # BUG FIX #8: Validate version is a known version
            version = frontmatter['clarity-gate-version'].strip()
            if version not in VALID_VERSIONS:
                warnings.append(ValidationError(
                    code='UNKNOWN_VERSION',
                    message=f'Clarity Gate version "{version}" is not recognized. Known versions: {", ".join(VALID_VERSIONS)}',
                    line=1
                ))
        
        # Required: verified-date
        if not frontmatter.get('verified-date'):
            errors.append(ValidationError(
                code='MISSING_VERIFIED_DATE',
                message='Frontmatter must contain "verified-date"',
                line=1
            ))
        else:
            # BUG FIX #9: Validate date format and not in future
            date_str = frontmatter['verified-date'].strip()
            date_match = re.match(r'^(\d{4})-(\d{2})-(\d{2})$', date_str)
            if not date_match:
                warnings.append(ValidationError(
                    code='INVALID_DATE_FORMAT',
                    message=f'verified-date "{date_str}" should be in YYYY-MM-DD format',
                    line=1
                ))
            else:
                try:
                    doc_date = date.fromisoformat(date_str)
                    if doc_date > date.today():
                        errors.append(ValidationError(
                            code='FUTURE_DATE',
                            message=f'verified-date ({date_str}) is in the future',
                            line=1
                        ))
                except ValueError:
                    warnings.append(ValidationError(
                        code='INVALID_DATE',
                        message=f'verified-date "{date_str}" is not a valid date',
                        line=1
                    ))
        
        # Required: verified-by
        if not frontmatter.get('verified-by'):
            errors.append(ValidationError(
                code='MISSING_VERIFIED_BY',
                message='Frontmatter must contain "verified-by"',
                line=1
            ))
        
        # Required: hitl-status
        if not frontmatter.get('hitl-status'):
            errors.append(ValidationError(
                code='MISSING_HITL_STATUS',
                message='Frontmatter must contain "hitl-status"',
                line=1
            ))
        else:
            # BUG FIX #10: Case-insensitive comparison, trim whitespace
            hitl_status = frontmatter['hitl-status'].strip().upper()
            if hitl_status != 'CONFIRMED':
                warnings.append(ValidationError(
                    code='HITL_NOT_CONFIRMED',
                    message=f'HITL status is "{frontmatter["hitl-status"]}" - should be "CONFIRMED" for full validation',
                    line=1
                ))
        
        # BUG FIX #7: Check for points-passed
        if not frontmatter.get('points-passed'):
            warnings.append(ValidationError(
                code='MISSING_POINTS_PASSED',
                message='Frontmatter should contain "points-passed" listing which verification points were checked',
                line=1
            ))
    
    # Required: Verification summary at end (case-insensitive)
    if not re.search(r'##\s*clarity\s+gate\s+verification', clean_content, re.IGNORECASE):
        errors.append(ValidationError(
            code='MISSING_VERIFICATION_SUMMARY',
            message='Document must contain "## Clarity Gate Verification" section'
        ))
    else:
        # BUG FIX #4: Check that section contains a table
        verification_match = re.search(r'##\s*clarity\s+gate\s+verification[\s\S]*$', clean_content, re.IGNORECASE)
        if verification_match and '|' not in verification_match.group(0):
            warnings.append(ValidationError(
                code='NO_TABLE_IN_VERIFICATION',
                message='Clarity Gate Verification section should contain a points table'
            ))
    
    # BUG FIX #2: Check EACH projection phrase for markers
    projection_phrases = re.findall(r'will\s+(be|reach|reduce|increase|decrease|grow|achieve)', clean_content, re.IGNORECASE)
    unmarked_projections = 0
    
    for match in re.finditer(r'will\s+(be|reach|reduce|increase|decrease|grow|achieve)', clean_content, re.IGNORECASE):
        start = max(0, match.start() - 50)
        end = min(len(clean_content), match.end() + 50)
        context = clean_content[start:end]
        if not re.search(r'\*\(projected|\(projected\)|\*projected\*', context, re.IGNORECASE):
            unmarked_projections += 1
    
    if unmarked_projections > 0:
        warnings.append(ValidationError(
            code='UNMARKED_PROJECTION',
            message=f'Found {unmarked_projections} projection phrase(s) without nearby *(projected)* marker'
        ))
    
    # BUG FIX #5: Better vague quantifier detection - exclude those in annotations
    without_annotations = re.sub(r'\*\([^)]*\)\*', '', clean_content)
    vague_quantifiers = re.findall(r'\b(several|many|most|some)\b', without_annotations, re.IGNORECASE)
    
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
