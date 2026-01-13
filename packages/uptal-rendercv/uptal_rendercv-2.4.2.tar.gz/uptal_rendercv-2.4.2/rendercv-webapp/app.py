from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
import rendercv.api.functions as rcv_api
from pathlib import Path
import json
import tempfile
import os
from datetime import datetime
import uuid

app = Flask(__name__)
CORS(app)

# Configure upload folder for temporary PDFs
UPLOAD_FOLDER = Path('static/pdf')
UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Store sessions in memory (for production, use Redis or database)
sessions = {}

# Default CV data structure
DEFAULT_CV_DATA = {
    "cv": {
        "name": "",
        "label": "",
        "location": "",
        "email": "",
        "phone": "",
        "website": "",
        "social_networks": [],
        "sections": {}
    },
    "design": {
        "theme": "classic",
        "color": "blue",
        "page_size": "letterpaper",
        "text_alignment": "justified",
        "header_alignment": "center",
        "font": "Source Sans 3",
        "font_size": "10pt",
        "page_numbering_style": "Page NAME of TOTAL_PAGES"
    },
    "locale": "en"
}

# Available themes
THEMES = ["classic", "sb2nov", "moderncv", "engineeringresumes", "engineeringclassic"]

# Entry types with their required fields
ENTRY_TYPES = {
    "TextEntry": [],
    "OneLineEntry": ["label", "details"],
    "BulletEntry": ["bullet"],
    "NumberedEntry": ["number"],
    "ReversedNumberedEntry": ["reversed_number"],
    "NormalEntry": ["name"],
    "ExperienceEntry": ["company", "position"],
    "EducationEntry": ["institution", "area"],
    "PublicationEntry": ["title", "authors"]
}

# Section templates
SECTION_TEMPLATES = {
    "experience": {
        "entry_type": "ExperienceEntry",
        "entries": []
    },
    "education": {
        "entry_type": "EducationEntry",
        "entries": []
    },
    "publications": {
        "entry_type": "PublicationEntry",
        "entries": []
    },
    "skills": {
        "entry_type": "BulletEntry",
        "entries": []
    },
    "projects": {
        "entry_type": "NormalEntry",
        "entries": []
    }
}

@app.route('/')
def index():
    """Render the main application page."""
    session_id = str(uuid.uuid4())
    sessions[session_id] = {"cv_data": DEFAULT_CV_DATA.copy()}
    return render_template('index.html', session_id=session_id)

