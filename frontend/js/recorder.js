class AudioRecorder {
    constructor() {
        this.mediaRecorder = null;
        this.audioChunks = [];
        this.isRecording = false;
        this.isPaused = false;
        this.stream = null;
        this.audioBlob = null;
        this.audioUrl = null;
    }

    async startRecording() {
        try {
            this.stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            this.mediaRecorder = new MediaRecorder(this.stream);
            this.audioChunks = [];

            this.mediaRecorder.ondataavailable = (event) => {
                this.audioChunks.push(event.data);
            };

            this.mediaRecorder.onstop = () => {
                this.audioBlob = new Blob(this.audioChunks, { type: 'audio/webm' });
                this.audioUrl = URL.createObjectURL(this.audioBlob);
            };

            this.mediaRecorder.start();
            this.isRecording = true;
            this.isPaused = false;
            return true;
        } catch (error) {
            console.error('Error starting recording:', error);
            throw error;
        }
    }

    stopRecording() {
        if (this.mediaRecorder && this.isRecording) {
            this.mediaRecorder.stop();
            this.isRecording = false;
            this.isPaused = false;
            
            // Stop all tracks
            if (this.stream) {
                this.stream.getTracks().forEach(track => track.stop());
            }
        }
    }

    pauseRecording() {
        if (this.mediaRecorder && this.isRecording && !this.isPaused) {
            this.mediaRecorder.pause();
            this.isPaused = true;
        }
    }

    resumeRecording() {
        if (this.mediaRecorder && this.isRecording && this.isPaused) {
            this.mediaRecorder.resume();
            this.isPaused = false;
        }
    }

    getAudioBlob() {
        return this.audioBlob;
    }

    getAudioUrl() {
        return this.audioUrl;
    }

    reset() {
        this.audioBlob = null;
        this.audioChunks = [];
        this.audioUrl = null;
        this.isRecording = false;
        this.isPaused = false;
        
        if (this.stream) {
            this.stream.getTracks().forEach(track => track.stop());
        }
    }
}

// Initialize recorder
const recorder = new AudioRecorder();

// DOM Elements
const recordBtn = document.getElementById('recordBtn');
const recordIcon = document.getElementById('recordIcon');
const recordText = document.getElementById('recordText');
const recordingStatus = document.getElementById('recordingStatus');
const audioFileInput = document.getElementById('audioFile');
const fileDropzone = document.getElementById('fileDropzone');
const processBtn = document.getElementById('processBtn');

// Recording State
let recordingStartTime = null;
let recordingInterval = null;

// Update recording UI
function updateRecordingUI() {
    if (recorder.isRecording) {
        if (recorder.isPaused) {
            recordIcon.textContent = '▶️';
            recordText.textContent = 'Resume Recording';
            recordBtn.classList.remove('btn-danger');
            recordBtn.classList.add('btn-warning');
        } else {
            recordIcon.textContent = '⏸️';
            recordText.textContent = 'Pause Recording';
            recordBtn.classList.remove('btn-warning');
            recordBtn.classList.add('btn-danger');
        }
    } else {
        recordIcon.textContent = '🎤';
        recordText.textContent = 'Start Recording';
        recordBtn.classList.remove('btn-danger', 'btn-warning');
        recordBtn.classList.add('btn-primary');
    }
}

// Update recording timer
function updateRecordingTimer() {
    if (recorder.isRecording && !recorder.isPaused) {
        const elapsed = Math.floor((Date.now() - recordingStartTime) / 1000);
        const minutes = Math.floor(elapsed / 60);
        const seconds = elapsed % 60;
        recordingStatus.textContent = `Recording: ${minutes}:${seconds.toString().padStart(2, '0')}`;
    }
}

// Handle record button click
recordBtn.addEventListener('click', async () => {
    if (!recorder.isRecording) {
        // Start recording
        try {
            await recorder.startRecording();
            recordingStartTime = Date.now();
            recordingInterval = setInterval(updateRecordingTimer, 1000);
            recordingStatus.textContent = 'Recording: 0:00';
            updateRecordingUI();
        } catch (error) {
            alert('Could not access microphone. Please ensure microphone permissions are granted.');
        }
    } else if (recorder.isPaused) {
        // Resume recording
        recorder.resumeRecording();
        updateRecordingUI();
    } else {
        // Pause recording
        recorder.pauseRecording();
        updateRecordingUI();
    }
});

// Add stop recording button dynamically
const stopRecordBtn = document.createElement('button');
stopRecordBtn.className = 'btn btn-secondary';
stopRecordBtn.textContent = '⏹ Stop Recording';
stopRecordBtn.style.display = 'none';
stopRecordBtn.id = 'stopRecordBtn';
recordBtn.parentElement.insertBefore(stopRecordBtn, recordBtn.nextSibling);

