"""
Citation extraction module using regex patterns. 
Handles various academic citation formats and enforces keyword proximity rules.
"""

import re
from typing import List, Set, Tuple

# =============================================================================
# CITATION REGEX PATTERNS
# Each pattern is designed to match specific citation formats commonly used
# in academic literature.  Patterns are ordered from most specific to general.
# =============================================================================

CITATION_PATTERNS = [
    # ---------------------------------------------------------------------
    # Pattern 1: "Author et al., 2010" or "Author et al.  2010" or "Author et al. 2010a"
    # Matches: Smith et al., 2010 | Smith et al. 2010 | Smith et al. 2010a
    # ---------------------------------------------------------------------
    (
        r'\b([A-Z][a-zA-Z\'-]+(? :\s+[A-Z][a-zA-Z\'-]+)?)\s+et\s+al\. [\s,]*(\d{4}[a-z]? )',
        lambda m: f"{m.group(1)} et al., {m.group(2)}"
    ),
    
    # ---------------------------------------------------------------------
    # Pattern 2: "(Author et al., 2010)" - parenthetical et al. citation
    # Matches: (Smith et al., 2010) | (Smith et al.  2010)
    # ---------------------------------------------------------------------
    (
        r'\(([A-Z][a-zA-Z\'-]+(?:\s+[A-Z][a-zA-Z\'-]+)?)\s+et\s+al\.[\s,]*(\d{4}[a-z]?)\)',
        lambda m: f"{m.group(1)} et al., {m.group(2)}"
    ),
    
    # ---------------------------------------------------------------------
    # Pattern 3: "Author & Coauthor, 2008" or "Author and Coauthor, 2008"
    # Matches:  Smith & Jones, 2008 | Smith and Jones, 2008
    # ---------------------------------------------------------------------
    (
        r'\b([A-Z][a-zA-Z\'-]+)\s+(? :&|and)\s+([A-Z][a-zA-Z\'-]+)[\s,]*(\d{4}[a-z]?)',
        lambda m:  f"{m.group(1)} & {m.group(2)}, {m.group(3)}"
    ),
    
    # ---------------------------------------------------------------------
    # Pattern 4: "(Author & Coauthor, 2008)" - parenthetical two-author
    # Matches:  (Smith & Jones, 2008) | (Smith and Jones, 2008)
    # ---------------------------------------------------------------------
    (
        r'\(([A-Z][a-zA-Z\'-]+)\s+(?:&|and)\s+([A-Z][a-zA-Z\'-]+)[\s,]*(\d{4}[a-z]?)\)',
        lambda m: f"{m.group(1)} & {m.group(2)}, {m.group(3)}"
    ),
    
    # ---------------------------------------------------------------------
    # Pattern 5: "Author (2010)" - author with year in parentheses
    # Matches: Smith (2010) | Smith (2010a)
    # ---------------------------------------------------------------------
    (
        r'\b([A-Z][a-zA-Z\'-]+(? :\s+[A-Z][a-zA-Z\'-]+)?)\s+\((\d{4}[a-z]?)\)',
        lambda m:  f"{m.group(1)}, {m.group(2)}"
    ),
    
    # ---------------------------------------------------------------------
    # Pattern 6: "(Author, 2010)" - simple parenthetical citation
    # Matches:  (Smith, 2010) | (Smith 2010)
    # ---------------------------------------------------------------------
    (
        r'\(([A-Z][a-zA-Z\'-]+)[\s,]+(\d{4}[a-z]?)\)',
        lambda m: f"{m.group(1)}, {m.group(2)}"
    ),
    
    # ---------------------------------------------------------------------
    # Pattern 7: "Author, 2010" - simple inline citation
    # Matches: Smith, 2010 | Smith 2010
    # ---------------------------------------------------------------------
    (
        r'\b([A-Z][a-zA-Z\'-]+)[\s,]+(\d{4}[a-z]?)\b(? !\s*[-–])',
        lambda m: f"{m. group(1)}, {m.group(2)}"
    ),
]

# Pattern for multiple citations within parentheses:  (Author, 2010; Coauthor et al., 2012)
GROUPED_CITATION_PATTERN = re.compile(
    r'\(([^)]+\d{4}[a-z]?(? :\s*;\s*[^)]+\d{4}[a-z]?)+)\)'
)

# Pattern to split grouped citations by semicolon
SEMICOLON_SPLIT_PATTERN = re.compile(r'\s*;\s*')


