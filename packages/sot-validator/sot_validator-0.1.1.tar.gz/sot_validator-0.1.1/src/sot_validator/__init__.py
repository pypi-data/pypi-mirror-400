"""
sot-validator

Validator for Source of Truth (.sot) files
Epistemic quality verification for AI-safe documentation

Part of the Clarity Gate ecosystem:
- .sot (Source of Truth) - Authoritative reference documents
- .cgd (Clarity-Gated Document) - Verified for LLM ingestion

https://github.com/frmoretto/clarity-gate
"""

import re
from dataclasses import dataclass, field
from typing import List, Optional
from pathlib import Path
from datetime import date

__version__ = "0.1.1"


@dataclass
class ValidationError:
    """A validation error"""
    code: str
    message: str
    line: Optional[int] = None


@dataclass
class ValidationResult:
    """Result of validating a .sot file"""
    valid: bool
    errors: List[ValidationError] = field(default_factory=list)
    warnings: List[ValidationError] = field(default_factory=list)
    version: str = __version__


def validate(content: str) -> ValidationResult:
    """
    Validate a Source of Truth (.sot) file
    
    Args:
        content: The file content to validate
        
    Returns:
        ValidationResult with errors and warnings
    """
    errors = []
    warnings = []
    
    # Strip BOM if present
    clean_content = content.lstrip('\ufeff')
    
    # Required: Header block (case-insensitive)
    if not re.search(r'--\s*source\s+of\s+truth', clean_content, re.IGNORECASE):
        errors.append(ValidationError(
            code='MISSING_HEADER',
            message='Document must contain "-- Source of Truth" header',
            line=1
        ))
    
    # Required: Last Updated (case-insensitive)
    if not re.search(r'\*\*last\s*updated:\*\*', clean_content, re.IGNORECASE):
        errors.append(ValidationError(
            code='MISSING_DATE',
            message='Document must contain "**Last Updated:**" field'
        ))
    else:
        # BUG FIX #9: Validate date is not in future
        date_match = re.search(r'\*\*last\s*updated:\*\*\s*(\d{4}-\d{2}-\d{2})', clean_content, re.IGNORECASE)
        if date_match:
            try:
                doc_date = date.fromisoformat(date_match.group(1))
                if doc_date > date.today():
                    errors.append(ValidationError(
                        code='FUTURE_DATE',
                        message=f'Last Updated date ({date_match.group(1)}) is in the future'
                    ))
            except ValueError:
                pass  # Invalid date format, will be caught by other checks
    
    # Required: Owner (case-insensitive)
    if not re.search(r'\*\*owner:\*\*', clean_content, re.IGNORECASE):
        errors.append(ValidationError(
            code='MISSING_OWNER',
            message='Document must contain "**Owner:**" field'
        ))
    
    # Required: Status (case-insensitive)
    if not re.search(r'\*\*status:\*\*', clean_content, re.IGNORECASE):
        errors.append(ValidationError(
            code='MISSING_STATUS',
            message='Document must contain "**Status:**" field'
        ))
    
    # Required: Verification Status table (case-insensitive)
    has_verification_section = bool(re.search(r'##\s*verification\s+status', clean_content, re.IGNORECASE))
    if not has_verification_section:
        errors.append(ValidationError(
            code='MISSING_VERIFICATION_TABLE',
            message='Document must contain "## Verification Status" section'
        ))
    else:
        # BUG FIX #4: Check that section contains a table
        verification_match = re.search(r'##\s*verification\s+status[\s\S]*?(?=##|$)', clean_content, re.IGNORECASE)
        if verification_match and '|' not in verification_match.group(0):
            warnings.append(ValidationError(
                code='NO_TABLE_IN_VERIFICATION',
                message='Verification Status section should contain a markdown table'
            ))
    
    # Warning: Status says VERIFIED without qualification (case-insensitive)
    if re.search(r'status:\*\*\s*verified\s*$', clean_content, re.IGNORECASE | re.MULTILINE):
        warnings.append(ValidationError(
            code='UNQUALIFIED_VERIFIED',
            message='Status "VERIFIED" should be qualified (e.g., "with noted exceptions")'
        ))
    
    # Extract Verified Data section for scoped checks
    verified_data_match = re.search(r'##\s*verified\s+data[\s\S]*?(?=##|$)', clean_content, re.IGNORECASE)
    verified_data_section = verified_data_match.group(0) if verified_data_match else None
    
    if verified_data_section:
        # BUG FIX #4: Check that Verified Data contains a table
        if '|' not in verified_data_section:
            warnings.append(ValidationError(
                code='NO_TABLE_IN_VERIFIED_DATA',
                message='Verified Data section should contain a markdown table'
            ))
        
        # Warning: Estimates in Verified Data section
        if re.search(r'~\d|estimated|approximately', verified_data_section, re.IGNORECASE):
            warnings.append(ValidationError(
                code='ESTIMATES_IN_VERIFIED',
                message='Estimates found in Verified Data section - move to Estimates section'
            ))
        
        # BUG FIX #1: Check staleness markers WITHIN Verified Data section only
        if not re.search(r'\[STABLE\]|\[VOLATILE\]|\[CHECK BEFORE CITING\]|\[SNAPSHOT\]', verified_data_section, re.IGNORECASE):
            warnings.append(ValidationError(
                code='MISSING_STALENESS',
                message='Verified Data should include staleness markers ([STABLE], [VOLATILE], etc.)'
            ))
    
    return ValidationResult(
        valid=len(errors) == 0,
        errors=errors,
        warnings=warnings
    )


def is_valid(content: str) -> bool:
    """
    Check if content is a valid .sot file
    
    Args:
        content: The file content to check
        
    Returns:
        True if valid
    """
    return validate(content).valid


def detect(content: str) -> bool:
    """
    Detect if a file is a .sot file based on content
    
    Args:
        content: The file content
        
    Returns:
        True if appears to be .sot format
    """
    clean_content = content.lstrip('\ufeff')
    return (bool(re.search(r'--\s*source\s+of\s+truth', clean_content, re.IGNORECASE)) and 
            bool(re.search(r'##\s*verification\s+status', clean_content, re.IGNORECASE)))


def validate_file(path: str | Path) -> ValidationResult:
    """
    Validate a .sot file from disk
    
    Args:
        path: Path to the file
        
    Returns:
        ValidationResult with errors and warnings
    """
    path = Path(path)
    content = path.read_text(encoding='utf-8')
    result = validate(content)
    return result