@app.route('/api/render', methods=['POST'])
def render_cv():
    """Generate PDF from CV data."""
    try:
        data = request.json
        cv_data = data.get('cv_data', DEFAULT_CV_DATA)
        session_id = data.get('session_id', str(uuid.uuid4()))
        
        # Store in session
        if session_id not in sessions:
            sessions[session_id] = {}
        sessions[session_id]['cv_data'] = cv_data
        
        # Generate unique filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"cv_{session_id[:8]}_{timestamp}.pdf"
        output_path = Path(app.config['UPLOAD_FOLDER']) / filename
        
        # Generate PDF using RenderCV API
        errors = rcv_api.create_a_pdf_from_a_python_dictionary(
            cv_data,
            output_path
        )
        
        if errors:
            return jsonify({
                'success': False,
                'errors': str(errors)
            }), 400
        
        # Clean up old PDFs (keep only last 10)
        cleanup_old_pdfs()
        
        return jsonify({
            'success': True,
            'pdf_url': f'/static/pdf/{filename}',
            'filename': filename
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/validate', methods=['POST'])
def validate_cv():
    """Validate CV data structure."""
    try:
        cv_data = request.json.get('cv_data', {})
        
        # Use RenderCV's validation
        data_model = rcv_api.read_a_python_dictionary_and_return_a_data_model(cv_data)
        
        if data_model is None:
            return jsonify({
                'valid': False,
                'errors': ['Invalid CV data structure']
            }), 400
        
        return jsonify({
            'valid': True,
            'message': 'CV data is valid'
        })
        
    except Exception as e:
        return jsonify({
            'valid': False,
            'errors': [str(e)]
        }), 400

@app.route('/api/themes', methods=['GET'])
def get_themes():
    """Get available themes."""
    return jsonify({
        'themes': THEMES,
        'default': 'classic'
    })

@app.route('/api/entry-types', methods=['GET'])
def get_entry_types():
    """Get available entry types with their required fields."""
    return jsonify(ENTRY_TYPES)

@app.route('/api/section-templates', methods=['GET'])
def get_section_templates():
    """Get section templates."""
    return jsonify(SECTION_TEMPLATES)

@app.route('/api/export/<format>', methods=['POST'])
def export_cv(format):
    """Export CV in different formats."""
    try:
        cv_data = request.json.get('cv_data', DEFAULT_CV_DATA)
        
        if format == 'yaml':
            import ruamel.yaml
            yaml = ruamel.yaml.YAML()
            
            # Create temporary file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
                yaml.dump(cv_data, f)
                temp_path = f.name
            
            return send_file(
                temp_path,
                as_attachment=True,
                download_name='cv.yaml',
                mimetype='text/yaml'
            )
            
        elif format == 'json':
            return jsonify(cv_data)
            
        elif format == 'markdown':
            # Generate Markdown using RenderCV API
            with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
                errors = rcv_api.create_a_markdown_file_from_a_python_dictionary(
                    cv_data,
                    Path(f.name)
                )
                if errors:
                    return jsonify({'error': str(errors)}), 400
                    
                return send_file(
                    f.name,
                    as_attachment=True,
                    download_name='cv.md',
                    mimetype='text/markdown'
                )
        
        else:
            return jsonify({'error': 'Invalid format'}), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/import', methods=['POST'])
def import_cv():
    """Import CV from YAML file."""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
            
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
            
        if file and file.filename.endswith('.yaml'):
            # Read YAML content
            yaml_content = file.read().decode('utf-8')
            
            # Parse using RenderCV API
            data_model = rcv_api.read_a_yaml_string_and_return_a_data_model(yaml_content)
            
            if data_model is None:
                return jsonify({'error': 'Invalid YAML file'}), 400
            
            # Convert back to dictionary
            cv_data = data_model.model_dump()
            
            return jsonify({
                'success': True,
                'cv_data': cv_data
            })
        else:
            return jsonify({'error': 'Invalid file type. Only YAML files are supported.'}), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/sample-cv', methods=['GET'])
def get_sample_cv():
    """Get a sample CV for demonstration."""
    sample_cv = {
        "cv": {
            "name": "John Doe",
            "label": "Software Engineer",
            "location": "San Francisco, CA",
            "email": "john.doe@example.com",
            "phone": "+1-555-123-4567",
            "website": "https://johndoe.com",
            "social_networks": [
                {
                    "network": "LinkedIn",
                    "username": "johndoe"
                },
                {
                    "network": "GitHub",
                    "username": "johndoe"
                }
            ],
            "sections": {
                "experience": [
                    {
                        "company": "Tech Corp",
                        "position": "Senior Software Engineer",
                        "location": "San Francisco, CA",
                        "start_date": "2020-01",
                        "end_date": "present",
                        "highlights": [
                            "Led development of microservices architecture",
                            "Improved system performance by 40%",
                            "Mentored junior developers"
                        ]
                    },
                    {
                        "company": "StartupXYZ",
                        "position": "Software Engineer",
                        "location": "Palo Alto, CA",
                        "start_date": "2018-06",
                        "end_date": "2019-12",
                        "highlights": [
                            "Built RESTful APIs using Python and Flask",
                            "Implemented CI/CD pipeline",
                            "Worked on React frontend"
                        ]
                    }
                ],
                "education": [
                    {
                        "institution": "Stanford University",
                        "area": "Computer Science",
                        "degree": "BS",
                        "start_date": "2014-09",
                        "end_date": "2018-05",
                        "highlights": [
                            "GPA: 3.8/4.0",
                            "Dean's List"
                        ]
                    }
                ],
                "skills": [
                    {"bullet": "Python, JavaScript, Java, C++"},
                    {"bullet": "React, Flask, Django, Node.js"},
                    {"bullet": "AWS, Docker, Kubernetes"},
                    {"bullet": "PostgreSQL, MongoDB, Redis"}
                ]
            }
        },
        "design": {
            "theme": "classic"
        }
    }
    return jsonify(sample_cv)

def cleanup_old_pdfs():
    """Remove old PDF files, keeping only the 10 most recent."""
    try:
        pdf_files = list(Path(app.config['UPLOAD_FOLDER']).glob('*.pdf'))
        pdf_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        
        # Keep only the 10 most recent files
        for old_file in pdf_files[10:]:
            old_file.unlink()
    except Exception as e:
        print(f"Error cleaning up PDFs: {e}")

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)