"""
FastAPI application for citation extraction from academic documents.
Provides a POST /extract endpoint that accepts document files,
returning all citations found in the documents.
"""

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from typing import List
import os

# Use relative imports when running as a package
try:
    from backend.text_processor import extract_text_from_file, split_into_sentences
    from backend.citation_extractor import extract_all_citations
except ImportError:
    from text_processor import extract_text_from_file, split_into_sentences
    from citation_extractor import extract_all_citations

app = FastAPI(
    title="Citation Extractor API",
    description="Extract citations from academic documents",
    version="1.0.0"
)

# Enable CORS for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/extract")
async def extract_references(
    files: List[UploadFile] = File(..., description="One or more .docx or .txt files")
):
    """
    Extract all citations from uploaded documents.
    """
    if not files:
        raise HTTPException(status_code=400, detail="At least one file is required")
    
    # Collect all text from uploaded files
    all_text = []
    
    for file in files:
        # Validate file extension
        filename = file.filename.lower()
        if not (filename.endswith('.docx') or filename.endswith('.txt')):
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type: {file.filename}. Only .docx and .txt files are supported."
            )
        
        try:
            # Read file content
            content = await file.read()
            
            # Extract text based on file type
            text = extract_text_from_file(content, filename)
            if text:
                all_text.append(text)
                
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"Error processing file {file.filename}: {str(e)}"
            )
    
    if not all_text:
        return {"references": []}
    
    # Merge all text while preserving sentence boundaries
    combined_text = "\n\n".join(all_text)
    
    # Split into sentences
    sentences = split_into_sentences(combined_text)
    
    # Extract all citations
    references = extract_all_citations(sentences)
    
    return {"references": references}


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


# Mount frontend static files
frontend_path = os.path.join(os.path.dirname(__file__), "..", "frontend")
if os.path.exists(frontend_path):
    app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")