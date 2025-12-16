"""
Citation extraction module using regex patterns. 
Handles various academic citation formats and enforces keyword proximity rules.
"""

import re
from typing import List, Set

# =============================================================================
# CITATION REGEX PATTERNS
# =============================================================================

def extract_citations_from_text(text:  str) -> List[str]:
    """
    Extract all citations from a given text using regex patterns.
    """
    citations = []
    
    # Pattern 1: Author et al., 2010 or Author et al.  2010a
    pattern1 = r'\b([A-Z][a-zA-Z\'-]+)\s+et\s+al\.[\s,]*(\d{4}[a-z]?)'
    for match in re.finditer(pattern1, text):
        citations.append(f"{match.group(1)} et al., {match.group(2)}")
    
    # Pattern 2: (Author et al., 2010) - parenthetical
    pattern2 = r'\(([A-Z][a-zA-Z\'-]+)\s+et\s+al\. [\s,]*(\d{4}[a-z]? )\)'
    for match in re.finditer(pattern2, text):
        citations.append(f"{match.group(1)} et al., {match.group(2)}")
    
    # Pattern 3: Author & Coauthor, 2008
    pattern3 = r'\b([A-Z][a-zA-Z\'-]+)\s+&\s+([A-Z][a-zA-Z\'-]+)[\s,]*(\d{4}[a-z]? )'
    for match in re.finditer(pattern3, text):
        citations. append(f"{match.group(1)} & {match.group(2)}, {match.group(3)}")
    
    # Pattern 4: Author and Coauthor, 2008
    pattern4 = r'\b([A-Z][a-zA-Z\'-]+)\s+and\s+([A-Z][a-zA-Z\'-]+)[\s,]*(\d{4}[a-z]?)'
    for match in re. finditer(pattern4, text):
        citations.append(f"{match.group(1)} & {match.group(2)}, {match.group(3)}")
    
    # Pattern 5: (Author & Coauthor, 2008) - parenthetical
    pattern5 = r'\(([A-Z][a-zA-Z\'-]+)\s+&\s+([A-Z][a-zA-Z\'-]+)[\s,]*(\d{4}[a-z]?)\)'
    for match in re.finditer(pattern5, text):
        citations.append(f"{match.group(1)} & {match.group(2)}, {match.group(3)}")
    
    # Pattern 6: (Author and Coauthor, 2008) - parenthetical
    pattern6 = r'\(([A-Z][a-zA-Z\'-]+)\s+and\s+([A-Z][a-zA-Z\'-]+)[\s,]*(\d{4}[a-z]?)\)'
    for match in re.finditer(pattern6, text):
        citations.append(f"{match.group(1)} & {match.group(2)}, {match.group(3)}")
    
    # Pattern 7: Author (2010) - author with year in parentheses
    pattern7 = r'\b([A-Z][a-zA-Z\'-]+)\s+\((\d{4}[a-z]?)\)'
    for match in re.finditer(pattern7, text):
        citations.append(f"{match. group(1)}, {match.group(2)}")
    
    # Pattern 8: (Author, 2010) - simple parenthetical
    pattern8 = r'\(([A-Z][a-zA-Z\'-]+)[\s,]+(\d{4}[a-z]?)\)'
    for match in re. finditer(pattern8, text):
        citations.append(f"{match.group(1)}, {match.group(2)}")
    
    # Pattern 9: Grouped citations (Author, 2010; Coauthor, 2012)
    pattern9 = r'\(([^)]*\d{4}[^)]*;[^)]*\d{4}[^)]*)\)'
    for match in re.finditer(pattern9, text):
        group_content = match.group(1)
        parts = group_content. split(';')
        for part in parts: 
            part = part.strip()
            if part and re.search(r'\d{4}', part):
                citations.append(part)
    
    return citations


def is_valid_citation(citation: str) -> bool:
    """
    Validate that a citation string is properly formed.
    """
    if not citation: 
        return False
    if not re.search(r'\b(19|20)\d{2}[a-z]?\b', citation):
        return False
    if not re.match(r'^[A-Z]', citation):
        return False
    if len(citation) < 7:
        return False
    return True


def keyword_in_sentence(sentence: str, keyword: str) -> bool:
    """
    Check if keyword appears in sentence (case-insensitive).
    """
    pattern = re.compile(r'\b' + re. escape(keyword) + r'\b', re.IGNORECASE)
    return bool(pattern.search(sentence))


def extract_citations_with_keyword_proximity(
    sentences: List[str],
    keyword: str
) -> List[str]:
    """
    Extract citations that appear within +/-1 sentence of the keyword. 
    """
    # Track which sentences contain the keyword
    keyword_sentence_indices:  Set[int] = set()
    
    for i, sentence in enumerate(sentences):
        if keyword_in_sentence(sentence, keyword):
            keyword_sentence_indices.add(i)
    
    # Determine which sentences are within proximity of keyword sentences
    valid_sentence_indices:  Set[int] = set()
    for idx in keyword_sentence_indices:
        valid_sentence_indices. add(idx - 1)  # Previous sentence
        valid_sentence_indices.add(idx)       # Same sentence
        valid_sentence_indices.add(idx + 1)   # Next sentence
    
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
            citation_key = citation.lower().replace(' ', '')
            if citation_key not in seen_citations: 
                seen_citations.add(citation_key)
                if is_valid_citation(citation):
                    ordered_citations. append(citation)
    
    return ordered_citations