stopRecordBtn.addEventListener('click', () => {
    if (recorder.isRecording) {
        recorder.stopRecording();
        clearInterval(recordingInterval);
        recordingStatus.textContent = 'Recording saved!';
        updateRecordingUI();
        stopRecordBtn.style.display = 'none';
        
        // Show preview
        showRecordingPreview();
    }
});

// Show recording preview
function showRecordingPreview() {
    const audioUrl = recorder.getAudioUrl();
    if (audioUrl) {
        const previewContainer = document.createElement('div');
        previewContainer.className = 'recording-preview';
        previewContainer.innerHTML = `
            <audio controls src="${audioUrl}" style="width: 100%; margin-top: 10px;"></audio>
            <div style="margin-top: 10px; display: flex; gap: 10px;">
                <button id="submitRecording" class="btn btn-primary">Submit Recording</button>
                <button id="deleteRecording" class="btn btn-secondary">Delete</button>
            </div>
        `;
        
        recordingStatus.parentElement.appendChild(previewContainer);
        
        // Submit recording
        document.getElementById('submitRecording').addEventListener('click', async () => {
            await submitRecording();
        });
        
        // Delete recording
        document.getElementById('deleteRecording').addEventListener('click', () => {
            recorder.reset();
            previewContainer.remove();
            recordingStatus.textContent = '';
            stopRecordBtn.style.display = 'none';
        });
    }
}

// Submit recording to API
async function submitRecording() {
    const audioBlob = recorder.getAudioBlob();
    if (!audioBlob) {
        alert('No recording to submit');
        return;
    }
    
    const formData = new FormData();
    formData.append('file', audioBlob, 'recording.webm');
    
    try {
        const response = await fetchAPI('/audio/record', {
            method: 'POST',
            body: formData,
        });
        
        if (response) {
            alert('Recording saved successfully!');
            recorder.reset();
            document.querySelector('.recording-preview').remove();
            recordingStatus.textContent = '';
            stopRecordBtn.style.display = 'none';
            
            // Store audio file ID for next step
            const audioId = response.id || response.audio_id;
            localStorage.setItem('current_audio_id', audioId);
            localStorage.setItem('current_audio_source', 'record');
            
            // Enable process button
            processBtn.disabled = false;
            
            // Automatically trigger transcription
            await triggerTranscription(audioId);
        }
    } catch (error) {
        alert('Failed to save recording: ' + error.message);
    }
}

// Handle file dropzone click
fileDropzone.addEventListener('click', () => {
    audioFileInput.click();
});

// Handle file selection
audioFileInput.addEventListener('change', async (e) => {
    const file = e.target.files[0];
    if (file) {
        await uploadFile(file);
    }
});

// Handle drag and drop
fileDropzone.addEventListener('dragover', (e) => {
    e.preventDefault();
    fileDropzone.style.borderColor = '#667eea';
    fileDropzone.style.backgroundColor = '#f0f0f0';
});

fileDropzone.addEventListener('dragleave', (e) => {
    e.preventDefault();
    fileDropzone.style.borderColor = '#ddd';
    fileDropzone.style.backgroundColor = 'transparent';
});

fileDropzone.addEventListener('drop', async (e) => {
    e.preventDefault();
    fileDropzone.style.borderColor = '#ddd';
    fileDropzone.style.backgroundColor = 'transparent';
    
    const file = e.dataTransfer.files[0];
    if (file) {
        await uploadFile(file);
    }
});

// Upload file to API
async function uploadFile(file) {
    const formData = new FormData();
    formData.append('file', file);
    
    try {
        const response = await fetchAPI('/audio/upload', {
            method: 'POST',
            body: formData,
        });
        
        if (response) {
            alert('File uploaded successfully!');
            fileDropzone.innerHTML = `<p>✅ ${file.name} uploaded</p>`;
            
            // Store audio file ID for next step
            const audioId = response.id || response.audio_id;
            localStorage.setItem('current_audio_id', audioId);
            localStorage.setItem('current_audio_source', 'upload');
            
            // Enable process button
            processBtn.disabled = false;
            
            // Automatically trigger transcription
            await triggerTranscription(audioId);
        }
    } catch (error) {
        alert('Failed to upload file: ' + error.message);
    }
}

// Show stop button when recording starts
const originalStartRecording = recorder.startRecording;
recorder.startRecording = async function() {
    const result = await originalStartRecording.call(this);
    if (result) {
        stopRecordBtn.style.display = 'inline-block';
    }
    return result;
};

// Initialize process button as disabled
if (processBtn) {
    processBtn.disabled = true;
}

