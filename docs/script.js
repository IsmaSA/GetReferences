/**
 * Citation Extractor - Frontend JavaScript
 * Modern UI with enhanced user experience
 */

// =============================================================================
// DOM Elements
// =============================================================================

const dropZone = document.getElementById('drop-zone');
const fileInput = document.getElementById('file-input');
const fileList = document.getElementById('file-list');
const extractBtn = document.getElementById('extract-btn');
const clearBtn = document.getElementById('clear-btn');
const resultsSection = document.getElementById('results-section');
const resultsCount = document.getElementById('results-count');
const resultsContainer = document.getElementById('results-container');
const resultsFooter = document.getElementById('results-footer');
const copyBtn = document.getElementById('copy-btn');
const downloadBtn = document.getElementById('download-btn');
const errorMessage = document.getElementById('error-message');
const errorText = document.getElementById('error-text');
const toast = document.getElementById('toast');
const toastMessage = document.getElementById('toast-message');

// =============================================================================
// Configuration
// =============================================================================

// API URL - Replace with your actual Render deployment URL
const API_URL = 'https://getreferences.onrender.com';

// =============================================================================
// State
// =============================================================================

let uploadedFiles = [];
let extractedReferences = [];

// =============================================================================
// Utility Functions
// =============================================================================

function formatFileSize(bytes) {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function showToast(message, duration = 3000) {
    toastMessage.textContent = message;
    toast.hidden = false;
    setTimeout(() => toast.classList.add('show'), 10);
    
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => toast.hidden = true, 300);
    }, duration);
}

function getFileIcon(filename) {
    if (filename.endsWith('.docx')) return '📄';
    if (filename.endsWith('.txt')) return '📝';
    return '📁';
}

// =============================================================================
// File Handling
// =============================================================================

function handleFiles(files) {
    const validExtensions = ['.docx', '.doc', '.txt'];
    let addedCount = 0;
    
    for (const file of files) {
        const ext = '.' + file.name.split('.').pop().toLowerCase();
        
        if (!validExtensions.includes(ext)) {
            showError(`Unsupported file: ${file.name}. Only .docx, .doc and .txt files are supported.`);
            continue;
        }
        
        if (uploadedFiles.some(f => f.name === file.name && f.size === file.size)) {
            continue;
        }
        
        uploadedFiles.push(file);
        addedCount++;
    }
    
    if (addedCount > 0) {
        showToast(`Added ${addedCount} file${addedCount > 1 ? 's' : ''}`);
    }
    
    updateFileList();
    updateUI();
    hideError();
}

function updateFileList() {
    if (uploadedFiles.length === 0) {
        fileList.innerHTML = '';
        return;
    }
    
    fileList.innerHTML = uploadedFiles.map((file, index) => `
        <div class="file-item">
            <div class="file-icon">${getFileIcon(file.name)}</div>
            <div class="file-info">
                <div class="file-name">${escapeHtml(file.name)}</div>
                <div class="file-size">${formatFileSize(file.size)}</div>
            </div>
            <button class="file-remove" data-index="${index}" title="Remove file">
                <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <line x1="18" y1="6" x2="6" y2="18"></line>
                    <line x1="6" y1="6" x2="18" y2="18"></line>
                </svg>
            </button>
        </div>
    `).join('');
    
    // Add remove handlers
    fileList.querySelectorAll('.file-remove').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const index = parseInt(e.currentTarget.dataset.index);
            uploadedFiles.splice(index, 1);
            updateFileList();
            updateUI();
            showToast('File removed');
        });
    });
}

// =============================================================================
// UI State Management
// =============================================================================

function updateUI() {
    const hasFiles = uploadedFiles.length > 0;
    
    // Enable extract button if files are uploaded
    extractBtn.disabled = !hasFiles;
    clearBtn.hidden = !(hasFiles || extractedReferences.length > 0);
}

function setLoading(loading) {
    extractBtn.disabled = loading;
    
    const btnContent = extractBtn.querySelector('.btn-content');
    const btnLoading = extractBtn.querySelector('.btn-loading');
    
    btnContent.hidden = loading;
    btnLoading.hidden = !loading;
}

function showError(message) {
    errorText.textContent = message;
    errorMessage.hidden = false;
}

function hideError() {
    errorMessage.hidden = true;
}

