@app.route('/extract', methods=['POST'])
def extract():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not file.filename.lower().endswith('.pdf'):
            return jsonify({'error': 'File must be a PDF'}), 400
        
        # Read the PDF file
        pdf_content = file.read()
        
        # Extract references
        references = extract_references_from_pdf(pdf_content)
        
        if not references:
            return jsonify({'error': 'No references found in the PDF'}), 404
        
        return jsonify({'references': references})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Failed to extract references: {str(e)}'}), 500
