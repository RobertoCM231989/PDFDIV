document.addEventListener('DOMContentLoaded', () => {
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('file-input');
    const fileName = document.getElementById('file-name');
    const uploadForm = document.getElementById('upload-form');
    const submitBtn = document.getElementById('submit-btn');
    const loader = document.getElementById('loader');
    const btnText = submitBtn.querySelector('.btn-text');
    const statusMsg = document.getElementById('status-message');
    const progressContainer = document.getElementById('progress-container');
    const progressBarFill = document.getElementById('progress-bar-fill');
    const progressText = document.getElementById('progress-text');

    // Drag & Drop events
    dropZone.addEventListener('click', () => fileInput.click());

    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.classList.add('drag-over');
    });

    ['dragleave', 'dragend'].forEach(type => {
        dropZone.addEventListener(type, () => {
            dropZone.classList.remove('drag-over');
        });
    });

    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.classList.remove('drag-over');
        if (e.dataTransfer.files.length) {
            fileInput.files = e.dataTransfer.files;
            updateFileName();
        }
    });

    fileInput.addEventListener('change', updateFileName);

    function updateFileName() {
        if (fileInput.files.length) {
            fileName.innerText = fileInput.files[0].name;
            fileName.style.color = '#38bdf8';
        } else {
            fileName.innerText = 'Ningún archivo seleccionado';
            fileName.style.color = '#94a3b8';
        }
    }

    // Comprehensive Job Management
    async function manageJob(formData) {
        // 1. Upload Phase
        const jobId = await uploadFile(formData);
        if (!jobId) return;

        // 2. Start SSE Progress Listening
        const progressSource = new EventSource(`/progress/${jobId}`);

        progressSource.onmessage = (event) => {
            const data = JSON.parse(event.data);

            if (data.status === 'processing') {
                progressBarFill.style.width = data.progress + '%';
                progressText.innerText = `Dividiendo PDF... ${data.progress}%`;
                btnText.innerText = 'Dividiendo...';
            } else if (data.status === 'completed') {
                progressSource.close();
                showStatus('¡Procesado completo! Iniciando descarga...', 'success');
                progressContainer.classList.add('hidden');
                triggerDownload(jobId);
                resetUI();
            } else if (data.status === 'error') {
                progressSource.close();
                showStatus('Error: ' + data.error, 'error');
                progressContainer.classList.add('hidden');
                resetUI();
            }
        };

        // 3. Trigger Processing
        await fetch(`/process/${jobId}`, { method: 'POST' });
    }

    function uploadFile(formData) {
        return new Promise((resolve) => {
            const xhr = new XMLHttpRequest();

            xhr.upload.addEventListener('progress', (e) => {
                if (e.lengthComputable) {
                    const percent = Math.round((e.loaded / e.total) * 100);
                    progressBarFill.style.width = percent + '%';
                    progressText.innerText = `Subiendo archivo... ${percent}%`;
                }
            });

            xhr.onload = () => {
                if (xhr.status === 200) {
                    const data = JSON.parse(xhr.responseText);
                    resolve(data.job_id);
                } else {
                    showStatus('Error al subir el archivo', 'error');
                    resetUI();
                    resolve(null);
                }
            };

            xhr.onerror = () => {
                showStatus('Error de red al subir', 'error');
                resetUI();
                resolve(null);
            };

            xhr.open('POST', '/upload');
            xhr.send(formData);
        });
    }

    function triggerDownload(jobId) {
        const a = document.createElement('a');
        a.href = `/download/${jobId}`;
        a.download = `${fileInput.files[0].name.split('.')[0]}_dividido.zip`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
    }

    function resetUI() {
        submitBtn.disabled = false;
        loader.style.display = 'none';
        btnText.innerText = 'Dividir y Descargar ZIP';
    }

    uploadForm.addEventListener('submit', (e) => {
        e.preventDefault();

        if (!fileInput.files.length) {
            showStatus('Por favor selecciona un archivo PDF', 'error');
            return;
        }

        const formData = new FormData(uploadForm);

        submitBtn.disabled = true;
        loader.style.display = 'block';
        btnText.innerText = 'Enviando...';
        statusMsg.classList.add('hidden');
        progressContainer.classList.remove('hidden');

        manageJob(formData);
    });

    function showStatus(msg, type) {
        statusMsg.innerText = msg;
        statusMsg.className = `status-message ${type}`;
        statusMsg.classList.remove('hidden');
    }
});
