/**
 * Template Management System
 * Handles PDF uploads, text extraction, and template processing
 */

class TemplateManager {
    constructor() {
        this.pdfjsLib = null;
        this.initializePDFJS();
        this.setupEventListeners();
    }

    /**
     * Initialize PDF.js library for PDF processing
     */
    async initializePDFJS() {
        try {
            // Load PDF.js from CDN
            const script = document.createElement('script');
            script.src = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.min.js';
            script.onload = () => {
                this.pdfjsLib = window.pdfjsLib;
                this.pdfjsLib.GlobalWorkerOptions.workerSrc = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js';
                console.log('PDF.js loaded successfully');
            };
            document.head.appendChild(script);
        } catch (error) {
            console.error('Failed to load PDF.js:', error);
        }
    }

    /**
     * Setup event listeners for template functionality
     */
    setupEventListeners() {
        // PDF file input change
        document.getElementById('pdfFile')?.addEventListener('change', (e) => {
            this.handlePDFFileSelect(e.target.files[0]);
        });

        // Drag and drop for PDF upload
        const pdfUploadArea = document.getElementById('pdfUploadArea');
        if (pdfUploadArea) {
            pdfUploadArea.addEventListener('dragover', (e) => {
                e.preventDefault();
                pdfUploadArea.classList.add('dragover');
            });

            pdfUploadArea.addEventListener('dragleave', (e) => {
                e.preventDefault();
                pdfUploadArea.classList.remove('dragover');
            });

            pdfUploadArea.addEventListener('drop', (e) => {
                e.preventDefault();
                pdfUploadArea.classList.remove('dragover');
                const files = e.dataTransfer.files;
                if (files.length > 0 && files[0].type === 'application/pdf') {
                    this.handlePDFFileSelect(files[0]);
                }
            });

            // Click to browse
            pdfUploadArea.addEventListener('click', () => {
                document.getElementById('pdfFile').click();
            });
        }

        // Edit extracted content button
        document.getElementById('editExtractedContent')?.addEventListener('click', () => {
            this.toggleContentEdit();
        });

        // Auto-detect variables button
        document.getElementById('detectVariables')?.addEventListener('click', () => {
            this.autoDetectVariables();
        });

        // Upload template button
        document.getElementById('uploadTemplateBtn')?.addEventListener('click', () => {
            this.uploadTemplate();
        });

        // Tab switching
        document.querySelectorAll('[data-bs-toggle="tab"]').forEach(tab => {
            tab.addEventListener('shown.bs.tab', (e) => {
                this.handleTabSwitch(e);
            });
        });
    }

    /**
     * Handle PDF file selection
     */
    async handlePDFFileSelect(file) {
        if (!file) return;

        // Validate file type
        if (file.type !== 'application/pdf') {
            this.showAlert('Please select a valid PDF file.', 'error');
            return;
        }

        // Validate file size (10MB limit)
        if (file.size > 10 * 1024 * 1024) {
            this.showAlert('File size must be less than 10MB.', 'error');
            return;
        }

        try {
            this.showLoading('Processing PDF...');
            
            // Extract text from PDF
            const extractedText = await this.extractTextFromPDF(file);
            
            // Auto-fill template name from filename
            const templateName = file.name.replace('.pdf', '').replace(/[^a-zA-Z0-9\s]/g, ' ').trim();
            document.getElementById('pdfTemplateName').value = templateName;
            
            // Show extracted content
            document.getElementById('pdfExtractedContent').value = extractedText;
            document.getElementById('pdfPreviewSection').style.display = 'block';
            
            // Auto-detect variables
            this.autoDetectVariables();
            
            this.hideLoading();
            this.showAlert('PDF processed successfully! You can now edit the content and variables.', 'success');
            
        } catch (error) {
            this.hideLoading();
            console.error('PDF processing error:', error);
            this.showAlert('Failed to process PDF. Please try again or use text input instead.', 'error');
        }
    }

