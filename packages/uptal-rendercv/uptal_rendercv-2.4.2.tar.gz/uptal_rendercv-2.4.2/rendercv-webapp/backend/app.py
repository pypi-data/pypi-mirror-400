from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_cors import CORS
import rendercv.api.functions as rcv_api
from pathlib import Path
import tempfile
import os
import uuid
from datetime import datetime
import logging
import shutil
import subprocess
import sys
import re
from dotenv import load_dotenv
from services import CVService, CVServiceException

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app, origins="*")
logger = logging.getLogger(__name__)

# Initialize services
cv_service = CVService()

# Theme asset configuration
ASSETS_DIR = Path(__file__).resolve().parent / "assets"
THEME_ASSET_BASE_URL = os.getenv("THEME_ASSET_BASE_URL")

def _bool_env(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "y", "on"}


def _render_pdf_from_typst(typst_path: Path, pdf_path: Path) -> None:
    """
    Render a PDF from a Typst file.

    Default is to run the native `typst` binding in a subprocess to avoid
    long-lived RSS growth across many renders.
    """
    isolate = _bool_env("RENDER_ISOLATE_PROCESS", default=True)
    timeout_sec = int(os.getenv("RENDER_TIMEOUT_SEC", "120"))

    if not isolate:
        import rendercv.renderer.renderer as renderer

        generated_pdf_path = Path(renderer.render_a_pdf_from_typst(typst_path))
        if generated_pdf_path != pdf_path:
            generated_pdf_path.replace(pdf_path)
        return

    code = """
import sys
from pathlib import Path
import rendercv.renderer.renderer as renderer

typst_path = Path(sys.argv[1])
pdf_path = Path(sys.argv[2])
generated = Path(renderer.render_a_pdf_from_typst(typst_path))
if generated != pdf_path:
    generated.replace(pdf_path)
"""
    result = subprocess.run(
        [sys.executable, "-c", code, str(typst_path), str(pdf_path)],
        capture_output=True,
        text=True,
        timeout=timeout_sec,
    )
    if result.returncode != 0:
        stderr = (result.stderr or "").strip()
        stdout = (result.stdout or "").strip()
        details = stderr or stdout or f"exit code {result.returncode}"
        raise RuntimeError(f"Typst render failed: {details}")


def _log_memory_usage(note: str) -> None:
    if not _bool_env("LOG_MEMORY_USAGE", default=False):
        return
    try:
        import resource

        # ru_maxrss is KB on Linux, bytes on macOS; keep raw to avoid lying.
        max_rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        logger.info("memory note=%s ru_maxrss=%s", note, max_rss)
    except Exception:
        return


def _format_typst_error_context(error_text: str, typst_path: Path) -> str | None:
    if not typst_path.exists():
        return None

    matches = re.findall(r"([^\s:]+\.typ):(\d+):(\d+)", error_text)
    if not matches:
        return None

    try:
        lines = typst_path.read_text(encoding="utf-8", errors="replace").splitlines()
    except Exception:
        return None

    snippets = []
    seen = set()
    for _, line_str, col_str in matches:
        try:
            line_num = int(line_str)
            col_num = int(col_str)
        except ValueError:
            continue
        key = (line_num, col_num)
        if key in seen:
            continue
        seen.add(key)
        if line_num < 1 or line_num > len(lines):
            continue

        start = max(1, line_num - 2)
        end = min(len(lines), line_num + 2)
        snippet_lines = []
        for i in range(start, end + 1):
            marker = ">" if i == line_num else " "
            snippet_lines.append(f"{marker}{i:4d} | {lines[i - 1]}")
        if col_num > 0:
            caret_prefix = " " * (len(f">{line_num:4d} | ") + max(col_num - 1, 0))
            snippet_lines.append(f"{caret_prefix}^")
        snippets.append("\n".join(snippet_lines))

    if not snippets:
        return None

    return "Typst source context:\n" + "\n\n".join(snippets)


def _compose_typst_error_message(error_text: str, typst_path: Path) -> str:
    context = _format_typst_error_context(error_text, typst_path)
    if context:
        return f"{error_text}\n\n{context}"
    return error_text


def _escape_typst_left_bracket(value: str) -> str:
    return re.sub(r"(?<!\\)\[", r"\\[", value)


