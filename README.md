# Face Recognition System

A complete face recognition system built with Flask, OpenCV, and the face_recognition library.

## Features

- **Image Upload**: Upload images to recognize faces
- **Webcam Feed**: Real-time face recognition from webcam
- **Add Known Faces**: Build a database of known faces
- **Face Matching**: Compare uploaded images against known faces
- **Confidence Scores**: Get confidence scores for face matches
- **Web Interface**: Clean, modern UI for easy interaction

## Project Structure

```
face-recognition/
├── app/
│   ├── __init__.py
│   ├── face_recognizer.py      # Core face recognition logic
│   └── routes.py               # Flask routes
├── templates/
│   └── index.html              # Web interface
├── static/
│   ├── style.css               # Styling
│   └── script.js               # Frontend logic
├── known_faces/                # Directory for known face images
│   └── person_name/            # Subdirectory for each person
│       ├── image1.jpg
│       ├── image2.jpg
│       └── ...
├── uploads/                    # Temporary upload directory
├── requirements.txt            # Python dependencies
├── main.py                     # Application entry point
└── README.md                   # This file
```

## Installation

### Prerequisites
- Python 3.7 or higher
- pip package manager
- Webcam (optional, for live feed feature)

### Setup Steps

1. **Navigate to the project directory**:
   ```bash
   cd c:\Projects\face-recognition
   ```

2. **Create a virtual environment** (recommended):
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

   > **Note**: The first installation may take a while as it downloads pre-trained models.

## Usage

### Starting the Application

1. **Run the main application**:
   ```bash
   python main.py
   ```

2. **Open your browser** and go to:
   ```
   http://localhost:5000
   ```

### Adding Known Faces

1. Go to the **"Add Face"** tab
2. Enter the person's name
3. Select an image containing their face
4. Click **"Add Face"**

**Tips for best results**:
- Use clear, well-lit images
- Ensure the face is clearly visible
- Use 1-3 images per person
- Different angles and expressions improve accuracy

### Recognizing Faces in Images

1. Go to the **"Upload Image"** tab
2. Upload an image containing one or more faces
3. Click **"Recognize Faces"**
4. Results show:
   - Identified person name (or "Unknown")
   - Confidence score (0.0 - 1.0)
   - Face location coordinates

### Live Webcam Recognition

1. Go to the **"Webcam Feed"** tab
2. Click **"Start Webcam"**
3. The system will stream live video with real-time face recognition
4. Click **"Stop Webcam"** to stop the stream

## How It Works

### Face Recognition Process

1. **Face Detection**: Uses HOG (Histogram of Oriented Gradients) or CNN to detect faces
2. **Face Encoding**: Converts each detected face into a 128-dimensional vector
3. **Face Comparison**: Compares encoded faces using Euclidean distance
4. **Match Decision**: If distance is below tolerance threshold, faces are considered a match

### Key Parameters

- **Tolerance** (default: 0.6): Lower values = stricter matching
  - 0.4: Very strict
  - 0.6: Balanced (default)
  - 0.8: More permissive

- **Model** (default: 'hog'): Detection model
  - 'hog': Fast, less accurate, CPU only
  - 'cnn': Slow, more accurate, GPU recommended

## Configuration

Edit settings in `app/face_recognizer.py`:

```python
recognizer = FaceRecognizer(
    known_faces_dir='known_faces',
    tolerance=0.6,           # Adjust for stricter/looser matching
    model='hog'              # Use 'cnn' for higher accuracy
)
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Main web interface |
| `/recognize_image` | POST | Recognize faces in uploaded image |
| `/video_feed` | GET | Stream live webcam with recognition |
| `/add_face` | POST | Add new face to known faces |
| `/known_faces` | GET | List all known faces |
| `/health` | GET | Health check |

## Troubleshooting

### Common Issues

**Issue**: "No module named 'face_recognition'"
- **Solution**: Run `pip install -r requirements.txt`

**Issue**: Webcam not working
- **Solution**: Check camera permissions and try a different camera ID (modify `video_source` parameter)

**Issue**: Faces not being recognized
- **Solution**: 
  - Ensure at least one image is added to known_faces
  - Try adjusting the tolerance value (lower = stricter)
  - Use clearer, better-lit images
  - Try the 'cnn' model for better accuracy

**Issue**: Application runs slow
- **Solution**:
  - Reduce image resolution
  - Change model from 'cnn' to 'hog'
  - Process every nth frame for video (currently set to 2)

## Performance Tips

1. **Pre-process known faces**: Add 2-3 high-quality images per person
2. **Use HOG for speed**: Switch to CNN only when accuracy is critical
3. **Optimize video**: Process every 2-3 frames instead of every frame
4. **Cache encodings**: Encodings are cached in `face_encodings.pkl`

## Dependencies

- **face_recognition**: Core face recognition library
- **opencv-python**: Image and video processing
- **numpy**: Numerical computations
- **Flask**: Web framework
- **Werkzeug**: WSGI utilities
- **Pillow**: Image handling

## Security Notes

⚠️ **Important**: This is a demonstration system. For production use:
- Implement proper authentication
- Use HTTPS for data transmission
- Store sensitive data securely
- Consider privacy implications
- Implement proper logging and monitoring

## Limitations

- Currently supports only facial features (not facial recognition by other attributes)
- Requires clear, frontal face images for best results
- Performance depends on image quality and lighting
- May have difficulties with heavily obscured faces

## Future Enhancements

- [ ] Database integration for persistent storage
- [ ] Face clustering for automatic grouping
- [ ] Multi-face batch processing
- [ ] Export reports and statistics
- [ ] User authentication and roles
- [ ] Mobile app support
- [ ] GPU acceleration support
- [ ] Advanced filtering and search

## License

This project is open source and available for educational and personal use.

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review the source code comments
3. Consult the face_recognition library documentation

---

**Created**: January 2026
**Version**: 1.0.0