    /**
     * Extract text content from PDF file
     */
    async extractTextFromPDF(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            
            reader.onload = async (e) => {
                try {
                    const arrayBuffer = e.target.result;
                    const pdf = await this.pdfjsLib.getDocument({ data: arrayBuffer }).promise;
                    
                    let fullText = '';
                    
                    // Extract text from all pages
                    for (let pageNum = 1; pageNum <= pdf.numPages; pageNum++) {
                        const page = await pdf.getPage(pageNum);
                        const textContent = await page.getTextContent();
                        
                        const pageText = textContent.items
                            .map(item => item.str)
                            .join(' ');
                        
                        fullText += pageText + '\n\n';
                    }
                    
                    // Clean up the extracted text
                    const cleanedText = this.cleanExtractedText(fullText);
                    resolve(cleanedText);
                    
                } catch (error) {
                    reject(error);
                }
            };
            
            reader.onerror = () => reject(new Error('Failed to read file'));
            reader.readAsArrayBuffer(file);
        });
    }

    /**
     * Clean and format extracted text
     */
    cleanExtractedText(text) {
        return text
            .replace(/\s+/g, ' ') // Replace multiple spaces with single space
            .replace(/\n\s*\n/g, '\n\n') // Clean up multiple newlines
            .trim();
    }

    /**
     * Toggle content editing mode
     */
    toggleContentEdit() {
        const textarea = document.getElementById('pdfExtractedContent');
        const button = document.getElementById('editExtractedContent');
        
        if (textarea.readOnly) {
            textarea.readOnly = false;
            textarea.classList.remove('form-control-plaintext');
            button.innerHTML = '<i class="fas fa-save me-1"></i>Save Content';
            button.classList.remove('btn-outline-secondary');
            button.classList.add('btn-outline-success');
        } else {
            textarea.readOnly = true;
            textarea.classList.add('form-control-plaintext');
            button.innerHTML = '<i class="fas fa-edit me-1"></i>Edit Content';
            button.classList.remove('btn-outline-success');
            button.classList.add('btn-outline-secondary');
        }
    }

    /**
     * Auto-detect variables in the extracted content
     */
    autoDetectVariables() {
        const content = document.getElementById('pdfExtractedContent').value;
        const variables = this.extractVariablesFromContent(content);
        
        if (variables.length > 0) {
            document.getElementById('pdfRequiredVariables').value = variables.join(', ');
            this.showAlert(`Auto-detected ${variables.length} potential variables.`, 'info');
        } else {
            this.showAlert('No variables detected. You may need to manually add them.', 'warning');
        }
    }

    /**
     * Extract potential variables from content
     */
    extractVariablesFromContent(content) {
        // Common legal document patterns
        const patterns = [
            /\[([A-Z_][A-Z0-9_]*)\]/g, // [VARIABLE_NAME]
            /\{([A-Z_][A-Z0-9_]*)\}/g, // {VARIABLE_NAME}
            /\{\{([A-Z_][A-Z0-9_]*)\}\}/g, // {{VARIABLE_NAME}}
            /__([A-Z_][A-Z0-9_]*)__/g, // __VARIABLE_NAME__
        ];
        
        const variables = new Set();
        
        patterns.forEach(pattern => {
            let match;
            while ((match = pattern.exec(content)) !== null) {
                variables.add(match[1]);
            }
        });
        
        // Also detect common legal terms that might be variables
        const commonLegalTerms = [
            'CLIENT_NAME', 'COMPANY_NAME', 'LAWYER_NAME', 'LAW_FIRM_NAME',
            'CASE_NUMBER', 'CASE_DESCRIPTION', 'COURT_NAME', 'JUDGE_NAME',
            'DATE', 'SIGNATURE_DATE', 'EFFECTIVE_DATE', 'EXPIRY_DATE',
            'ADDRESS', 'PHONE', 'EMAIL', 'FAX', 'WEBSITE',
            'AMOUNT', 'CURRENCY', 'PERCENTAGE', 'DURATION'
        ];
        
        commonLegalTerms.forEach(term => {
            if (content.toUpperCase().includes(term)) {
                variables.add(term);
            }
        });
        
        return Array.from(variables).sort();
    }

    /**
     * Handle tab switching
     */
    handleTabSwitch(event) {
        const targetId = event.target.getAttribute('data-bs-target');
        
        // Reset forms when switching tabs
        if (targetId === '#text-upload') {
            document.getElementById('templateUploadForm').reset();
        } else if (targetId === '#pdf-upload') {
            document.getElementById('pdfTemplateUploadForm').reset();
            document.getElementById('pdfPreviewSection').style.display = 'none';
        }
    }

    /**
     * Upload template (both text and PDF)
     */
    uploadTemplate() {
        const activeTab = document.querySelector('.nav-link.active');
        const isPDFTab = activeTab.getAttribute('data-bs-target') === '#pdf-upload';
        
        if (isPDFTab) {
            this.uploadPDFTemplate();
        } else {
            this.uploadTextTemplate();
        }
    }

    /**
     * Upload text-based template
     */
    uploadTextTemplate() {
        const form = document.getElementById('templateUploadForm');
        const formData = new FormData(form);
        
        const template = {
            name: document.getElementById('templateName').value,
            description: document.getElementById('templateDescription').value,
            content: document.getElementById('templateContent').value,
            variables: document.getElementById('requiredVariables').value,
            category: document.getElementById('templateCategory').value,
            type: 'text',
            created: new Date().toISOString()
        };
        
        this.saveTemplate(template);
    }

    /**
     * Upload PDF-based template
     */
    uploadPDFTemplate() {
        const template = {
            name: document.getElementById('pdfTemplateName').value,
            description: document.getElementById('pdfTemplateDescription').value,
            content: document.getElementById('pdfExtractedContent').value,
            variables: document.getElementById('pdfRequiredVariables').value,
            category: document.getElementById('pdfTemplateCategory').value,
            type: 'pdf',
            created: new Date().toISOString()
        };
        
        this.saveTemplate(template);
    }

    /**
     * Save template to storage
     */
    saveTemplate(template) {
        try {
            // Validate required fields
            if (!template.name || !template.content) {
                this.showAlert('Template name and content are required.', 'error');
                return;
            }
            
            // Get existing templates
            const existingTemplates = JSON.parse(localStorage.getItem('customTemplates') || '[]');
            
            // Check for duplicate names
            if (existingTemplates.some(t => t.name === template.name)) {
                this.showAlert('A template with this name already exists.', 'error');
                return;
            }
            
            // Add new template
            existingTemplates.push(template);
            localStorage.setItem('customTemplates', JSON.stringify(existingTemplates));
            
            // Close modal and refresh
            const modal = bootstrap.Modal.getInstance(document.getElementById('templateUploadModal'));
            modal.hide();
            
            this.showAlert('Template uploaded successfully!', 'success');
            
            // Refresh the page to show new template
            setTimeout(() => {
                location.reload();
            }, 1000);
            
        } catch (error) {
            console.error('Error saving template:', error);
            this.showAlert('Failed to save template. Please try again.', 'error');
        }
    }

    /**
     * Show loading indicator
     */
    showLoading(message) {
        // Create loading overlay if it doesn't exist
        let loadingOverlay = document.getElementById('loadingOverlay');
        if (!loadingOverlay) {
            loadingOverlay = document.createElement('div');
            loadingOverlay.id = 'loadingOverlay';
            loadingOverlay.innerHTML = `
                <div class="loading-content">
                    <div class="spinner-border text-primary" role="status">
                        <span class="visually-hidden">Loading...</span>
                    </div>
                    <p class="mt-2">${message}</p>
                </div>
            `;
            loadingOverlay.style.cssText = `
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(0,0,0,0.5);
                display: flex;
                align-items: center;
                justify-content: center;
                z-index: 9999;
            `;
            loadingOverlay.querySelector('.loading-content').style.cssText = `
                background: white;
                padding: 30px;
                border-radius: 10px;
                text-align: center;
            `;
            document.body.appendChild(loadingOverlay);
        } else {
            loadingOverlay.style.display = 'flex';
            loadingOverlay.querySelector('p').textContent = message;
        }
    }

    /**
     * Hide loading indicator
     */
    hideLoading() {
        const loadingOverlay = document.getElementById('loadingOverlay');
        if (loadingOverlay) {
            loadingOverlay.style.display = 'none';
        }
    }

    /**
     * Show alert message
     */
    showAlert(message, type = 'info') {
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type === 'error' ? 'danger' : type} alert-dismissible fade show`;
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        // Insert at the top of the modal body
        const modalBody = document.querySelector('.modal-body');
        modalBody.insertBefore(alertDiv, modalBody.firstChild);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (alertDiv.parentNode) {
                alertDiv.remove();
            }
        }, 5000);
    }
}

// Initialize template manager when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.templateManager = new TemplateManager();
});

// Export for global access
window.TemplateManager = TemplateManager; 