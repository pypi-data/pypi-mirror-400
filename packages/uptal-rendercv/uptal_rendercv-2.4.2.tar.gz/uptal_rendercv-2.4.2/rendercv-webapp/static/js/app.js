// Global variables
let cvData = {
    cv: {
        name: "",
        label: "",
        location: "",
        email: "",
        phone: "",
        website: "",
        social_networks: [],
        sections: {}
    },
    design: {
        theme: "classic",
        color: "blue"
    }
};

let updateTimeout;
let sessionId = document.getElementById('sessionId').value;

// Initialize the app
document.addEventListener('DOMContentLoaded', function() {
    loadFromLocalStorage();
    initializeEventListeners();
    if (cvData.cv.name) {
        updateCV();
    }
});

// Initialize event listeners
function initializeEventListeners() {
    // Listen for changes in form inputs
    document.querySelectorAll('#cvForm input, #cvForm select, #cvForm textarea').forEach(element => {
        element.addEventListener('input', debounceUpdate);
        element.addEventListener('change', debounceUpdate);
    });

    // Template selector change
    document.getElementById('sectionTemplate').addEventListener('change', function() {
        const entryTypeDiv = document.getElementById('entryTypeDiv');
        if (this.value === 'custom') {
            entryTypeDiv.style.display = 'block';
        } else {
            entryTypeDiv.style.display = 'none';
        }
    });
}

// Debounce function to prevent too many API calls
function debounceUpdate() {
    clearTimeout(updateTimeout);
    updateTimeout = setTimeout(updateCV, 500);
}

// Update CV data and generate PDF
function updateCV() {
    // Collect form data
    collectFormData();
    
    // Save to localStorage
    saveToLocalStorage();
    
    // Show loading spinner
    document.getElementById('loadingSpinner').style.display = 'block';
    document.getElementById('pdfViewer').style.display = 'none';
    document.getElementById('errorMessage').style.display = 'none';
    
    // Send to server
    fetch('/api/render', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            cv_data: cvData,
            session_id: sessionId
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Display PDF
            displayPDF(data.pdf_url);
        } else {
            showError(data.error || 'Failed to generate PDF');
        }
    })
    .catch(error => {
        showError('Network error: ' + error.message);
    });
}

// Collect form data
function collectFormData() {
    // Personal information
    cvData.cv.name = document.getElementById('name').value;
    cvData.cv.label = document.getElementById('label').value;
    cvData.cv.email = document.getElementById('email').value;
    cvData.cv.phone = document.getElementById('phone').value;
    cvData.cv.location = document.getElementById('location').value;
    cvData.cv.website = document.getElementById('website').value;
    
    // Theme
    cvData.design.theme = document.getElementById('theme').value;
    cvData.design.color = document.getElementById('color').value;
    
    // Social networks
    cvData.cv.social_networks = collectSocialNetworks();
    
    // Sections
    cvData.cv.sections = collectSections();
}

// Collect social networks
function collectSocialNetworks() {
    const networks = [];
    document.querySelectorAll('.social-network-item').forEach(item => {
        const network = item.querySelector('.network-select').value;
        const username = item.querySelector('.username-input').value;
        if (network && username) {
            networks.push({ network, username });
        }
    });
    return networks;
}

// Collect sections
function collectSections() {
    const sections = {};
    document.querySelectorAll('.cv-section').forEach(section => {
        const sectionName = section.dataset.sectionName;
        const entries = [];
        
        section.querySelectorAll('.section-entry').forEach(entry => {
            const entryData = collectEntryData(entry, section.dataset.entryType);
            if (entryData) {
                entries.push(entryData);
            }
        });
        
        if (entries.length > 0) {
            sections[sectionName] = entries;
        }
    });
    return sections;
}

// Collect entry data based on type
function collectEntryData(entryElement, entryType) {
    const data = {};
    
    // Collect all input fields in the entry
    entryElement.querySelectorAll('input, textarea, select').forEach(field => {
        const fieldName = field.dataset.field;
        if (fieldName) {
            const value = field.value.trim();
            if (value) {
                // Handle highlights as array
                if (fieldName === 'highlights') {
                    data[fieldName] = value.split('\n').filter(h => h.trim());
                } else {
                    data[fieldName] = value;
                }
            }
        }
    });
    
    return Object.keys(data).length > 0 ? data : null;
}

