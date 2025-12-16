"""
Text processing module for document parsing and sentence splitting. 
Handles extraction of text from various file formats and intelligent
sentence boundary detection.
"""

import re
import io
from typing import List, Optional
from docx import Document
from docx.opc.exceptions import PackageNotFoundError


def extract_text_from_docx(content: bytes) -> str:
    """
    Extract plain text from a Word document (. docx).
    
    Ignores: 
    - Headers and footers
    - Tables (often contain data, not prose)
    - References section (if detectable)
    
    Args:
        content: Raw bytes of the . docx file
        
    Returns: 
        Extracted plain text
    """
    try:
        doc = Document(io.BytesIO(content))
    except PackageNotFoundError:
        raise ValueError("Invalid or corrupted .docx file")
    
    paragraphs = []
    in_references_section = False
    
    # Common patterns that indicate start of references section
    references_headers = [
        r'^references?\s*$',
        r'^bibliography\s*$',
        r'^works?\s+cited\s*$',
        r'^literature\s+cited\s*$',
        r'^sources?\s*$',
    ]
    references_pattern = re.compile(
        '|'.join(references_headers), 
        re. IGNORECASE
    )
    
    for para in doc. paragraphs: 
        text = para.text. strip()
        
        if not text:
            continue
        
        # Check if we've hit the references section
        if references_pattern.match(text):
            in_references_section = True
            continue
        
        # Skip paragraphs in references section
        if in_references_section:
            continue
        
        # Skip if paragraph looks like a header/title (all caps, very short)
        if text.isupper() and len(text) < 100:
            continue
        
        paragraphs.append(text)
    
    return '\n\n'. join(paragraphs)


def extract_text_from_txt(content: bytes) -> str:
    """
    Extract text from a plain text file.
    
    Attempts multiple encodings to handle various file sources.
    
    Args:
        content: Raw bytes of the . txt file
        
    Returns:
        Decoded text content
    """
    # Try common encodings
    encodings = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252']
    
    for encoding in encodings: 
        try: 
            return content.decode(encoding)
        except UnicodeDecodeError:
            continue
    
    # Fallback with error replacement
    return content.decode('utf-8', errors='replace')


def extract_text_from_file(content: bytes, filename:  str) -> str:
    """
    Extract text from a file based on its extension.
    
    Args:
        content: Raw bytes of the file
        filename: Name of the file (used to determine type)
        
    Returns:
        Extracted text content
    """
    filename_lower = filename. lower()
    
    if filename_lower.endswith('.docx'):
        return extract_text_from_docx(content)
    elif filename_lower.endswith('.txt'):
        return extract_text_from_txt(content)
    else:
        raise ValueError(f"Unsupported file type: {filename}")


def split_into_sentences(text:  str) -> List[str]:
    """
    Split text into sentences using intelligent boundary detection.
    
    Handles common abbreviations and edge cases in academic text: 
    - Abbreviations (Dr., Mr., Mrs., Prof., etc.)
    - "et al." citations
    - Decimal numbers
    - Initials (A.  B. Smith)
    
    Args:
        text: The text to split
        
    Returns:
        List of sentences
    """
    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Protect common abbreviations from being split
    abbreviations = [
        (r'\bDr\. ', 'Dr<DOT>'),
        (r'\bMr\.', 'Mr<DOT>'),
        (r'\bMrs\. ', 'Mrs<DOT>'),
        (r'\bMs\.', 'Ms<DOT>'),
        (r'\bProf\.', 'Prof<DOT>'),
        (r'\bvs\.', 'vs<DOT>'),
        (r'\bVs\.', 'Vs<DOT>'),
        (r'\bet al\.', 'et al<DOT>'),
        (r'\bEt al\.', 'Et al<DOT>'),
        (r'\bi\.e\.', 'i<DOT>e<DOT>'),
        (r'\be\.g\.', 'e<DOT>g<DOT>'),
        (r'\bcf\.', 'cf<DOT>'),
        (r'\bFig\.', 'Fig<DOT>'),
        (r'\bfig\.', 'fig<DOT>'),
        (r'\bNo\.', 'No<DOT>'),
        (r'\bno\.', 'no<DOT>'),
        (r'\bVol\.', 'Vol<DOT>'),
        (r'\bvol\.', 'vol<DOT>'),
        (r'\bpp\.', 'pp<DOT>'),
        (r'\bPp\.', 'Pp<DOT>'),
        (r'\bEd\.', 'Ed<DOT>'),
        (r'\bed\.', 'ed<DOT>'),
        (r'\bEds\.', 'Eds<DOT>'),
        (r'\beds\.', 'eds<DOT>'),
        # Protect single letter initials (A.  B. Smith)
        (r'\b([A-Z])\.(\s+[A-Z])', r'\1<DOT>\2'),
    ]
    
    protected_text = text
    for pattern, replacement in abbreviations: 
        protected_text = re.sub(pattern, replacement, protected_text)
    
    # Protect decimal numbers (e.g., 3.14, p < . 05)
    protected_text = re.sub(r'(\d)\. (\d)', r'\1<DECIMAL>\2', protected_text)
    
    # Split on sentence-ending punctuation followed by space and capital letter
    # or end of string
    sentence_pattern = re.compile(r'(? <=[.!? ])\s+(?=[A-Z])|(?<=[.! ?])$')
    raw_sentences = sentence_pattern.split(protected_text)
    
    # Restore protected characters and clean up
    sentences = []
    for sentence in raw_sentences:
        sentence = sentence.replace('<DOT>', '.')
        sentence = sentence.replace('<DECIMAL>', '.')
        sentence = sentence. strip()
        
        if sentence:
            sentences.append(sentence)
    
    return sentences