function hideResults() {
    resultsSection.hidden = true;
    resultsContainer.innerHTML = '';
    resultsFooter.hidden = true;
    extractedReferences = [];
}

function clearAll() {
    uploadedFiles = [];
    extractedReferences = [];
    fileInput.value = '';
    updateFileList();
    hideResults();
    hideError();
    updateUI();
    showToast('Cleared all');
}

// =============================================================================
// Drag and Drop
// =============================================================================

dropZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropZone.classList.add('drag-over');
});

dropZone.addEventListener('dragleave', (e) => {
    e.preventDefault();
    dropZone.classList.remove('drag-over');
});

dropZone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropZone.classList.remove('drag-over');
    
    if (e.dataTransfer.files.length > 0) {
        handleFiles(e.dataTransfer.files);
    }
});

dropZone.addEventListener('click', (e) => {
    if (e.target.tagName !== 'LABEL' && e.target.tagName !== 'INPUT') {
        fileInput.click();
    }
});

fileInput.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
        handleFiles(e.target.files);
        fileInput.value = '';
    }
});

// =============================================================================
// Form Events
// =============================================================================

extractBtn.addEventListener('click', extractReferences);
clearBtn.addEventListener('click', clearAll);

// =============================================================================
// API Communication
// =============================================================================

async function extractReferences() {
    if (uploadedFiles.length === 0) {
        return;
    }
    
    setLoading(true);
    hideError();
    hideResults();
    
    try {
        const formData = new FormData();
        uploadedFiles.forEach(file => {
            formData.append('files', file);
        });
        
        const response = await fetch(`${API_URL}/extract`, {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.detail || `Server error: ${response.status}`);
        }
        
        const data = await response.json();
        extractedReferences = data.references;
        displayResults(extractedReferences);
        
        if (extractedReferences.length > 0) {
            showToast(`Found ${extractedReferences.length} reference${extractedReferences.length > 1 ? 's' : ''}`);
        }
        
    } catch (error) {
        if (error.message === 'Failed to fetch') {
            showError('Cannot connect to server. The backend service may be starting up - please try again in a moment.');
        } else {
            showError(error.message || 'An error occurred while processing your request.');
        }
    } finally {
        setLoading(false);
    }
}

// =============================================================================
// Results Display
// =============================================================================

function displayResults(references) {
    resultsSection.hidden = false;
    
    if (references.length === 0) {
        resultsCount.textContent = '0 found';
        resultsContainer.innerHTML = `
            <div class="no-results">
                <div class="no-results-icon">🔍</div>
                <p><strong>No references found</strong></p>
                <p>Check that your documents contain citations.</p>
            </div>
        `;
        resultsFooter.hidden = true;
        return;
    }
    
    resultsCount.textContent = `${references.length} found`;
    
    resultsContainer.innerHTML = references.map((ref, index) => `
        <div class="reference-item">
            <span class="reference-number">${index + 1}</span>
            <span class="reference-text">${escapeHtml(ref)}</span>
            <button class="reference-copy" data-ref="${escapeHtml(ref)}" title="Copy reference">
                <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
                    <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1-2 2v1"></path>
                </svg>
            </button>
        </div>
    `).join('');
    
    resultsFooter.hidden = false;
    
    // Add individual copy handlers
    resultsContainer.querySelectorAll('.reference-copy').forEach(btn => {
        btn.addEventListener('click', async (e) => {
            const ref = e.currentTarget.dataset.ref;
            await copyToClipboard(ref);
            showToast('Reference copied!');
        });
    });
}

// =============================================================================
// Export Functions
// =============================================================================

async function copyToClipboard(text) {
    try {
        await navigator.clipboard.writeText(text);
        return true;
    } catch (err) {
        console.error('Failed to copy:', err);
        return false;
    }
}

copyBtn.addEventListener('click', async () => {
    const text = extractedReferences.join('\n');
    const success = await copyToClipboard(text);
    
    if (success) {
        showToast('All references copied to clipboard!');
    } else {
        showError('Failed to copy to clipboard');
    }
});

downloadBtn.addEventListener('click', () => {
    const text = extractedReferences.join('\n');
    const blob = new Blob([text], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    
    const a = document.createElement('a');
    a.href = url;
    a.download = `references_${new Date().toISOString().slice(0, 10)}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    
    showToast('References downloaded!');
});

// =============================================================================
// Initialize
// =============================================================================

updateUI();