let currentSession = {
    id: null,
    name: '',
    targetTotal: 0,
    currentCount: 0,
    files: []
};

// Démarrer une nouvelle session
document.getElementById('startBtn').addEventListener('click', async function() {
    const totalPdfs = parseInt(document.getElementById('totalPdfs').value);
    const sessionName = document.getElementById('sessionName').value || 'Session sans nom';
    
    if (!totalPdfs || totalPdfs < 1) {
        alert('Veuillez entrer un nombre valide de PDFs');
        return;
    }
    
    try {
        const response = await fetch(API_URLS.createSession, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                total: totalPdfs,
                name: sessionName
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            currentSession = {
                id: data.session_id,
                name: sessionName,
                targetTotal: totalPdfs,
                currentCount: 0,
                files: []
            };
            
            showStep2();
        } else {
            showError(data.error || 'Erreur lors de la création de la session');
        }
    } catch (error) {
        console.error('Erreur détaillée:', error);
        showError('Erreur de connexion: ' + error.message);
    }
});

// Reprendre une session existante
document.getElementById('resumeBtn').addEventListener('click', async function() {
    const sessionId = document.getElementById('existingSessionId').value.trim();
    
    if (!sessionId) {
        alert('Veuillez entrer un ID de session');
        return;
    }
    
    try {
        const response = await fetch(API_URLS.getSession + sessionId);
        const data = await response.json();
        
        if (data.success) {
            currentSession = {
                id: data.session_id,
                name: data.name,
                targetTotal: data.target_total,
                currentCount: data.current_count,
                files: data.files
            };
            
            showStep2();
        } else {
            showError(data.error || 'Session non trouvée');
        }
    } catch (error) {
        console.error('Erreur détaillée:', error);
        showError('Erreur de connexion: ' + error.message);
    }
});

// Upload des fichiers
document.getElementById('uploadForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const fileInput = document.getElementById('pdf_files');
    const files = Array.from(fileInput.files);
    
    if (files.length === 0) {
        alert('Veuillez sélectionner au moins un fichier PDF');
        return;
    }
    
    const remainingSpace = currentSession.targetTotal - currentSession.currentCount;
    
    if (files.length > remainingSpace) {
        if (!confirm(`Vous avez sélectionné ${files.length} fichiers mais il ne reste que ${remainingSpace} places. Voulez-vous uploader seulement les ${remainingSpace} premiers fichiers ?`)) {
            return;
        }
        files.splice(remainingSpace);
    }
    
    document.getElementById('uploadBtn').disabled = true;
    document.getElementById('uploadStatus').classList.remove('hidden');
    document.getElementById('filesTotalProgress').textContent = files.length;
    
    for (let i = 0; i < files.length; i++) {
        const file = files[i];
        document.getElementById('currentFile').textContent = file.name;
        document.getElementById('fileProgress').textContent = i + 1;
        
        const formData = new FormData();
        formData.append('pdf_file', file);
        formData.append('session_id', currentSession.id);
        
        try {
            const response = await fetch(API_URLS.addPdf, {
                method: 'POST',
                body: formData
            });
            
            const data = await response.json();
            
            if (data.success) {
                currentSession.currentCount = data.current_count;
                currentSession.files.push(file.name);
                updateProgress();
            } else {
                console.error(`Erreur upload ${file.name}:`, data.error);
            }
        } catch (error) {
            console.error(`Erreur upload ${file.name}:`, error);
        }
    }
    
    document.getElementById('uploadBtn').disabled = false;
    document.getElementById('uploadStatus').classList.add('hidden');
    fileInput.value = '';
    
    if (currentSession.currentCount >= currentSession.targetTotal) {
        document.getElementById('finishBtn').disabled = false;
    }
});

