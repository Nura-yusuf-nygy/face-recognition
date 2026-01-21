from flask import Flask, render_template, request, jsonify, Response
from werkzeug.utils import secure_filename
import os
from pathlib import Path
from app.face_recognizer import FaceRecognizer

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp'}
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB

# Get the root directory (parent of the app directory)
root_dir = Path(__file__).parent.parent

# Create app with correct template and static paths
app = Flask(
    __name__,
    template_folder=str(root_dir / 'templates'),
    static_folder=str(root_dir / 'static')
)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# Create upload folder if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize face recognizer
recognizer = FaceRecognizer(tolerance=0.6, model='hog')
recognizer.load_known_faces()


def allowed_file(filename):
    """Check if file has allowed extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def index():
    """Render the main page."""
    return render_template('index.html')


@app.route('/recognize_image', methods=['POST'])
def recognize_image():
    """Handle image upload and recognize faces."""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'File type not allowed'}), 400
    
    try:
        # Save file
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Recognize faces
        result = recognizer.recognize_faces_in_image(filepath)
        
        # Clean up
        os.remove(filepath)
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'error': f'Error processing image: {str(e)}'}), 500


@app.route('/video_feed')
def video_feed():
    """Stream video from webcam with face recognition."""
    return Response(
        recognizer.recognize_faces_in_video(video_source=0),
        mimetype='multipart/x-mixed-replace; boundary=frame'
    )


@app.route('/add_face', methods=['POST'])
def add_face():
    """Add a new face to known faces."""
    if 'file' not in request.files or 'name' not in request.form:
        return jsonify({'error': 'Missing file or name'}), 400
    
    file = request.files['file']
    name = request.form.get('name', '').strip()
    
    if file.filename == '' or not name:
        return jsonify({'error': 'Invalid file or name'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'File type not allowed'}), 400
    
    try:
        # Save temporarily
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Add to known faces
        result = recognizer.add_face_to_known(filepath, name)
        
        # Clean up
        os.remove(filepath)
        
        if result['success']:
            # Reload known faces
            recognizer.load_known_faces()
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500


@app.route('/known_faces')
def list_known_faces():
    """Get list of known faces."""
    known_faces_dir = 'known_faces'
    faces = []
    
    if os.path.exists(known_faces_dir):
        for person_name in os.listdir(known_faces_dir):
            person_path = os.path.join(known_faces_dir, person_name)
            if os.path.isdir(person_path):
                faces.append(person_name)
    
    return jsonify({'faces': sorted(faces)})


@app.route('/delete_face/<person_name>', methods=['DELETE', 'POST'])
def delete_face(person_name):
    """Delete a person from known faces."""
    person_dir = os.path.join('known_faces', person_name)
    
    try:
        if os.path.exists(person_dir):
            import shutil
            shutil.rmtree(person_dir)
            
            # Clear cache to force reload
            if os.path.exists('face_model.yml'):
                os.remove('face_model.yml')
            if os.path.exists('face_encodings.pkl'):
                os.remove('face_encodings.pkl')
            
            return jsonify({'success': True, 'message': f'Deleted {person_name}'})
        else:
            return jsonify({'success': False, 'message': 'Person not found'}), 404
    
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500


@app.route('/health')
def health():
    """Health check endpoint."""
    return jsonify({'status': 'ok'})


if __name__ == '__main__':
    app.run(debug=True, port=5000)