def _sanitize_cv_locations(cv_data: dict) -> None:
    cv_section = cv_data.get("cv")
    if not isinstance(cv_section, dict):
        return

    location = cv_section.get("location")
    if isinstance(location, str):
        cv_section["location"] = _escape_typst_left_bracket(location)

    sections = cv_section.get("sections")
    if not isinstance(sections, dict):
        return

    for entries in sections.values():
        if not isinstance(entries, list):
            continue
        for entry in entries:
            if not isinstance(entry, dict):
                continue
            entry_location = entry.get("location")
            if isinstance(entry_location, str):
                entry["location"] = _escape_typst_left_bracket(entry_location)


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({"status": "healthy", "service": "rendercv-backend"})

def _theme_image_url(filename: str) -> str:
    """
    Build a full URL for a theme preview image.

    Allows overriding the base URL via THEME_ASSET_BASE_URL; otherwise uses
    the current host and serves from /assets/<filename>.
    """
    if THEME_ASSET_BASE_URL:
        base = THEME_ASSET_BASE_URL.rstrip("/")
    else:
        # Force HTTPS if the host URL comes in as HTTP
        host_url = request.host_url.rstrip("/").replace("http://", "https://")
        base = f"{host_url}/assets"
    return f"{base}/{filename}"


@app.route('/assets/<path:filename>', methods=['GET'])
def get_theme_asset(filename):
    """Serve theme preview images from the assets directory."""
    asset_path = ASSETS_DIR / filename
    if not asset_path.exists():
        return jsonify({"error": "Asset not found"}), 404
    return send_from_directory(ASSETS_DIR, filename)


@app.route('/api/themes', methods=['GET'])
def get_themes():
    """Get available themes."""
    themes = [
        {"id": "classic", "name": "Classic", "image": _theme_image_url("classic.png")},
        {"id": "sb2nov", "name": "Sb2nov", "image": _theme_image_url("sb2nov.png")},
        {"id": "moderncv", "name": "ModernCV", "image": _theme_image_url("modern.png")},
        {"id": "engineeringresumes", "name": "Engineering Resumes", "image": _theme_image_url("engineering.png")},
        {"id": "engineeringclassic", "name": "Engineering Classic", "image": _theme_image_url("engineering_classic.png")}
    ]
    return jsonify(themes)

@app.route('/api/render', methods=['POST'])
@app.route('/api/render/<hash>', methods=['POST'])
def render_cv(hash=None):
    """Generate PDF from CV data and return it directly."""
    tmpdir_path = Path(tempfile.mkdtemp(prefix="rendercv_"))
    def _cleanup_tmpdir() -> None:
        shutil.rmtree(tmpdir_path, ignore_errors=True)

    try:
        cv_data = request.get_json(silent=True)

        if not cv_data:
            _cleanup_tmpdir()
            return jsonify({"error": "No CV data provided"}), 400

        # check if email not in cv_data
        if not cv_data.get("cv", {}).get("email"):
            _cleanup_tmpdir()
            return jsonify({"error": "Email is required"}), 400

        if _bool_env("LOG_RENDER_REQUESTS", default=False):
            logger.info(
                "render request content_length=%s name=%s theme=%s",
                request.content_length,
                cv_data.get("cv", {}).get("name"),
                cv_data.get("design", {}).get("theme"),
            )
        _log_memory_usage("before_render")
        _sanitize_cv_locations(cv_data)

        # Generate unique filename
        pdf_id = f"{uuid.uuid4().hex[:8]}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        typst_path = tmpdir_path / f"{pdf_id}.typ"
        pdf_path = tmpdir_path / f"{pdf_id}.pdf"

        # Generate Typst file
        errors = rcv_api.create_a_typst_file_from_a_python_dictionary(
            cv_data,
            typst_path
        )

        if errors:
            if _bool_env("LOG_RENDER_REQUESTS", default=False):
                logger.warning("render validation errors=%s", errors)
            _cleanup_tmpdir()
            return jsonify({"error": str(errors)}), 400

        # Render the PDF from the Typst file
        try:
            _render_pdf_from_typst(typst_path, pdf_path)
            typst_path.unlink(missing_ok=True)

            # Add metadata if hash is provided
            if hash:
                add_pdf_metadata(pdf_path, hash)
        except Exception as e:
            error_message = _compose_typst_error_message(str(e), typst_path)
            _cleanup_tmpdir()
            return jsonify({"error": error_message}), 500

        if not pdf_path.exists():
            _cleanup_tmpdir()
            return jsonify({"error": "PDF generation failed"}), 500

        download_name = f"{cv_data.get('cv', {}).get('name', 'cv')}_{pdf_id}.pdf"
        response = send_file(
            pdf_path,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=download_name
        )

        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'POST'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        response.call_on_close(_cleanup_tmpdir)

        _log_memory_usage("after_render")
        return response

    except Exception as e:
        _cleanup_tmpdir()
        return jsonify({"error": str(e)}), 500