def extract_citations_from_text(text:  str) -> List[str]:
    """
    Extract all citations from a given text using regex patterns.
    
    Args: 
        text: The text to search for citations
        
    Returns:
        List of normalized citation strings
    """
    citations = []
    
    # First, handle grouped citations within parentheses
    for match in GROUPED_CITATION_PATTERN.finditer(text):
        group_content = match.group(1)
        # Split by semicolons and process each citation
        individual_citations = SEMICOLON_SPLIT_PATTERN.split(group_content)
        for citation in individual_citations:
            citation = citation.strip()
            if citation: 
                normalized = normalize_citation(citation)
                if normalized: 
                    citations. append(normalized)
    
    # Then apply individual patterns
    for pattern, formatter in CITATION_PATTERNS:
        compiled = re.compile(pattern)
        for match in compiled.finditer(text):
            try:
                normalized = formatter(match)
                if normalized and is_valid_citation(normalized):
                    citations.append(normalized)
            except Exception:
                continue
    
    return citations


def normalize_citation(citation: str) -> str:
    """
    Normalize a citation string to a consistent format.
    
    Args:
        citation: Raw citation string
        
    Returns:
        Normalized citation string
    """
    # Remove extra whitespace
    citation = ' '.join(citation. split())
    
    # Try to match and format using patterns
    for pattern, formatter in CITATION_PATTERNS:
        match = re.match(pattern, citation)
        if match: 
            try:
                return formatter(match)
            except Exception:
                continue
    
    # If no pattern matches, return cleaned version
    # Check if it looks like a valid citation (has author and year)
    if re.search(r'[A-Z][a-zA-Z\'-]+.*\d{4}', citation):
        return citation. strip()
    
    return ""


def is_valid_citation(citation:  str) -> bool:
    """
    Validate that a citation string is properly formed.
    
    Args:
        citation: Citation string to validate
        
    Returns: 
        True if valid, False otherwise
    """
    if not citation: 
        return False
    
    # Must contain a year (1900-2099)
    if not re.search(r'\b(19|20)\d{2}[a-z]?\b', citation):
        return False
    
    # Must start with a capital letter (author name)
    if not re.match(r'^[A-Z]', citation):
        return False
    
    # Must not be too short (minimum:  "A, 2000" = 7 chars)
    if len(citation) < 7:
        return False
    
    return True


def keyword_in_sentence(sentence: str, keyword:  str) -> bool:
    """
    Check if keyword appears in sentence (case-insensitive).
    
    Args:
        sentence: The sentence to search
        keyword: The keyword to find
        
    Returns:
        True if keyword is found, False otherwise
    """
    # Use word boundary matching for more accurate results
    pattern = re.compile(r'\b' + re.escape(keyword) + r'\b', re.IGNORECASE)
    return bool(pattern.search(sentence))


def extract_citations_with_keyword_proximity(
    sentences: List[str], 
    keyword: str
) -> List[str]:
    """
    Extract citations that appear within ±1 sentence of the keyword.
    
    This is the main extraction function that enforces the proximity rule: 
    a citation is only included if the keyword appears in the same sentence,
    one sentence before, or one sentence after.
    
    Args: 
        sentences: List of sentences from the document
        keyword: The keyword to search for
        
    Returns: 
        Deduplicated list of citations in order of first appearance
    """
    # Track which sentences contain the keyword
    keyword_sentence_indices:  Set[int] = set()
    
    for i, sentence in enumerate(sentences):
        if keyword_in_sentence(sentence, keyword):
            keyword_sentence_indices.add(i)
    
    # Determine which sentences are within proximity (±1) of keyword sentences
    valid_sentence_indices:  Set[int] = set()
    for idx in keyword_sentence_indices:
        valid_sentence_indices. add(idx - 1)  # Previous sentence
        valid_sentence_indices.add(idx)       # Same sentence
        valid_sentence_indices.add(idx + 1)  # Next sentence
    
    # Remove invalid indices
    valid_sentence_indices = {
        idx for idx in valid_sentence_indices 
        if 0 <= idx < len(sentences)
    }
    
    # Extract citations from valid sentences
    seen_citations: Set[str] = set()
    ordered_citations: List[str] = []
    
    for idx in sorted(valid_sentence_indices):
        sentence = sentences[idx]
        citations = extract_citations_from_text(sentence)
        
        for citation in citations: 
            # Normalize for deduplication comparison
            citation_key = citation.lower().replace(' ', '')
            if citation_key not in seen_citations: 
                seen_citations.add(citation_key)
                ordered_citations.append(citation)
    
    return ordered_citations