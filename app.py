from flask import Flask, render_template_string, request, jsonify
import os
from werkzeug.utils import secure_filename
 
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB
app.config['UPLOAD_FOLDER'] = '/tmp/media_uploader'
 
# Upload qovluğu yaratdir
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
 
# İcazəli fayl tipleri
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif', 'mp4', 'mp3', 'webm', 'wav', 'm4a'}
 
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
 
# Frontend HTML + CSS + JavaScript
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="az">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>📸 Media Yükləyici</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
 
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
            display: flex;
            align-items: center;
            justify-content: center;
        }
 
        .container {
            background: white;
            border-radius: 16px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            max-width: 600px;
            width: 100%;
            padding: 40px;
        }
 
        h1 {
            color: #333;
            margin-bottom: 10px;
            font-size: 28px;
            text-align: center;
        }
 
        .subtitle {
            color: #666;
            margin-bottom: 30px;
            font-size: 14px;
            text-align: center;
        }
 
        .upload-zone {
            border: 2px dashed #667eea;
            background: #f8f9ff;
            border-radius: 12px;
            padding: 30px;
            cursor: pointer;
            transition: all 0.3s ease;
            text-align: center;
        }
 
        .upload-zone:hover {
            background: #f0f2ff;
            border-color: #764ba2;
        }
 
        .upload-zone.drag-over {
            background: #e8ebff;
            border-color: #764ba2;
            transform: scale(1.02);
        }
 
        .upload-zone p {
            color: #667eea;
            font-weight: 500;
            margin-bottom: 10px;
        }
 
        .upload-zone small {
            color: #999;
        }
 
        input[type="file"] {
            display: none;
        }
 
        .loading {
            display: none;
            color: #667eea;
            font-size: 14px;
            margin-top: 10px;
            text-align: center;
        }
 
        .stats {
            margin-top: 20px;
            padding: 15px;
            background: #f8f9ff;
            border-radius: 8px;
            font-size: 13px;
            color: #666;
            text-align: center;
        }
 
        .gallery {
            margin-top: 40px;
        }
 
        .gallery-title {
            font-size: 18px;
            color: #333;
            margin-bottom: 20px;
            font-weight: 600;
        }
 
        .gallery-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
            gap: 15px;
            max-height: 400px;
            overflow-y: auto;
        }
 
        .gallery-item {
            position: relative;
            border-radius: 8px;
            overflow: hidden;
            background: #f5f5f5;
            aspect-ratio: 1;
            display: flex;
            align-items: center;
            justify-content: center;
        }
 
        .gallery-item img,
        .gallery-item video {
            width: 100%;
            height: 100%;
            object-fit: cover;
        }
 
        .gallery-item.audio {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            font-size: 40px;
        }
 
        .gallery-item .delete-btn {
            position: absolute;
            top: 5px;
            right: 5px;
            background: rgba(255,0,0,0.9);
            color: white;
            border: none;
            border-radius: 50%;
            width: 28px;
            height: 28px;
            cursor: pointer;
            font-size: 16px;
            display: none;
            z-index: 10;
        }
 
        .gallery-item:hover .delete-btn {
            display: block;
        }
 
        .error {
            background: #fee;
            color: #c33;
            padding: 12px;
            border-radius: 8px;
            margin-top: 10px;
            font-size: 14px;
            display: none;
        }
 
        @media (max-width: 600px) {
            .container {
                padding: 20px;
            }
 
            h1 {
                font-size: 22px;
            }
 
            .gallery-grid {
                grid-template-columns: repeat(auto-fill, minmax(80px, 1fr));
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>📸 Media Yükləyici</h1>
        <p class="subtitle">Şəkil, video və səsi asanlıqla yüklə</p>
 
        <div class="upload-zone" id="uploadZone">
            <p>💾 Faylları bura sürükləyib burax</p>
            <small>və ya kliklə faylları seçmək üçün</small>
            <input type="file" id="fileInput" accept="image/*,video/*,audio/*" multiple>
        </div>
 
        <div class="loading" id="loading">⏳ Yüklənir...</div>
        <div class="error" id="error"></div>
 
        <div class="stats">
            📊 Yüklənmiş fayllar: <span id="total">0</span>
        </div>
 
        <div class="gallery">
            <div class="gallery-title">Galereya</div>
            <div class="gallery-grid" id="gallery"></div>
        </div>
    </div>
 
    <script>
        const uploadZone = document.getElementById('uploadZone');
        const fileInput = document.getElementById('fileInput');
        const gallery = document.getElementById('gallery');
        const loading = document.getElementById('loading');
        const error = document.getElementById('error');
 
        // Sürükləyib burax
        uploadZone.addEventListener('click', () => fileInput.click());
 
        uploadZone.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadZone.classList.add('drag-over');
        });
 
        uploadZone.addEventListener('dragleave', () => {
            uploadZone.classList.remove('drag-over');
        });
 
        uploadZone.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadZone.classList.remove('drag-over');
            handleFiles(e.dataTransfer.files);
        });
 
        fileInput.addEventListener('change', (e) => {
            handleFiles(e.target.files);
        });
 
        function handleFiles(files) {
            Array.from(files).forEach(file => {
                const formData = new FormData();
                formData.append('file', file);
 
                loading.style.display = 'block';
                error.style.display = 'none';
 
                fetch('/upload', {
                    method: 'POST',
                    body: formData
                })
                .then(res => res.json())
                .then(data => {
                    if (data.success) {
                        loadGallery();
                    } else {
                        showError(data.error);
                    }
                    loading.style.display = 'none';
                })
                .catch(err => {
                    showError(err.message);
                    loading.style.display = 'none';
                });
            });
        }
 
        function showError(msg) {
            error.textContent = '❌ Xəta: ' + msg;
            error.style.display = 'block';
        }
 
        function loadGallery() {
            fetch('/gallery')
                .then(res => res.json())
                .then(data => {
                    gallery.innerHTML = '';
                    document.getElementById('total').textContent = data.total;
 
                    data.files.forEach(file => {
                        const item = document.createElement('div');
                        item.className = 'gallery-item';
 
                        if (file.type === 'image') {
                            item.innerHTML = `
                                <img src="/download/${file.name}">
                                <button class="delete-btn" onclick="deleteFile('${file.name}')">×</button>
                            `;
                        } else if (file.type === 'video') {
                            item.innerHTML = `
                                <video><source src="/download/${file.name}"></video>
                                <button class="delete-btn" onclick="deleteFile('${file.name}')">×</button>
                            `;
                        } else {
                            item.classList.add('audio');
                            item.innerHTML = `
                                🎵
                                <button class="delete-btn" onclick="deleteFile('${file.name}')">×</button>
                            `;
                        }
 
                        gallery.appendChild(item);
                    });
                });
        }
 
        function deleteFile(filename) {
            if (confirm('Silmək istəsən?')) {
                fetch(`/delete/${filename}`, { method: 'DELETE' })
                    .then(() => loadGallery());
            }
        }
 
        loadGallery();
    </script>