// Display PDF
function displayPDF(pdfUrl) {
    const pdfViewer = document.getElementById('pdfViewer');
    pdfViewer.src = pdfUrl;
    pdfViewer.style.display = 'block';
    document.getElementById('loadingSpinner').style.display = 'none';
}

// Show error message
function showError(message) {
    const errorDiv = document.getElementById('errorMessage');
    errorDiv.textContent = 'Error: ' + message;
    errorDiv.style.display = 'block';
    document.getElementById('loadingSpinner').style.display = 'none';
}

// Add social network
function addSocialNetwork() {
    const container = document.getElementById('socialNetworks');
    const index = container.children.length;
    
    const html = `
        <div class="social-network-item">
            <select class="form-select network-select">
                <option value="">Select Network</option>
                <option value="LinkedIn">LinkedIn</option>
                <option value="GitHub">GitHub</option>
                <option value="Twitter">Twitter</option>
                <option value="Facebook">Facebook</option>
                <option value="Instagram">Instagram</option>
            </select>
            <input type="text" class="form-control username-input" placeholder="Username">
            <button type="button" class="btn btn-danger btn-sm" onclick="removeSocialNetwork(this)">
                <i class="bi bi-trash"></i>
            </button>
        </div>
    `;
    
    container.insertAdjacentHTML('beforeend', html);
    
    // Add event listeners to new elements
    const newItem = container.lastElementChild;
    newItem.querySelectorAll('input, select').forEach(el => {
        el.addEventListener('change', debounceUpdate);
    });
}

// Remove social network
function removeSocialNetwork(button) {
    button.closest('.social-network-item').remove();
    debounceUpdate();
}

// Show add section modal
function showAddSectionModal() {
    const modal = new bootstrap.Modal(document.getElementById('addSectionModal'));
    modal.show();
}

// Add section
function addSection() {
    const sectionName = document.getElementById('sectionName').value.trim();
    const template = document.getElementById('sectionTemplate').value;
    const entryType = template === 'custom' ? 
        document.getElementById('entryType').value : 
        getSectionEntryType(template);
    
    if (!sectionName) {
        alert('Please enter a section name');
        return;
    }
    
    // Create section HTML
    const sectionHtml = createSectionHtml(sectionName, entryType);
    document.getElementById('sections').insertAdjacentHTML('beforeend', sectionHtml);
    
    // Close modal
    bootstrap.Modal.getInstance(document.getElementById('addSectionModal')).hide();
    
    // Clear modal inputs
    document.getElementById('sectionName').value = '';
    document.getElementById('sectionTemplate').value = 'experience';
    
    debounceUpdate();
}

// Get entry type for section template
function getSectionEntryType(template) {
    const templates = {
        'experience': 'ExperienceEntry',
        'education': 'EducationEntry',
        'skills': 'BulletEntry',
        'projects': 'NormalEntry',
        'publications': 'PublicationEntry'
    };
    return templates[template] || 'TextEntry';
}

// Create section HTML
function createSectionHtml(sectionName, entryType) {
    return `
        <div class="cv-section mb-3" data-section-name="${sectionName}" data-entry-type="${entryType}">
            <div class="section-header d-flex justify-content-between align-items-center">
                <h6 class="mb-0">${sectionName}</h6>
                <div class="section-controls">
                    <button type="button" class="btn btn-sm btn-primary" onclick="addEntry('${sectionName}', '${entryType}')">
                        <i class="bi bi-plus"></i> Add Entry
                    </button>
                    <button type="button" class="btn btn-sm btn-danger" onclick="removeSection(this)">
                        <i class="bi bi-trash"></i>
                    </button>
                </div>
            </div>
            <div class="section-entries mt-2">
                <!-- Entries will be added here -->
            </div>
        </div>
    `;
}

// Add entry to section
function addEntry(sectionName, entryType) {
    const section = document.querySelector(`[data-section-name="${sectionName}"]`);
    const entriesContainer = section.querySelector('.section-entries');
    const entryHtml = createEntryHtml(entryType);
    
    entriesContainer.insertAdjacentHTML('beforeend', entryHtml);
    
    // Add event listeners to new entry
    const newEntry = entriesContainer.lastElementChild;
    newEntry.querySelectorAll('input, textarea, select').forEach(el => {
        el.addEventListener('input', debounceUpdate);
        el.addEventListener('change', debounceUpdate);
    });
}