@app.route('/api/validate', methods=['POST'])
def validate_cv():
    """Validate CV data structure."""
    try:
        cv_data = request.json
        
        # Try to parse with RenderCV
        data_model = rcv_api.read_a_python_dictionary_and_return_a_data_model(cv_data)
        
        if data_model is None:
            return jsonify({
                "valid": False,
                "errors": ["Invalid CV data structure"]
            }), 400
        
        return jsonify({
            "valid": True,
            "message": "CV data is valid"
        })
        
    except Exception as e:
        return jsonify({
            "valid": False,
            "errors": [str(e)]
        }), 400

@app.route('/api/sample/<cv_code>', methods=['GET'])
def get_sample_cv(cv_code):
    """Get CV data from Uptal API using cv_code."""
    try:
        redirect_url = request.args.get('redirectUrl')
        # Use the CV service to fetch data
        cv_data = cv_service.get_cv_by_code(cv_code, redirect_url)
        response = cv_data['data']
        position_match = response.get('position_match', None)

        # check if response is empty return 404
        if not response:
            return jsonify({'error': 'CV not found'}), 404

        # check if enhancement_result is not empty return enhancement_result
        if response.get('enhancement_result'):
            if position_match:
                response['enhancement_result']['position_match'] = position_match
            return jsonify(response['enhancement_result'])
        else:
            return jsonify({'error': 'CV not enhanced'}), 400
        
    except CVServiceException as e:
        # Handle known service exceptions with their specific status codes
        print(f"CV Service error: {e.message}")
        return jsonify({'error': e.message}), e.status_code
        
    except Exception as e:
        # Handle unexpected errors
        print(f"Unexpected error in get_sample_cv: {str(e)}")
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/api/info/<cv_code>', methods=['GET'])
def get_info(cv_code):
    """Get info about a CV."""
    try:
        redirect_url = request.args.get('redirectUrl')
        cv_data = cv_service.get_cv_by_code(cv_code, redirect_url)
        return jsonify(cv_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/export/<format>', methods=['POST'])
def export_cv(format):
    """Export CV in different formats."""
    try:
        cv_data = request.json
        
        if format == 'yaml':
            import ruamel.yaml
            yaml = ruamel.yaml.YAML()
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
                yaml.dump(cv_data, f)
                temp_path = f.name

            response = send_file(
                temp_path,
                as_attachment=True,
                download_name='cv.yaml',
                mimetype='text/yaml'
            )
            response.call_on_close(lambda: os.unlink(temp_path))
            return response
            
        elif format == 'json':
            return jsonify(cv_data)
            
        elif format == 'markdown':
            with tempfile.NamedTemporaryFile(suffix='.md', delete=False) as f:
                errors = rcv_api.create_a_markdown_file_from_a_python_dictionary(
                    cv_data,
                    Path(f.name)
                )
                if errors:
                    os.unlink(f.name)
                    return jsonify({'error': str(errors)}), 400

                response = send_file(
                    f.name,
                    as_attachment=True,
                    download_name='cv.md',
                    mimetype='text/markdown'
                )
                response.call_on_close(lambda: os.unlink(f.name))
                return response
        else:
            return jsonify({'error': f'Unsupported format: {format}'}), 400
            
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
            
        if file and file.filename.endswith(('.yaml', '.yml')):
            yaml_content = file.read().decode('utf-8')
            
            # Parse using RenderCV API
            data_model = rcv_api.read_a_yaml_string_and_return_a_data_model(yaml_content)
            
            if data_model is None:
                return jsonify({'error': 'Invalid YAML file'}), 400
            
            cv_data = data_model.model_dump()
            
            return jsonify({
                'success': True,
                'cv_data': cv_data
            })
        else:
            return jsonify({'error': 'Only YAML files are supported'}), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/cv-enhance/<cv_code>/edits', methods=['POST'])
def update_cv_edits(cv_code):
    """
    Update CV with new data via external API.

    User edits their CV in the editor and submits JSON data.

    Process:
    1. Validate JSON data
    2. Generate PDF from JSON using RenderCV
    3. Call cv_service.update_cv_edits() which triggers:
       - Old CV file deleted from storage
       - New CV uploaded
       - CV text extracted
       - CV data re-parsed
       - Database record updated (cv_path, cv_data, status, cv_enhance_status)
       - CV Enhancement Job dispatched
       - CV Analysis Job dispatched
       - Socket Event: cv_updated emitted

    Returns:
        JSON response with:
        - status: success/error
        - data: {cv_code, cv_id, application_id, status, cv_updated, message}
    """
    try:
        # Validate JSON data
        cv_data = request.json
        
        if not cv_data:
            return jsonify({
                'status': 'error',
                'error': 'No CV data provided'
            }), 400

        # check if email not in cv_data
        if not cv_data.get("cv", {}).get("email"):
            return jsonify({
                'status': 'error',
                'error': 'Email is required'
            }), 400

        if _bool_env("LOG_RENDER_REQUESTS", default=False):
            logger.info(
                "render enhance request content_length=%s cv_code=%s name=%s theme=%s",
                request.content_length,
                cv_code,
                cv_data.get("cv", {}).get("name"),
                cv_data.get("design", {}).get("theme"),
            )
        _sanitize_cv_locations(cv_data)
        
        redirect_url = request.args.get('redirectUrl')

        # Generate PDF from JSON using RenderCV within a temporary directory
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            pdf_id = f"{uuid.uuid4().hex[:8]}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            typst_path = tmpdir_path / f"{pdf_id}.typ"
            pdf_path = tmpdir_path / f"{pdf_id}.pdf"
            
            # Step 1: Create Typst file from CV data
            errors = rcv_api.create_a_typst_file_from_a_python_dictionary(
                cv_data,
                typst_path
            )
            
            if errors:
                print(f"RenderCV validation errors: {errors}")
                return jsonify({
                    'status': 'error',
                    'error': f'Invalid CV data: {str(errors)}'
                }), 400

            # Step 2: Render PDF from Typst file
            try:
                _render_pdf_from_typst(typst_path, pdf_path)
                # Clean up the Typst file
                typst_path.unlink(missing_ok=True)
            except Exception as e:
                # Clean up on error
                error_message = _compose_typst_error_message(str(e), typst_path)
                typst_path.unlink(missing_ok=True)
                return jsonify({
                    'status': 'error',
                    'error': f'PDF generation failed: {error_message}'
                }), 500
            
            # Validate PDF was created
            if not pdf_path.exists():
                return jsonify({
                    'status': 'error',
                    'error': 'PDF generation failed'
                }), 500

            # Validate file size (max 5MB)
            file_size = pdf_path.stat().st_size
            if file_size > 5 * 1024 * 1024:  # 5MB
                return jsonify({
                    'status': 'error',
                    'error': 'Generated PDF exceeds 5MB limit'
                }), 400

            # Stamp PDF with the CV hash for downstream tracking
            add_pdf_metadata(pdf_path, cv_code)

            from werkzeug.datastructures import FileStorage

            with open(pdf_path, "rb") as pdf_file:
                cv_file = FileStorage(
                    stream=pdf_file,
                    filename=f"{cv_data.get('cv', {}).get('name', 'CV').replace(' ', '_')}_{pdf_id}.pdf",
                    content_type="application/pdf",
                )

                # Call cv_service to update CV via external API
                # The API handles:
                # - Deleting old CV file
                # - Uploading new CV
                # - Extracting text
                # - Re-parsing data
                # - Updating database
                # - Dispatching jobs
                # - Emitting socket events
                result = cv_service.update_cv_edits(cv_code, cv_file, redirect_url)
        
        return jsonify(result), 200

    except CVServiceException as e:
        return jsonify({
            'status': 'error',
            'error': e.message
        }), e.status_code
    except Exception as e:
        print(f"Error in update_cv_edits: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'status': 'error',
            'error': f'Server error: {str(e)}'
        }), 500

def add_pdf_metadata(pdf_path, cv_hash):
    """Add custom metadata to PDF."""
    try:
        from pypdf import PdfReader, PdfWriter

        with open(pdf_path, "rb") as input_file:
            reader = PdfReader(input_file)
            writer = PdfWriter()

            # Copy all pages
            for page in reader.pages:
                writer.add_page(page)

            # Copy existing metadata if any
            if reader.metadata:
                writer.add_metadata(reader.metadata)

            # Add custom metadata
            writer.add_metadata({
                '/uptal_candidate_cv_hash': cv_hash
            })

            # Write to a temporary file first
            temp_path = pdf_path.with_suffix('.tmp.pdf')
            with open(temp_path, 'wb') as output_file:
                writer.write(output_file)

        # Replace original file with the new one (after input file is closed)
        temp_path.replace(pdf_path)
        if _bool_env("LOG_RENDER_REQUESTS", default=False):
            logger.info("Added PDF metadata uptal_candidate_cv_hash=%s", cv_hash)

    except Exception as e:
        logger.warning("Error adding PDF metadata: %s", e)
        # Non-critical error, don't fail the request

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