// Trigger transcription after successful upload/record
async function triggerTranscription(audioId) {
    const sourceLanguage = document.getElementById('sourceLanguage')?.value;
    
    try {
        // Disable process button and show loading
        if (processBtn) {
            processBtn.disabled = true;
            processBtn.textContent = 'Processing...';
        }
        
        // Call transcription API
        const body = {
            audio_id: parseInt(audioId)
        };
        if (sourceLanguage && sourceLanguage !== 'auto') {
            body.source_language = sourceLanguage;
        }
        
        const transcription = await fetchAPI('/speech/transcribe', {
            method: 'POST',
            body: JSON.stringify(body),
        });
        
        // Store transcription data
        localStorage.setItem('current_transcription_id', transcription.id);
        localStorage.setItem('current_transcription_text', transcription.ai_transcription);
        localStorage.setItem('detected_language', transcription.source_language);
        
        // Update STEP 2 UI
        updateStep2UI(transcription);
        
        // Move to STEP 2
        moveToStep(2);
        
        alert('Transcription completed successfully!');
    } catch (error) {
        alert('Transcription failed: ' + error.message);
    } finally {
        if (processBtn) {
            processBtn.disabled = false;
            processBtn.textContent = 'Start Processing';
        }
    }
}

// Update STEP 2 UI with transcription results
function updateStep2UI(transcription) {
    const transcriptionText = document.getElementById('transcriptionText');
    const transcriptionLanguage = document.getElementById('transcriptionLanguage');
    const transcriptionConfidence = document.getElementById('transcriptionConfidence');
    const transcriptionDuration = document.getElementById('transcriptionDuration');
    const transcriptionStatus = document.getElementById('transcriptionStatus');
    const transcriptionFilename = document.getElementById('transcriptionFilename');
    const transcriptionFileSize = document.getElementById('transcriptionFileSize');
    const audioPlayer = document.getElementById('transcriptionAudioPlayer');
    const errorBanner = document.getElementById('transcriptionError');
    const errorMessage = document.getElementById('errorMessage');
    
    // Hide error banner
    if (errorBanner) {
        errorBanner.style.display = 'none';
    }
    
    // Check for failed status
    if (transcription.status === 'FAILED') {
        if (errorBanner && errorMessage) {
            errorMessage.textContent = 'Unable to transcribe audio. Please try again.';
            errorBanner.style.display = 'flex';
        }
        return;
    }
    
    // Update transcription text
    if (transcriptionText) {
        transcriptionText.innerHTML = `<p>${transcription.ai_transcription || 'No transcription available'}</p>`;
    }
    
    // Update language badge
    if (transcriptionLanguage) {
        const lang = transcription.source_language || 'Unknown';
        transcriptionLanguage.textContent = `Language: ${lang.toUpperCase()}`;
    }
    
    // Update confidence badge
    if (transcriptionConfidence) {
        const confidence = transcription.confidence_score 
            ? `${(transcription.confidence_score * 100).toFixed(1)}%` 
            : 'N/A';
        transcriptionConfidence.textContent = `Confidence: ${confidence}`;
    }
    
    // Update duration badge
    if (transcriptionDuration && transcription.audio_metadata) {
        const duration = transcription.audio_metadata.duration_seconds;
        if (duration) {
            const minutes = Math.floor(duration / 60);
            const seconds = duration % 60;
            transcriptionDuration.textContent = `Duration: ${minutes}:${seconds.toString().padStart(2, '0')}`;
        } else {
            transcriptionDuration.textContent = 'Duration: N/A';
        }
    }
    
    // Update status badge
    if (transcriptionStatus) {
        transcriptionStatus.textContent = `Status: ${transcription.status}`;
        transcriptionStatus.className = `badge badge-status ${transcription.status.toLowerCase()}`;
    }
    
    // Update filename
    if (transcriptionFilename && transcription.audio_metadata) {
        transcriptionFilename.textContent = `File: ${transcription.audio_metadata.original_filename}`;
    }
    
    // Update file size
    if (transcriptionFileSize && transcription.audio_metadata) {
        const sizeBytes = transcription.audio_metadata.file_size_bytes;
        const sizeMB = (sizeBytes / (1024 * 1024)).toFixed(2);
        transcriptionFileSize.textContent = `Size: ${sizeMB} MB`;
    }
    
    // Update audio player
    if (audioPlayer && transcription.audio_metadata && transcription.audio_metadata.file_path) {
        audioPlayer.src = transcription.audio_metadata.file_path;
    }
}

// Move to specific step
function moveToStep(stepNumber) {
    // Update step indicators
    document.querySelectorAll('.step').forEach(step => {
        step.classList.remove('active');
        if (parseInt(step.dataset.step) === stepNumber) {
            step.classList.add('active');
        }
    });
    
    // Update step content
    document.querySelectorAll('.step-content').forEach(content => {
        content.classList.remove('active');
    });
    
    const targetStep = document.getElementById(`step${stepNumber}`);
    if (targetStep) {
        targetStep.classList.add('active');
    }
}