// Create entry HTML based on type
function createEntryHtml(entryType) {
    let fields = '';
    
    switch(entryType) {
        case 'ExperienceEntry':
            fields = `
                <input type="text" class="form-control mb-2" data-field="company" placeholder="Company">
                <input type="text" class="form-control mb-2" data-field="position" placeholder="Position">
                <input type="text" class="form-control mb-2" data-field="location" placeholder="Location">
                <div class="row">
                    <div class="col-6">
                        <input type="text" class="form-control mb-2" data-field="start_date" placeholder="Start Date (YYYY-MM)">
                    </div>
                    <div class="col-6">
                        <input type="text" class="form-control mb-2" data-field="end_date" placeholder="End Date or 'present'">
                    </div>
                </div>
                <textarea class="form-control mb-2" data-field="highlights" rows="3" placeholder="Highlights (one per line)"></textarea>
            `;
            break;
            
        case 'EducationEntry':
            fields = `
                <input type="text" class="form-control mb-2" data-field="institution" placeholder="Institution">
                <input type="text" class="form-control mb-2" data-field="area" placeholder="Field of Study">
                <input type="text" class="form-control mb-2" data-field="degree" placeholder="Degree">
                <input type="text" class="form-control mb-2" data-field="location" placeholder="Location">
                <div class="row">
                    <div class="col-6">
                        <input type="text" class="form-control mb-2" data-field="start_date" placeholder="Start Date (YYYY-MM)">
                    </div>
                    <div class="col-6">
                        <input type="text" class="form-control mb-2" data-field="end_date" placeholder="End Date">
                    </div>
                </div>
                <textarea class="form-control mb-2" data-field="highlights" rows="2" placeholder="Highlights (one per line)"></textarea>
            `;
            break;
            
        case 'BulletEntry':
            fields = `
                <input type="text" class="form-control mb-2" data-field="bullet" placeholder="Bullet point">
            `;
            break;
            
        case 'NormalEntry':
            fields = `
                <input type="text" class="form-control mb-2" data-field="name" placeholder="Name">
                <input type="text" class="form-control mb-2" data-field="location" placeholder="Location">
                <textarea class="form-control mb-2" data-field="summary" rows="2" placeholder="Summary"></textarea>
                <textarea class="form-control mb-2" data-field="highlights" rows="2" placeholder="Highlights (one per line)"></textarea>
            `;
            break;
            
        case 'PublicationEntry':
            fields = `
                <input type="text" class="form-control mb-2" data-field="title" placeholder="Title">
                <input type="text" class="form-control mb-2" data-field="authors" placeholder="Authors">
                <input type="text" class="form-control mb-2" data-field="journal" placeholder="Journal">
                <input type="text" class="form-control mb-2" data-field="date" placeholder="Date">
                <input type="text" class="form-control mb-2" data-field="doi" placeholder="DOI (optional)">
            `;
            break;
            
        case 'OneLineEntry':
            fields = `
                <input type="text" class="form-control mb-2" data-field="label" placeholder="Label">
                <input type="text" class="form-control mb-2" data-field="details" placeholder="Details">
            `;
            break;
            
        default: // TextEntry
            fields = `
                <textarea class="form-control mb-2" data-field="text" rows="2" placeholder="Text content"></textarea>
            `;
    }
    
    return `
        <div class="section-entry">
            ${fields}
            <div class="entry-controls">
                <button type="button" class="btn btn-sm btn-danger" onclick="removeEntry(this)">
                    <i class="bi bi-trash"></i> Remove
                </button>
            </div>
        </div>
    `;
}

// Remove section
function removeSection(button) {
    button.closest('.cv-section').remove();
    debounceUpdate();
}

// Remove entry
function removeEntry(button) {
    button.closest('.section-entry').remove();
    debounceUpdate();
}

// Load sample CV
function loadSampleCV() {
    fetch('/api/sample-cv')
        .then(response => response.json())
        .then(data => {
            cvData = data;
            populateForm();
            updateCV();
        })
        .catch(error => {
            alert('Failed to load sample CV: ' + error.message);
        });
}

