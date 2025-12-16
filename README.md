# 📚 Citation Extractor

https://ismasa.github.io/GetReferences/

A lightweight scientific web application that extracts keyword-linked citations from academic documents.  Upload Word documents or text files, enter a keyword, and automatically extract all in-text literature references associated with that keyword. 

## Features

- **Drag-and-drop file upload** - Support for `.docx` and `.txt` files
- **Keyword-based extraction** - Find citations within ±1 sentence of your keyword
- **Multiple citation formats** - Handles Author et al., two-author, parenthetical, and grouped citations
- **Smart text processing** - Ignores references sections, headers, and footers
- **Deduplication** - Clean, ordered list of unique references
- **Copy to clipboard** - Easy export of extracted references

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/IsmaSA/GetReferences.git
   cd GetReferences
   ```

2. **Create a virtual environment** (recommended)
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r backend/requirements.txt
   ```

4. **Run the application**
   ```bash
   cd backend
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

5. **Open in browser**
   Navigate to [http://localhost:8000](http://localhost:8000)

## Usage

1. **Upload files** - Drag and drop `.docx` or `.txt` files, or click "Browse Files"
2. **Enter keyword** - Type the keyword or phrase you want to search for
3. **Extract** - Click "Extract References" to find citations
4. **Review** - See all citations found near your keyword
5. **Copy** - Use the "Copy to Clipboard" button to export

## Supported Citation Formats

The application recognizes these common academic citation formats: 

| Format | Example |
|--------|---------|
| Author et al., year | Smith et al., 2010 |
| Author et al.  year | Smith et al.  2010a |
| Two authors with & | Smith & Jones, 2008 |
| Two authors with "and" | Smith and Jones (2008) |
| Parenthetical | (Smith et al., 2010) |
| Grouped | (Smith, 2005; Jones et al., 2012) |

## API Reference

### POST /extract

Extract citations from uploaded documents. 

**Request:**
- `files`: One or more `.docx` or `.txt` files (multipart/form-data)
- `keyword`: Search keyword or phrase (form field)

**Response:**
```json
{
  "references": [
    "Smith et al., 2010",
    "Jones & Brown, 2008"
  ]
}
```

### GET /health

Health check endpoint.

**Response:**
```json
{
  "status": "healthy"
}
```

## Project Structure

```
GetReferences/
├── backend/
│   ├── main.py              # FastAPI application
│   ├── citation_extractor.py # Citation regex patterns & logic
│   ├── text_processor.py     # Document parsing & sentence splitting
│   └── requirements.txt      # Python dependencies
├── frontend/
│   ├── index.html           # Main page
│   ├── styles.css           # Styling
│   └── script.js            # Frontend logic
└── README. md
```

## Future Extensions

This application is designed with extensibility in mind: 

- [ ] PDF support
- [ ] CSV / BibTeX export
- [ ] Citation frequency by year
- [ ] DOI resolution via CrossRef
- [ ] NLP-based sentence classification

## Development

### Running in development mode

```bash
cd backend
uvicorn main:app --reload
```

### Running tests

```bash
# TODO: Add test suite
pytest
```

## License

MIT License - See LICENSE file for details. 

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. 