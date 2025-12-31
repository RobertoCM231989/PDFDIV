import os
import io
import zipfile
import uuid
import time
import threading
from flask import Flask, request, send_file, render_template, jsonify, Response
from werkzeug.utils import secure_filename
from pdf_logic import split_pdf

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB limit
app.config['UPLOAD_FOLDER'] = 'temp_uploads'

# In-memory job storage (Note: in production with multiple workers, 
# you'd use Redis or similar. For Koyeb 1-worker, this is OK)
jobs = {}

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'pdf_file' not in request.files:
        return jsonify({"error": "No hay archivo"}), 400
    
    file = request.files['pdf_file']
    if file.filename == '':
        return jsonify({"error": "No se ha seleccionado archivo"}), 400
    
    job_id = str(uuid.uuid4())
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], f"{job_id}_{filename}")
    file.save(filepath)
    
    jobs[job_id] = {
        'status': 'uploaded',
        'progress': 0,
        'filename': filename,
        'filepath': filepath,
        'result': None,
        'max_size': float(request.form.get('max_size', 4.0))
    }
    
    return jsonify({"job_id": job_id})

@app.route('/progress/<job_id>')
def progress(job_id):
    job = jobs.get(job_id)
    if not job:
        return jsonify({"error": "Job no encontrado"}), 404
    
    return jsonify({
        'status': job['status'],
        'progress': job['progress'],
        'error': job.get('error_msg')
    })

@app.route('/process/<job_id>', methods=['POST'])
def process(job_id):
    job = jobs.get(job_id)
    if not job:
        return jsonify({"error": "Job no encontrado"}), 404
    
    def run_split():
        try:
            job['status'] = 'processing'
            
            def update_progress(p):
                job['progress'] = p
                
            with open(job['filepath'], 'rb') as f:
                input_stream = io.BytesIO(f.read())
                parts = split_pdf(input_stream, job['max_size'], progress_callback=update_progress)
            
            # Create ZIP in memory
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                base_name = os.path.splitext(job['filename'])[0]
                for filename, content in parts:
                    zip_file.writestr(f"{base_name}_{filename}", content)
            
            job['result'] = zip_buffer.getvalue()
            job['status'] = 'completed'
            job['progress'] = 100
            
            # Cleanup temp file
            if os.path.exists(job['filepath']):
                os.remove(job['filepath'])
                
        except Exception as e:
            job['status'] = 'error'
            job['error_msg'] = str(e)
            print(f"ERROR in job {job_id}: {str(e)}")

    thread = threading.Thread(target=run_split)
    thread.start()
    return jsonify({"status": "started"})

@app.route('/download/<job_id>')
def download(job_id):
    job = jobs.get(job_id)
    if not job or job['status'] != 'completed' or not job['result']:
        return "Archivo no listo o expirado", 404
    
    base_name = os.path.splitext(job['filename'])[0]
    return send_file(
        io.BytesIO(job['result']),
        mimetype='application/zip',
        as_attachment=True,
        download_name=f"{base_name}_dividido.zip"
    )

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, threaded=True)