// Terminer et lancer l'analyse
document.getElementById('finishBtn').addEventListener('click', async function() {
    if (currentSession.currentCount < currentSession.targetTotal) {
        if (!confirm(`Vous avez uploadé ${currentSession.currentCount} PDFs sur ${currentSession.targetTotal} prévus. Voulez-vous quand même lancer l'analyse ?`)) {
            return;
        }
    }
    
    showStep3();
    
    try {
        document.getElementById('analyzeCount').textContent = currentSession.currentCount;
        
        const response = await fetch(API_URLS.analyzeSession, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({session_id: currentSession.id})
        });
        
        const data = await response.json();
        
        if (data.success) {
            showStep4(data);
        } else {
            showError(data.error || 'Erreur lors de l\'analyse');
        }
    } catch (error) {
        console.error('Erreur détaillée:', error);
        showError('Erreur de connexion: ' + error.message);
    }
});

// Annuler la session
document.getElementById('cancelBtn').addEventListener('click', function() {
    if (confirm('Voulez-vous vraiment annuler cette session ? Tous les fichiers uploadés seront perdus.')) {
        resetToStep1();
    }
});

// Nouvelle session
document.getElementById('newSessionBtn').addEventListener('click', function() {
    resetToStep1();
});

// Réessayer après erreur
document.getElementById('retryBtn').addEventListener('click', function() {
    resetToStep1();
});

// Fonctions utilitaires
function showStep2() {
    document.getElementById('step1').classList.add('hidden');
    document.getElementById('step2').classList.remove('hidden');
    document.getElementById('step3').classList.add('hidden');
    document.getElementById('step4').classList.add('hidden');
    document.getElementById('errorSection').classList.add('hidden');
    
    document.getElementById('sessionIdDisplay').textContent = currentSession.id;
    document.getElementById('sessionNameDisplay').textContent = currentSession.name;
    document.getElementById('targetCount').textContent = currentSession.targetTotal;
    
    updateProgress();
    
    if (currentSession.currentCount >= currentSession.targetTotal) {
        document.getElementById('finishBtn').disabled = false;
    }
}

function showStep3() {
    document.getElementById('step1').classList.add('hidden');
    document.getElementById('step2').classList.add('hidden');
    document.getElementById('step3').classList.remove('hidden');
    document.getElementById('step4').classList.add('hidden');
    document.getElementById('errorSection').classList.add('hidden');
}

function showStep4(data) {
    document.getElementById('step1').classList.add('hidden');
    document.getElementById('step2').classList.add('hidden');
    document.getElementById('step3').classList.add('hidden');
    document.getElementById('step4').classList.remove('hidden');
    document.getElementById('errorSection').classList.add('hidden');
    
    document.getElementById('totalCount').textContent = data.total || 0;
    document.getElementById('successCount').textContent = data.success_count || 0;
    document.getElementById('failedCount').textContent = data.failed_count || 0;
    
    document.getElementById('downloadExcel').onclick = () => {
        window.location.href = API_URLS.download + data.session_id + '/excel';
    };
    
    document.getElementById('downloadCSV').onclick = () => {
        window.location.href = API_URLS.download + data.session_id + '/csv';
    };
}

function showError(message) {
    document.getElementById('step1').classList.add('hidden');
    document.getElementById('step2').classList.add('hidden');
    document.getElementById('step3').classList.add('hidden');
    document.getElementById('step4').classList.add('hidden');
    document.getElementById('errorSection').classList.remove('hidden');
    
    document.getElementById('errorMessage').textContent = message;
}

function updateProgress() {
    const current = currentSession.currentCount;
    const target = currentSession.targetTotal;
    const percent = target > 0 ? Math.round((current / target) * 100) : 0;
    
    document.getElementById('currentCount').textContent = current;
    document.getElementById('progressPercent').textContent = percent;
    document.getElementById('progressBar').style.width = percent + '%';
}

function resetToStep1() {
    currentSession = {
        id: null,
        name: '',
        targetTotal: 0,
        currentCount: 0,
        files: []
    };
    
    document.getElementById('step1').classList.remove('hidden');
    document.getElementById('step2').classList.add('hidden');
    document.getElementById('step3').classList.add('hidden');
    document.getElementById('step4').classList.add('hidden');
    document.getElementById('errorSection').classList.add('hidden');
    
    document.getElementById('totalPdfs').value = '';
    document.getElementById('sessionName').value = '';
    document.getElementById('existingSessionId').value = '';
    document.getElementById('pdf_files').value = '';
    document.getElementById('finishBtn').disabled = true;
}
