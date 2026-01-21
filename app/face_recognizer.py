import os
import cv2
import numpy as np
from pathlib import Path
import pickle


class FaceRecognizer:
    """Face recognizer using OpenCV cascade classifiers and LBPH recognizer."""
    
    def __init__(self, known_faces_dir='known_faces', tolerance=0.6, model='cascade'):
        """
        Initialize the face recognizer.
        
        Args:
            known_faces_dir: Directory containing known face images
            tolerance: Face comparison tolerance (lower = more strict)
            model: Detection model ('cascade' using cascade classifiers)
        """
        self.known_faces_dir = known_faces_dir
        self.tolerance = tolerance
        self.model = model
        self.encodings_file = 'face_encodings.pkl'
        self.recognizer = cv2.face.LBPHFaceRecognizer_create()
        self.known_face_labels = []
        self.known_face_names = []
        self.label_to_name = {}
        self.model_file = 'face_model.yml'
        
        # Load cascade classifiers
        cascade_path = cv2.data.haarcascades
        self.face_cascade = cv2.CascadeClassifier(
            os.path.join(cascade_path, 'haarcascade_frontalface_default.xml')
        )
        
        # Create directory if it doesn't exist
        Path(self.known_faces_dir).mkdir(exist_ok=True)
        
    def load_known_faces(self):
        """Load and train model on known faces."""
        print(f"Loading known faces from {self.known_faces_dir}...")
        
        if os.path.exists(self.model_file) and os.path.exists(self.encodings_file):
            print(f"Loading cached model from {self.model_file}...")
            self.recognizer.read(self.model_file)
            with open(self.encodings_file, 'rb') as f:
                data = pickle.load(f)
                self.label_to_name = data['label_to_name']
                self.known_face_names = list(set(self.label_to_name.values()))
            print(f"Loaded model with {len(self.label_to_name)} face(s)")
            return
        
        # Scan for image files
        image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp'}
        face_images = []
        face_labels = []
        label_counter = 0
        
        for person_dir in os.listdir(self.known_faces_dir):
            person_path = os.path.join(self.known_faces_dir, person_dir)
            
            if not os.path.isdir(person_path):
                continue
            
            print(f"Processing images for: {person_dir}")
            self.label_to_name[label_counter] = person_dir
            
            for image_name in os.listdir(person_path):
                if not any(image_name.lower().endswith(ext) for ext in image_extensions):
                    continue
                
                image_path = os.path.join(person_path, image_name)
                
                try:
                    # Load and convert image
                    image = cv2.imread(image_path)
                    if image is None:
                        print(f"  ✗ Failed to load: {image_name}")
                        continue
                    
                    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                    
                    # Detect faces
                    faces = self.face_cascade.detectMultiScale(
                        gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30)
                    )
                    
                    if len(faces) == 0:
                        print(f"  ✗ No face found in: {image_name}")
                        continue
                    
                    # Use the first (largest) face
                    (x, y, w, h) = faces[0]
                    face_roi = gray[y:y+h, x:x+w]
                    face_roi = cv2.resize(face_roi, (200, 200))
                    
                    face_images.append(face_roi)
                    face_labels.append(label_counter)
                    print(f"  ✓ Encoded: {image_name}")
                    
                except Exception as e:
                    print(f"  ✗ Error processing {image_name}: {str(e)}")
            
            label_counter += 1
        
        if len(face_images) > 0:
            print(f"\nTraining model with {len(face_images)} face(s)...")
            self.recognizer.train(face_images, np.array(face_labels))
            self.recognizer.save(self.model_file)
            
            # Cache metadata
            with open(self.encodings_file, 'wb') as f:
                pickle.dump({'label_to_name': self.label_to_name}, f)
            
            print(f"✓ Model saved to {self.model_file}")
            self.known_face_names = list(set(self.label_to_name.values()))
        else:
            print("No face images found for training.")
    
    def recognize_faces_in_image(self, image_path):
        """
        Recognize faces in an image.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            List of dicts with face information
        """
        try:
            image = cv2.imread(image_path)
            if image is None:
                return {'error': 'Failed to load image', 'faces': []}
            
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        except Exception as e:
            return {'error': f'Failed to load image: {str(e)}', 'faces': []}
        
        # Detect faces
        faces = self.face_cascade.detectMultiScale(
            gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30)
        )
        
        results = []
        
        for (x, y, w, h) in faces:
            face_roi = gray[y:y+h, x:x+w]
            face_roi = cv2.resize(face_roi, (200, 200))
            
            # Recognize face
            label, confidence = self.recognizer.predict(face_roi)
            
            # Lower confidence is better
            confidence_score = 1.0 - (min(confidence, 255) / 255.0)
            
            name = self.label_to_name.get(label, "Unknown")
            if confidence > 100:  # Threshold for unknown
                name = "Unknown"
                confidence_score = 0
            
            results.append({
                'name': name,
                'confidence': float(confidence_score),
                'location': {
                    'top': int(y),
                    'right': int(x + w),
                    'bottom': int(y + h),
                    'left': int(x)
                }
            })
        
        return {'error': None, 'faces': results}
    
    def recognize_faces_in_video(self, video_source=0, max_frames=None):
        """
        Recognize faces in video stream (webcam or video file).
        
        Args:
            video_source: 0 for webcam, or path to video file
            max_frames: Maximum frames to process (None for unlimited)
            
        Yields:
            Processed frame as bytes
        """
        cap = cv2.VideoCapture(video_source)
        frame_count = 0
        process_every_n_frames = 2  # Process every 2nd frame for speed
        
        try:
            while True:
                ret, frame = cap.read()
                
                if not ret:
                    break
                
                frame_count += 1
                
                # Process every nth frame for performance
                if frame_count % process_every_n_frames != 0:
                    continue
                
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                faces = self.face_cascade.detectMultiScale(
                    gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30)
                )
                
                for (x, y, w, h) in faces:
                    face_roi = gray[y:y+h, x:x+w]
                    face_roi = cv2.resize(face_roi, (200, 200))
                    
                    label, confidence = self.recognizer.predict(face_roi)
                    confidence_score = 1.0 - (min(confidence, 255) / 255.0)
                    
                    name = self.label_to_name.get(label, "Unknown")
                    if confidence > 100:
                        name = "Unknown"
                    
                    # Draw box and label
                    color = (0, 255, 0) if name != "Unknown" else (0, 0, 255)
                    cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
                    
                    label_text = f"{name} ({confidence_score:.2f})" if name != "Unknown" else name
                    cv2.rectangle(frame, (x, y + h - 35), (x + w, y + h), color, cv2.FILLED)
                    cv2.putText(frame, label_text, (x + 6, y + h - 6), 
                              cv2.FONT_HERSHEY_DUPLEX, 0.6, (255, 255, 255), 1)
                
                # Encode frame to jpeg
                ret, buffer = cv2.imencode('.jpg', frame)
                frame_bytes = buffer.tobytes()
                
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
                
                if max_frames and frame_count >= max_frames:
                    break
        
        finally:
            cap.release()
    
    def add_face_to_known(self, image_path, person_name):
        """
        Add a face image to the known faces collection.
        
        Args:
            image_path: Path to the image
            person_name: Name of the person
            
        Returns:
            Success status and message
        """
        person_dir = os.path.join(self.known_faces_dir, person_name)
        Path(person_dir).mkdir(exist_ok=True)
        
        try:
            import shutil
            dest_path = os.path.join(person_dir, os.path.basename(image_path))
            shutil.copy(image_path, dest_path)
            
            # Clear cache to force reload
            if os.path.exists(self.encodings_file):
                os.remove(self.encodings_file)
            
            return {'success': True, 'message': f'Face added for {person_name}'}
        except Exception as e:
            return {'success': False, 'message': f'Error adding face: {str(e)}'}
