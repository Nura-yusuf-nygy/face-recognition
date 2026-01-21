// Tab switching
function switchTab(tabName) {
    // Hide all tabs
    const tabs = document.querySelectorAll('.tab-content');
    tabs.forEach(tab => tab.classList.remove('active'));

    // Remove active from all buttons
    const buttons = document.querySelectorAll('.tab-btn');
    buttons.forEach(btn => btn.classList.remove('active'));

    // Show selected tab
    document.getElementById(tabName).classList.add('active');
    event.target.classList.add('active');
}

// File upload handling
document.getElementById('imageInput').addEventListener('change', function(e) {
    handleFileSelect(e, 'preview');
});

document.getElementById('addFaceInput').addEventListener('change', function(e) {
    handleFileSelect(e, 'addFacePreview');
});

// Drag and drop
setupDragAndDrop('uploadBox', 'imageInput');
setupDragAndDrop('addFaceBox', 'addFaceInput');

function setupDragAndDrop(boxId, inputId) {
    const box = document.getElementById(boxId);
    const input = document.getElementById(inputId);

    box.addEventListener('dragover', (e) => {
        e.preventDefault();
        box.classList.add('dragover');
    });

    box.addEventListener('dragleave', () => {
        box.classList.remove('dragover');
    });

    box.addEventListener('drop', (e) => {
        e.preventDefault();
        box.classList.remove('dragover');
        input.files = e.dataTransfer.files;
        input.dispatchEvent(new Event('change'));
    });

    box.addEventListener('click', () => input.click());
}

function handleFileSelect(e, previewId) {
    const file = e.target.files[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (event) => {
        const preview = document.getElementById(previewId);
        if (preview) {
            preview.src = event.target.result;
            preview.style.display = 'block';
        }
    };
    reader.readAsDataURL(file);
}

// Recognize image
function recognizeImage() {
    const imageInput = document.getElementById('imageInput');
    if (!imageInput.files[0]) {
        showMessage('Please select an image', 'error');
        return;
    }

    const formData = new FormData();
    formData.append('file', imageInput.files[0]);

    showMessage('Processing image...', 'info');

    fetch('/recognize_image', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        displayResults(data);
    })
    .catch(error => {
        showMessage('Error: ' + error.message, 'error');
    });
}

function displayResults(data) {
    const container = document.getElementById('resultsContainer');
    container.innerHTML = '';

    if (data.error) {
        showMessage('Error: ' + data.error, 'error');
        return;
    }

    if (!data.faces || data.faces.length === 0) {
        showMessage('No faces detected in the image', 'info');
        return;
    }

    showMessage(`Found ${data.faces.length} face(s)`, 'success');

    data.faces.forEach((face, index) => {
        const confidence = (face.confidence * 100).toFixed(1);
        const resultDiv = document.createElement('div');
        resultDiv.className = 'face-result';
        resultDiv.innerHTML = `
            <div class="face-info">
                <div class="face-name">${face.name}</div>
                <div class="face-confidence">
                    Confidence: ${confidence}%
                    <div class="confidence-bar">
                        <div class="confidence-fill" style="width: ${confidence}%"></div>
                    </div>
                </div>
                <div style="font-size: 0.9em; color: #999; margin-top: 5px;">
                    Location: (${face.location.left}, ${face.location.top}, ${face.location.right}, ${face.location.bottom})
                </div>
            </div>
        `;
        container.appendChild(resultDiv);
    });
}

// Webcam
let webcamRunning = false;

function startWebcam() {
    const feed = document.getElementById('webcamFeed');
    const status = document.getElementById('webcamStatus');

    feed.src = '/video_feed';
    feed.style.display = 'block';
    status.textContent = 'Webcam is running...';
    webcamRunning = true;
    showMessage('Webcam started', 'success');
}

function stopWebcam() {
    const feed = document.getElementById('webcamFeed');
    const status = document.getElementById('webcamStatus');

    feed.src = '';
    feed.style.display = 'none';
    status.textContent = 'Webcam stopped';
    webcamRunning = false;
    showMessage('Webcam stopped', 'info');
}

// Add face
function addFace() {
    const nameInput = document.getElementById('personName');
    const fileInput = document.getElementById('addFaceInput');

    const name = nameInput.value.trim();
    if (!name) {
        showMessage('Please enter a person name', 'error');
        return;
    }

    if (!fileInput.files[0]) {
        showMessage('Please select an image', 'error');
        return;
    }

    const formData = new FormData();
    formData.append('file', fileInput.files[0]);
    formData.append('name', name);

    showMessage('Adding face...', 'info');

    fetch('/add_face', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showMessage('Face added successfully!', 'success');
            nameInput.value = '';
            fileInput.value = '';
            document.getElementById('preview').style.display = 'none';
        } else {
            showMessage('Error: ' + data.message, 'error');
        }
    })
    .catch(error => {
        showMessage('Error: ' + error.message, 'error');
    });
}

// List known faces
function listKnownFaces() {
    fetch('/known_faces')
    .then(response => response.json())
    .then(data => {
        const container = document.getElementById('knownFacesList');
        container.innerHTML = '';

        if (!data.faces || data.faces.length === 0) {
            container.innerHTML = '<p>No known faces yet. Add some faces to get started!</p>';
            return;
        }

        const list = document.createElement('div');
        list.className = 'known-faces-list';

        data.faces.forEach(face => {
            const card = document.createElement('div');
            card.className = 'face-card';
            card.innerHTML = `
                <div style="font-size: 2em;">👤</div>
                <div class="face-card-name">${face}</div>
            `;
            list.appendChild(card);
        });

        container.appendChild(list);
        showMessage(`${data.faces.length} known face(s) loaded`, 'success');
    })
    .catch(error => {
        showMessage('Error loading faces: ' + error.message, 'error');
    });
}

// Message display
function showMessage(message, type) {
    // Create message element if it doesn't exist
    let messageDiv = document.getElementById('message');
    if (!messageDiv) {
        messageDiv = document.createElement('div');
        messageDiv.id = 'message';
        messageDiv.className = 'message';
        document.querySelector('main').insertBefore(messageDiv, document.querySelector('main').firstChild);
    }

    messageDiv.className = `message ${type}`;
    messageDiv.textContent = message;

    // Auto-hide after 5 seconds
    setTimeout(() => {
        messageDiv.style.display = 'none';
    }, 5000);
}

// Load known faces on page load
window.addEventListener('load', () => {
    listKnownFaces();
});
