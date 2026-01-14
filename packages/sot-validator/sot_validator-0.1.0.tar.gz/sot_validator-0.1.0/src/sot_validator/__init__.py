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

__version__ = "0.1.0"


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
    
    # Required: Header block
    if '-- Source of Truth' not in content:
        errors.append(ValidationError(
            code='MISSING_HEADER',
            message='Document must contain "-- Source of Truth" header',
            line=1
        ))
    
    # Required: Last Updated
    if not re.search(r'\*\*Last Updated:\*\*', content):
        errors.append(ValidationError(
            code='MISSING_DATE',
            message='Document must contain "**Last Updated:**" field'
        ))
    
    # Required: Owner
    if not re.search(r'\*\*Owner:\*\*', content):
        errors.append(ValidationError(
            code='MISSING_OWNER',
            message='Document must contain "**Owner:**" field'
        ))
    
    # Required: Status
    if not re.search(r'\*\*Status:\*\*', content):
        errors.append(ValidationError(
            code='MISSING_STATUS',
            message='Document must contain "**Status:**" field'
        ))
    
    # Required: Verification Status table
    if '## Verification Status' not in content:
        errors.append(ValidationError(
            code='MISSING_VERIFICATION_TABLE',
            message='Document must contain "## Verification Status" section'
        ))
    
    # Warning: Status says VERIFIED without qualification
    if re.search(r'Status:\*\*\s*VERIFIED\s*$', content, re.MULTILINE):
        warnings.append(ValidationError(
            code='UNQUALIFIED_VERIFIED',
            message='Status "VERIFIED" should be qualified (e.g., "with noted exceptions")'
        ))
    
    # Warning: Estimates in Verified Data section
    verified_match = re.search(r'## Verified Data[\s\S]*?(?=##|$)', content)
    if verified_match:
        verified_section = verified_match.group(0)
        if re.search(r'~\d|estimated|approximately', verified_section, re.IGNORECASE):
            warnings.append(ValidationError(
                code='ESTIMATES_IN_VERIFIED',
                message='Estimates found in Verified Data section - move to Estimates section'
            ))
    
    # Warning: Missing staleness markers
    if '## Verified Data' in content:
        if not re.search(r'\[STABLE\]|\[VOLATILE\]|\[CHECK BEFORE CITING\]|\[SNAPSHOT\]', content):
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
    return ('-- Source of Truth' in content and 
            '## Verification Status' in content)


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