// Populate form from CV data
function populateForm() {
    // Personal information
    document.getElementById('name').value = cvData.cv.name || '';
    document.getElementById('label').value = cvData.cv.label || '';
    document.getElementById('email').value = cvData.cv.email || '';
    document.getElementById('phone').value = cvData.cv.phone || '';
    document.getElementById('location').value = cvData.cv.location || '';
    document.getElementById('website').value = cvData.cv.website || '';
    
    // Theme
    document.getElementById('theme').value = cvData.design.theme || 'classic';
    document.getElementById('color').value = cvData.design.color || 'blue';
    
    // Social networks
    const socialContainer = document.getElementById('socialNetworks');
    socialContainer.innerHTML = '';
    if (cvData.cv.social_networks) {
        cvData.cv.social_networks.forEach(network => {
            addSocialNetwork();
            const lastItem = socialContainer.lastElementChild;
            lastItem.querySelector('.network-select').value = network.network;
            lastItem.querySelector('.username-input').value = network.username;
        });
    }
    
    // Sections
    const sectionsContainer = document.getElementById('sections');
    sectionsContainer.innerHTML = '';
    if (cvData.cv.sections) {
        Object.entries(cvData.cv.sections).forEach(([sectionName, entries]) => {
            // Determine entry type from first entry
            const entryType = detectEntryType(entries[0]);
            const sectionHtml = createSectionHtml(sectionName, entryType);
            sectionsContainer.insertAdjacentHTML('beforeend', sectionHtml);
            
            // Add entries
            entries.forEach(entry => {
                addEntry(sectionName, entryType);
                const section = document.querySelector(`[data-section-name="${sectionName}"]`);
                const lastEntry = section.querySelector('.section-entries').lastElementChild;
                populateEntry(lastEntry, entry);
            });
        });
    }
}

// Detect entry type from entry data
function detectEntryType(entry) {
    if (!entry) return 'TextEntry';
    
    if (entry.company && entry.position) return 'ExperienceEntry';
    if (entry.institution && entry.area) return 'EducationEntry';
    if (entry.title && entry.authors) return 'PublicationEntry';
    if (entry.bullet) return 'BulletEntry';
    if (entry.label && entry.details) return 'OneLineEntry';
    if (entry.name) return 'NormalEntry';
    
    return 'TextEntry';
}

// Populate entry fields
function populateEntry(entryElement, entryData) {
    Object.entries(entryData).forEach(([field, value]) => {
        const input = entryElement.querySelector(`[data-field="${field}"]`);
        if (input) {
            if (field === 'highlights' && Array.isArray(value)) {
                input.value = value.join('\n');
            } else {
                input.value = value;
            }
        }
    });
}

// Import YAML
function importYAML() {
    document.getElementById('fileInput').click();
}

// Handle file import
function handleFileImport(event) {
    const file = event.target.files[0];
    if (!file) return;
    
    const formData = new FormData();
    formData.append('file', file);
    
    fetch('/api/import', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            cvData = data.cv_data;
            populateForm();
            updateCV();
            alert('CV imported successfully!');
        } else {
            alert('Import failed: ' + data.error);
        }
    })
    .catch(error => {
        alert('Import failed: ' + error.message);
    });
    
    // Clear file input
    event.target.value = '';
}

// Export CV
function exportCV(format) {
    if (format === 'pdf') {
        // Download current PDF
        const pdfViewer = document.getElementById('pdfViewer');
        if (pdfViewer.src) {
            window.open(pdfViewer.src, '_blank');
        } else {
            alert('Please generate a PDF first');
        }
    } else {
        // Export in other formats
        fetch(`/api/export/${format}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ cv_data: cvData })
        })
        .then(response => {
            if (format === 'json') {
                return response.json();
            } else {
                return response.blob();
            }
        })
        .then(data => {
            if (format === 'json') {
                // Download JSON
                const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
                downloadBlob(blob, 'cv.json');
            } else {
                // Download file
                const filename = format === 'yaml' ? 'cv.yaml' : 'cv.md';
                downloadBlob(data, filename);
            }
        })
        .catch(error => {
            alert('Export failed: ' + error.message);
        });
    }
}

// Download blob as file
function downloadBlob(blob, filename) {
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
}

// Save to localStorage
function saveToLocalStorage() {
    try {
        localStorage.setItem('rendercv_data', JSON.stringify(cvData));
    } catch (e) {
        console.error('Failed to save to localStorage:', e);
    }
}

// Load from localStorage
function loadFromLocalStorage() {
    try {
        const saved = localStorage.getItem('rendercv_data');
        if (saved) {
            cvData = JSON.parse(saved);
            populateForm();
        }
    } catch (e) {
        console.error('Failed to load from localStorage:', e);
    }
}

// Auto-save every 30 seconds
setInterval(saveToLocalStorage, 30000);