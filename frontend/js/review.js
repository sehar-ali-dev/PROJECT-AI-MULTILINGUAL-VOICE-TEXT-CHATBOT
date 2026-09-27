// Review API functions
const reviewAPI = {
    async submitReview(transcriptionId, correctedText, reviewNotes = null) {
        const body = {
            transcription_id: transcriptionId,
            corrected_text: correctedText
        };
        if (reviewNotes) {
            body.review_notes = reviewNotes;
        }
        return fetchAPI(`/transcriptions/${transcriptionId}/review`, {
            method: 'POST',
            body: JSON.stringify(body),
        });
    },

    async getReview(transcriptionId) {
        return fetchAPI(`/transcriptions/${transcriptionId}/review`);
    }
};

// Store original AI transcription for reset
let originalAITranscription = '';

// Handle STEP 3 - Human Review
document.addEventListener('DOMContentLoaded', function() {
    const toStep3Btn = document.getElementById('toStep3');
    const reviewText = document.getElementById('reviewText');
    const reviewNotes = document.getElementById('reviewNotes');
    const resetReviewBtn = document.getElementById('resetReview');
    const saveReviewBtn = document.getElementById('saveReview');
    const toStep4Btn = document.getElementById('toStep4');
    const reviewAudioPlayer = document.getElementById('reviewAudioPlayer');
    const reviewSuccessBanner = document.getElementById('reviewSuccess');
    
    // When entering STEP 3, load AI transcription
    if (toStep3Btn) {
        toStep3Btn.addEventListener('click', function() {
            // Load AI transcription into review textarea
            const aiTranscription = localStorage.getItem('current_transcription_text');
            if (reviewText && aiTranscription) {
                reviewText.value = aiTranscription;
                originalAITranscription = aiTranscription;
            }
            
            // Load audio file if available (sanitize path)
            const audioPath = localStorage.getItem('current_audio_path');
            if (reviewAudioPlayer && audioPath) {
                const cleanPath = audioPath.replace(/\\/g, '/');
                loadAudioPlayer(reviewAudioPlayer, cleanPath);
            }
            
            // Hide success banner
            if (reviewSuccessBanner) {
                reviewSuccessBanner.style.display = 'none';
            }
            
            // Disable proceed button until review is saved
            if (toStep4Btn) {
                toStep4Btn.disabled = true;
            }
            
            moveToStep(3);
        });
    }
    
    // Reset to original AI text
    if (resetReviewBtn) {
        resetReviewBtn.addEventListener('click', function() {
            if (reviewText && originalAITranscription) {
                reviewText.value = originalAITranscription;
            }
        });
    }
    
    // Save and submit review
    if (saveReviewBtn) {
        saveReviewBtn.addEventListener('click', async function() {
            const transcriptionId = localStorage.getItem('current_transcription_id');
            const correctedText = reviewText.value;
            const notes = reviewNotes ? reviewNotes.value : null;
            
            if (!transcriptionId) {
                alert('No transcription to review. Please complete Step 2 first.');
                return;
            }
            
            if (!correctedText || correctedText.trim() === '') {
                alert('Please provide corrected transcription text.');
                return;
            }
            
            try {
                // Disable button and show loading state
                saveReviewBtn.disabled = true;
                saveReviewBtn.textContent = 'Saving...';
                
                // Submit review
                const review = await reviewAPI.submitReview(
                    parseInt(transcriptionId),
                    correctedText,
                    notes
                );
                
                // Store review data for next steps
                localStorage.setItem('current_review_id', review.id);
                localStorage.setItem('reviewed_transcription', correctedText);
                
                // Show success banner
                if (reviewSuccessBanner) {
                    reviewSuccessBanner.style.display = 'flex';
                }
                
                // Enable proceed to translation button
                if (toStep4Btn) {
                    toStep4Btn.disabled = false;
                }
                
                alert('Review saved successfully!');
            } catch (error) {
                alert('Failed to save review: ' + error.message);
            } finally {
                saveReviewBtn.disabled = false;
                saveReviewBtn.textContent = 'Save & Submit Review';
            }
        });
    }
    
    // Proceed to translation
    if (toStep4Btn) {
        toStep4Btn.addEventListener('click', function() {
            // Ensure reviewed transcription is saved
            const reviewedText = reviewText.value;
            localStorage.setItem('reviewed_transcription', reviewedText);
            
            moveToStep(4);
        });
    }
});

// Helper function to load audio player with proper URL handling
function loadAudioPlayer(audioElement, filePath) {
    if (!audioElement || !filePath) return;
    
    // Sanitize path: replace backslashes with forward slashes
    const cleanPath = filePath.replace(/\\/g, '/');
    
    // Build full URL if path is relative
    let fullUrl = cleanPath;
    if (cleanPath.startsWith('/')) {
        fullUrl = `http://127.0.0.1:8000${cleanPath}`;
    }
    
    audioElement.src = fullUrl;
    audioElement.load();
    
    // Add event listener for loadedmetadata to ensure duration renders
    audioElement.addEventListener('loadedmetadata', function() {
        console.log('Audio loaded, duration:', audioElement.duration);
    }, { once: true });
    
    // Handle load errors
    audioElement.addEventListener('error', function(e) {
        console.error('Audio load error:', e);
    }, { once: true });
}

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
