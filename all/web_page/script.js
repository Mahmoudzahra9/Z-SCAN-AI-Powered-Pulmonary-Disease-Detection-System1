document.addEventListener('DOMContentLoaded', () => {
    const API_BASE_URL = 'http://127.0.0.1:5000';
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('file-input');
    const dropContent = document.getElementById('drop-content');
    const previewContainer = document.getElementById('preview-container');
    const imagePreview = document.getElementById('image-preview');
    const removeBtn = document.getElementById('remove-btn');
    const analyzeBtn = document.getElementById('analyze-btn');
    const loadingState = document.getElementById('loading-state');
    const resultContainer = document.getElementById('result-container');
    const scanner = document.getElementById('scanner');
    
    // Result elements
    const diagnosisBadge = document.getElementById('diagnosis-badge');
    const diagnosisIcon = document.getElementById('diagnosis-icon');
    const diagnosisText = document.getElementById('diagnosis-text');
    const confidenceVal = document.getElementById('confidence-val');
    const confidenceBar = document.getElementById('confidence-bar');

    let currentFile = null;

    // Drag and Drop handlers
    dropZone.addEventListener('click', () => {
        if (!currentFile) fileInput.click();
    });

    ['dragover', 'dragenter'].forEach(evt => {
        dropZone.addEventListener(evt, (e) => {
            e.preventDefault();
            dropZone.classList.add('dragover');
        });
    });

    ['dragleave', 'dragend', 'drop'].forEach(evt => {
        dropZone.addEventListener(evt, (e) => {
            e.preventDefault();
            dropZone.classList.remove('dragover');
        });
    });

    dropZone.addEventListener('drop', (e) => {
        if (e.dataTransfer.files.length) {
            handleFile(e.dataTransfer.files[0]);
        }
    });

    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length) {
            handleFile(e.target.files[0]);
        }
    });

    removeBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        clearFile();
    });

    function handleFile(file) {
        if (!file.type.startsWith('image/')) {
            alert('Please select an image file (JPEG, PNG, etc).');
            return;
        }

        currentFile = file;
        const reader = new FileReader();
        reader.onload = (e) => {
            imagePreview.src = e.target.result;
            dropContent.classList.add('hidden');
            previewContainer.classList.remove('hidden');
            analyzeBtn.disabled = false;
            
            // Re-hide results if present
            resultContainer.classList.add('hidden');
        };
        reader.readAsDataURL(file);
    }

    function clearFile() {
        currentFile = null;
        fileInput.value = '';
        imagePreview.src = '';
        dropContent.classList.remove('hidden');
        previewContainer.classList.add('hidden');
        analyzeBtn.disabled = true;
        resultContainer.classList.add('hidden');
    }

    analyzeBtn.addEventListener('click', async () => {
        if (!currentFile) return;

        // UI updates for loading
        analyzeBtn.disabled = true;
        loadingState.classList.remove('hidden');
        resultContainer.classList.add('hidden');
        scanner.classList.remove('hidden'); // Show scanner lazers

        const formData = new FormData();
        formData.append('file', currentFile);

        try {
            // Actual backend URL running locally
            const response = await fetch(`${API_BASE_URL}/predict`, {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                throw new Error(`Server responded with status ${response.status}`);
            }

            const data = await response.json();
            
            if (data.error) {
                throw new Error(data.error);
            }

            displayResults(data);

        } catch (error) {
            console.error('API Error:', error);
            alert(`Failed to analyze image. Ensure the Python backend is running on ${API_BASE_URL}.\n\nError: ${error.message}`);
        } finally {
            loadingState.classList.add('hidden');
            scanner.classList.add('hidden'); // Hide scanner lazers
            analyzeBtn.disabled = false; 
        }
    });

    function displayResults(data) {
        const prediction = data.prediction;
        const conf = data.confidence;
        // Classes: COVID-19, NORMAL, PNEUMONIA, TUBERCULOSIS
        resultContainer.classList.remove('hidden');

        const isNormal = prediction.toUpperCase() === 'NORMAL';
        
        // Reset badge styles
        diagnosisBadge.className = 'diagnosis-badge';
        diagnosisBadge.classList.add(isNormal ? 'diagnosis-normal' : 'diagnosis-danger');

        // Set Icon
        if (isNormal) {
            diagnosisIcon.className = 'fa-solid fa-circle-check';
        } else if (prediction === 'COVID-19') {
            diagnosisIcon.className = 'fa-solid fa-virus-covid';
        } else if (prediction === 'PNEUMONIA') {
            diagnosisIcon.className = 'fa-solid fa-lungs-virus';
        } else if (prediction === 'TUBERCULOSIS') {
            diagnosisIcon.className = 'fa-solid fa-lungs';
        } else if (prediction === 'LUNG CANCER') {
            diagnosisIcon.className = 'fa-solid fa-ribbon';
        } else if (prediction === 'PNEUMOTHORAX') {
            diagnosisIcon.className = 'fa-solid fa-lungs';
        } else {
            diagnosisIcon.className = 'fa-solid fa-triangle-exclamation';
        }

        diagnosisText.textContent = prediction;
        
        // Handle confidence (assuming max 1.0 or 100)
        let percent = conf <= 1 ? (conf * 100) : conf;
        percent = Math.round(percent * 10) / 10; // 1 decimal

        confidenceVal.textContent = `${percent}%`;
        
        // Reset width to trigger animation
        confidenceBar.style.width = '0%';
        setTimeout(() => {
            confidenceBar.style.width = `${percent}%`;
            // Change bar color based on confidence and diagnosis
            if (percent > 85) {
                confidenceBar.style.background = isNormal 
                    ? 'linear-gradient(90deg, #10b981, #34d399)' 
                    : 'linear-gradient(90deg, #ef4444, #f87171)';
            } else {
                confidenceBar.style.background = 'linear-gradient(90deg, #f59e0b, #fbbf24)'; // Warning color if not so confident
            }
        }, 50);

        // Populate new fields
        const medInfoContainer = document.getElementById('medical-info-container');
        if (data.advice_en || data.advice_ar) {
            medInfoContainer.classList.remove('hidden');
            
            document.getElementById('advice-en').textContent = data.advice_en || '';
            document.getElementById('advice-ar').textContent = data.advice_ar || '';
            
            document.getElementById('diet-en').textContent = data.diet_en || '';
            document.getElementById('diet-ar').textContent = data.diet_ar || '';
            
            document.getElementById('doctors-en').textContent = data.doctors_en || '';
            document.getElementById('doctors-ar').textContent = data.doctors_ar || '';
            
            const videoList = document.getElementById('video-list');
            videoList.innerHTML = '';
            if (data.videos && data.videos.length > 0) {
                data.videos.forEach(video => {
                    const li = document.createElement('li');
                    li.innerHTML = `<a href="${video.url}" target="_blank"><i class="fa-solid fa-play"></i> ${video.title}</a>`;
                    videoList.appendChild(li);
                });
                document.querySelector('.video-card').classList.remove('hidden');
            } else {
                document.querySelector('.video-card').classList.add('hidden');
            }
        } else {
            medInfoContainer.classList.add('hidden');
        }
    }

    // Check backend connection on load
    async function checkBackend() {
        try {
            const response = await fetch(API_BASE_URL);
            if (response.ok) {
                console.log('Backend connected successfully');
                // Could update UI to show "Connected" status
            }
        } catch (e) {
            console.warn('Backend not reachable on initial load. Make sure to run start_app.bat');
        }
    }
    
    checkBackend();
});
