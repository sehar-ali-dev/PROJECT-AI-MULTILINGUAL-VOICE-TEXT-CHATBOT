// Transcription API functions
const transcriptionAPI = {
    async transcribe(audioId, sourceLanguage = null) {
        const body = {
            audio_id: audioId
        };
        if (sourceLanguage) {
            body.source_language = sourceLanguage;
        }
        return fetchAPI('/speech/transcribe', {
            method: 'POST',
            body: JSON.stringify(body),
        });
    },

    async getTranscription(transcriptionId) {
        return fetchAPI(`/speech/transcriptions/${transcriptionId}`);
    },

    async listTranscriptions() {
        return fetchAPI('/speech/transcriptions');
    }
};

// Handle STEP 3 - Human Review (moved from recorder.js to keep separation)
document.addEventListener('DOMContentLoaded', function() {
    const toStep3Btn = document.getElementById('toStep3');
    const reviewText = document.getElementById('reviewText');
    
    if (toStep3Btn) {
        toStep3Btn.addEventListener('click', function() {
            // Load AI transcription into review textarea
            const aiTranscription = localStorage.getItem('current_transcription_text');
            if (reviewText && aiTranscription) {
                reviewText.value = aiTranscription;
            }
            
            moveToStep(3);
        });
    }
    
    // Handle reset button
    const resetReviewBtn = document.getElementById('resetReview');
    if (resetReviewBtn) {
        resetReviewBtn.addEventListener('click', function() {
            const aiTranscription = localStorage.getItem('current_transcription_text');
            if (reviewText && aiTranscription) {
                reviewText.value = aiTranscription;
            }
        });
    }
    
    // Handle proceed to translation
    const toStep4Btn = document.getElementById('toStep4');
    if (toStep4Btn) {
        toStep4Btn.addEventListener('click', function() {
            // Save reviewed transcription
            const reviewedText = reviewText.value;
            localStorage.setItem('reviewed_transcription', reviewedText);
            
            moveToStep(4);
        });
    }
});

// Move to specific step (helper function)
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
