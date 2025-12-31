document.addEventListener('DOMContentLoaded', () => {
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('file-input');
    const fileName = document.getElementById('file-name');
    const uploadForm = document.getElementById('upload-form');
    const submitBtn = document.getElementById('submit-btn');
    const loader = document.getElementById('loader');
    const btnText = submitBtn.querySelector('.btn-text');
    const statusMsg = document.getElementById('status-message');

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

    // Form submission
    uploadForm.addEventListener('submit', (e) => {
        e.preventDefault();

        if (!fileInput.files.length) {
            showStatus('Por favor selecciona un archivo PDF', 'error');
            return;
        }

        const formData = new FormData(uploadForm);

        // UI Loading state
        submitBtn.disabled = true;
        loader.style.display = 'block';
        btnText.innerText = 'Subiendo...';
        statusMsg.classList.add('hidden');

        // Reset and show progress bar
        const progressContainer = document.getElementById('progress-container');
        const progressBarFill = document.getElementById('progress-bar-fill');
        const progressText = document.getElementById('progress-text');

        progressContainer.classList.remove('hidden');
        progressBarFill.style.width = '0%';
        progressText.innerText = 'Preparando subida... 0%';

        const xhr = new XMLHttpRequest();

        // Track upload progress
        xhr.upload.addEventListener('progress', (e) => {
            if (e.lengthComputable) {
                const percent = Math.round((e.loaded / e.total) * 100);
                progressBarFill.style.width = percent + '%';
                progressText.innerText = `Subiendo... ${percent}%`;

                if (percent === 100) {
                    progressText.innerText = 'Subida completa. Procesando PDF...';
                    btnText.innerText = 'Procesando...';
                }
            }
        });

        xhr.onload = function () {
            submitBtn.disabled = false;
            loader.style.display = 'none';
            btnText.innerText = 'Dividir y Descargar ZIP';

            if (xhr.status === 200) {
                // Success: Get blob and download
                const blob = new Blob([xhr.response], { type: 'application/zip' });
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `${fileInput.files[0].name.split('.')[0]}_dividido.zip`;
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
                showStatus('¡PDF dividido con éxito! Descargando ZIP...', 'success');
                progressContainer.classList.add('hidden');
            } else {
                // Error handling
                try {
                    const errorData = JSON.parse(xhr.responseText);
                    showStatus(errorData.error || 'Error al procesar el PDF', 'error');
                } catch (e) {
                    showStatus('Error inesperado en el servidor', 'error');
                }
                progressContainer.classList.add('hidden');
            }
        };

        xhr.onerror = function () {
            submitBtn.disabled = false;
            loader.style.display = 'none';
            btnText.innerText = 'Dividir y Descargar ZIP';
            showStatus('Error de conexión con el servidor', 'error');
            progressContainer.classList.add('hidden');
        };

        xhr.open('POST', '/split');
        xhr.responseType = 'blob';
        xhr.send(formData);
    });

    function showStatus(msg, type) {
        statusMsg.innerText = msg;
        statusMsg.className = `status-message ${type}`;
        statusMsg.classList.remove('hidden');
    }
});