</body>
</html>
'''
 
@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)
 
@app.route('/upload', methods=['POST'])
def upload():
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'Fayl seçilməyib'})
 
        file = request.files['file']
 
        if file.filename == '':
            return jsonify({'success': False, 'error': 'Boş fayl'})
 
        if not allowed_file(file.filename):
            return jsonify({'success': False, 'error': 'Fayl tipi dəstəklənmir'})
 
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
 
        return jsonify({'success': True, 'filename': filename})
 
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})
 
@app.route('/gallery')
def get_gallery():
    try:
        files = []
        upload_folder = app.config['UPLOAD_FOLDER']
 
        if os.path.exists(upload_folder):
            for filename in os.listdir(upload_folder):
                filepath = os.path.join(upload_folder, filename)
                if os.path.isfile(filepath):
                    ext = filename.rsplit('.', 1)[1].lower()
                    if ext in {'jpg', 'jpeg', 'png', 'gif'}:
                        file_type = 'image'
                    elif ext in {'mp4', 'webm'}:
                        file_type = 'video'
                    else:
                        file_type = 'audio'
 
                    files.append({
                        'name': filename,
                        'type': file_type
                    })
 
        return jsonify({'files': files, 'total': len(files)})
 
    except Exception as e:
        return jsonify({'error': str(e)})
 
@app.route('/download/<filename>')
def download(filename):
    try:
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(filename))
        if os.path.exists(filepath):
            return open(filepath, 'rb').read()
        return 'Not found', 404
    except:
        return 'Error', 500
 
@app.route('/delete/<filename>', methods=['DELETE'])
def delete(filename):
    try:
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(filename))
        if os.path.exists(filepath):
            os.remove(filepath)
            return jsonify({'success': True})
        return jsonify({'success': False, 'error': 'Fayl tapılmadı'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})
 
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
 
 
