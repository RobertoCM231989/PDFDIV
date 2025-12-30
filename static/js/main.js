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
    uploadForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        if (!fileInput.files.length) {
            showStatus('Por favor selecciona un archivo PDF', 'error');
            return;
        }

        const formData = new FormData(uploadForm);
        
        // UI Loading state
        submitBtn.disabled = true;
        loader.style.display = 'block';
        btnText.innerText = 'Procesando...';
        statusMsg.classList.add('hidden');

        try {
            const response = await fetch('/split', {
                method: 'POST',
                body: formData
            });

            if (response.ok) {
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `${fileInput.files[0].name.split('.')[0]}_dividido.zip`;
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
                showStatus('¡PDF dividido con éxito! Descargando ZIP...', 'success');
            } else {
                const errorData = await response.json();
                showStatus(errorData.error || 'Error al procesar el PDF', 'error');
            }
        } catch (error) {
            showStatus('Error de conexión con el servidor', 'error');
            console.error(error);
        } finally {
            submitBtn.disabled = false;
            loader.style.display = 'none';
            btnText.innerText = 'Dividir y Descargar ZIP';
        }
    });

    function showStatus(msg, type) {
        statusMsg.innerText = msg;
        statusMsg.className = `status-message ${type}`;
        statusMsg.classList.remove('hidden');
    }
});
