import os
import io
import zipfile
from flask import Flask, request, send_file, render_template, jsonify
from werkzeug.utils import secure_filename
from pdf_logic import split_pdf

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB limit per upload

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/split', methods=['POST'])
def handle_split():
    if 'pdf_file' not in request.files:
        return jsonify({"error": "No hay archivo"}), 400
    
    file = request.files['pdf_file']
    if file.filename == '':
        return jsonify({"error": "No se ha seleccionado archivo"}), 400
    
    try:
        max_size = float(request.form.get('max_size', 4.0))
        input_stream = io.BytesIO(file.read())
        
        # Split logic
        parts = split_pdf(input_stream, max_size)
        
        # Create ZIP
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            base_name = os.path.splitext(secure_filename(file.filename))[0]
            for filename, content in parts:
                zip_file.writestr(f"{base_name}_{filename}", content)
        
        zip_buffer.seek(0)
        
        return send_file(
            zip_buffer,
            mimetype='application/zip',
            as_attachment=True,
            download_name=f"{base_name}_dividido.zip"
        )
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Koyeb compatible port
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
