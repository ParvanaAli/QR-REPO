from flask import Flask, render_template_string, request, jsonify
import os
from werkzeug.utils import secure_filename
 
app = Flask(__name__)
 
# 1GB üçün artırıldı (əvvəl 100MB idi)
app.config['MAX_CONTENT_LENGTH'] = 1 * 1024 * 1024 * 1024  # 1GB
app.config['UPLOAD_FOLDER'] = '/tmp/media_uploader'
 
# Upload qovluğu yaratdir
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
 
# İcazəli fayl tipleri
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif', 'mp4', 'webm', 'mov', 'avi', 'mkv', 'mp3', 'wav', 'm4a', 'aac'}
 
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
 
# WEDDING THEME - GELIN BƏZƏYİ
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="az">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>💕 Wedding Day</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
 
        body {
            font-family: 'Georgia', 'Garamond', serif;
            background: linear-gradient(135deg, #f5ede3 0%, #e8dcc8 50%, #f0e6d8 100%);
            min-height: 100vh;
            padding: 20px;
            display: flex;
            align-items: center;
            justify-content: center;
            position: relative;
            overflow-x: hidden;
        }
 
        /* Wedding Day - Kölgə Yazı */
        body::before {
            content: "Wedding Day";
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            font-size: 120px;
            font-weight: bold;
            color: rgba(255, 255, 255, 0.08);
            white-space: nowrap;
            z-index: 0;
            letter-spacing: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.05);
            font-family: 'Georgia', serif;
            pointer-events: none;
        }
 
        .container {
            background: rgba(255, 252, 248, 0.95);
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(200, 150, 120, 0.2);
            max-width: 700px;
            width: 100%;
            padding: 50px 40px;
            z-index: 1;
            position: relative;
            backdrop-filter: blur(10px);
            border: 2px solid rgba(220, 180, 150, 0.3);
        }
 
        .heart-header {
            text-align: center;
            margin-bottom: 30px;
            animation: heartbeat 1.5s ease-in-out infinite;
        }
 
        .heart-header h1 {
            font-size: 80px;
            margin-bottom: 15px;
            filter: drop-shadow(0 2px 4px rgba(0,0,0,0.1));
        }
 
        .heart-header p {
            color: #c9896b;
            font-size: 18px;
            font-style: italic;
            letter-spacing: 2px;
            font-weight: 300;
        }
 
        @keyframes heartbeat {
            0%, 100% { transform: scale(1); }
            25% { transform: scale(1.05); }
            50% { transform: scale(1); }
        }
 
        .upload-zone {
            border: 3px dashed #d4a574;
            background: linear-gradient(135deg, rgba(245, 237, 227, 0.8) 0%, rgba(232, 220, 200, 0.5) 100%);
            border-radius: 15px;
            padding: 40px;
            cursor: pointer;
            transition: all 0.4s ease;
            text-align: center;
            position: relative;
            overflow: hidden;
        }
 
        .upload-zone::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: radial-gradient(circle at center, rgba(220, 180, 150, 0.05) 0%, transparent 70%);
            pointer-events: none;
        }
 
        .upload-zone:hover {
            background: linear-gradient(135deg, rgba(240, 230, 220, 0.9) 0%, rgba(225, 210, 190, 0.7) 100%);
            border-color: #c9896b;
            box-shadow: 0 10px 30px rgba(200, 150, 120, 0.15);
            transform: scale(1.02);
        }
 
        .upload-zone.drag-over {
            background: linear-gradient(135deg, rgba(235, 220, 205, 0.95) 0%, rgba(220, 200, 180, 0.8) 100%);
            border-color: #b8755f;
            box-shadow: 0 15px 40px rgba(200, 150, 120, 0.25);
            transform: scale(1.05);
        }
 
        .upload-zone p {
            color: #c9896b;
            font-weight: 600;
            margin-bottom: 10px;
            font-size: 18px;
            letter-spacing: 0.5px;
        }
 
        .upload-zone small {
            color: #a67c5f;
            font-size: 13px;
            display: block;
            margin-top: 8px;
        }
 
        input[type="file"] {
            display: none;
        }
 
        .loading {
            display: none;
            color: #c9896b;
            font-size: 14px;
            margin-top: 15px;
            text-align: center;
            animation: pulse 1.5s ease-in-out infinite;
        }
 
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.6; }
        }
 
        .stats {
            margin-top: 25px;
            padding: 20px;
            background: linear-gradient(135deg, rgba(245, 237, 227, 0.7) 0%, rgba(240, 230, 220, 0.5) 100%);
            border-radius: 12px;
            font-size: 14px;
            color: #8b6f47;
            text-align: center;
            border-left: 4px solid #d4a574;
            font-weight: 500;
        }
 
        .gallery {
            margin-top: 40px;
        }
 
        .gallery-title {
            font-size: 20px;
            color: #8b6f47;
            margin-bottom: 20px;
            font-weight: 600;
            letter-spacing: 1px;
            border-bottom: 2px solid #e8dcc8;
            padding-bottom: 10px;
        }
 
        .gallery-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
            gap: 15px;
            max-height: 450px;
            overflow-y: auto;
            padding: 5px;
        }
 
        .gallery-grid::-webkit-scrollbar {
            width: 6px;
        }
 
        .gallery-grid::-webkit-scrollbar-track {
            background: #f5ede3;
            border-radius: 3px;
        }
 
        .gallery-grid::-webkit-scrollbar-thumb {
            background: #d4a574;
            border-radius: 3px;
        }
 
        .gallery-grid::-webkit-scrollbar-thumb:hover {
            background: #c9896b;
        }
 
        .gallery-item {
            position: relative;
            border-radius: 12px;
            overflow: hidden;
            background: linear-gradient(135deg, #f5ede3 0%, #e8dcc8 100%);
            aspect-ratio: 1;
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 0 5px 15px rgba(200, 150, 120, 0.15);
            transition: all 0.3s ease;
            border: 2px solid rgba(220, 180, 150, 0.2);
        }
 
        .gallery-item:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 25px rgba(200, 150, 120, 0.25);
            border-color: rgba(200, 150, 120, 0.5);
        }
 
        .gallery-item img,
        .gallery-item video {
            width: 100%;
            height: 100%;
            object-fit: cover;
        }
 
        .gallery-item.audio {
            background: linear-gradient(135deg, #d4a574 0%, #c9896b 100%);
            color: white;
            font-size: 50px;
            text-shadow: 0 2px 4px rgba(0,0,0,0.2);
        }
 
        .gallery-item .delete-btn {
            position: absolute;
            top: 8px;
            right: 8px;
            background: rgba(220, 100, 100, 0.95);
            color: white;
            border: none;
            border-radius: 50%;
            width: 32px;
            height: 32px;
            cursor: pointer;
            font-size: 18px;
            display: none;
            z-index: 10;
            transition: all 0.2s ease;
            box-shadow: 0 2px 8px rgba(0,0,0,0.2);
        }
 
        .gallery-item .delete-btn:hover {
            background: rgba(200, 80, 80, 1);
            transform: scale(1.1);
        }
 
        .gallery-item:hover .delete-btn {
            display: block;
        }
 
        .error {
            background: linear-gradient(135deg, rgba(220, 150, 150, 0.2) 0%, rgba(200, 120, 120, 0.15) 100%);
            color: #a8524f;
            padding: 15px;
            border-radius: 10px;
            margin-top: 15px;
            font-size: 14px;
            display: none;
            border-left: 4px solid #d8888a;
        }
 
        .success {
            background: linear-gradient(135deg, rgba(150, 200, 150, 0.2) 0%, rgba(120, 180, 120, 0.15) 100%);
            color: #4a8f4e;
            padding: 15px;
            border-radius: 10px;
            margin-top: 15px;
            font-size: 14px;
            display: none;
            border-left: 4px solid #7cbe7f;
        }
 
        @media (max-width: 600px) {
            .container {
                padding: 30px 20px;
            }
 
            .heart-header h1 {
                font-size: 60px;
            }
 
            .heart-header p {
                font-size: 14px;
            }
 
            body::before {
                font-size: 60px;
                letter-spacing: 5px;
            }
 
            .gallery-grid {
                grid-template-columns: repeat(auto-fill, minmax(100px, 1fr));
            }
 
            .upload-zone {
                padding: 25px;
            }
 
            .upload-zone p {
                font-size: 16px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="heart-header">
            <h1>💕</h1>
            <p>Anımızı Saxla</p>
        </div>
 
        <div class="upload-zone" id="uploadZone">
            <p>💌 Faylları bura sürükləyib burax</p>
            <small>Şəkil, Video (3 saat qədər), Səs - hamısı dəstəklənir</small>
            <input type="file" id="fileInput" accept="image/*,video/*,audio/*" multiple>
        </div>
 
        <div class="loading" id="loading">⏳ Yüklənir... (böyük fayllar üçün vaxt ala bilər)</div>
        <div class="error" id="error"></div>
        <div class="success" id="success"></div>
 
        <div class="stats">
            💝 Yüklənmiş Anılar: <span id="total">0</span>
        </div>
 
        <div class="gallery">
            <div class="gallery-title">📸 Galereya</div>
            <div class="gallery-grid" id="gallery"></div>
        </div>
    </div>
 
    <script>
        const uploadZone = document.getElementById('uploadZone');
        const fileInput = document.getElementById('fileInput');
        const gallery = document.getElementById('gallery');
        const loading = document.getElementById('loading');
        const error = document.getElementById('error');
        const success = document.getElementById('success');
 
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
                // Fayl ölçüsü yoxla (1GB)
                if (file.size > 1024 * 1024 * 1024) {
                    showError('❌ Fayl çox böyükdür (Max 1GB)');
                    return;
                }
 
                const formData = new FormData();
                formData.append('file', file);
 
                loading.style.display = 'block';
                error.style.display = 'none';
                success.style.display = 'none';
 
                // Böyük fayllar üçün timeout artır (30 dəqiqə)
                const timeout = setTimeout(() => {
                    showError('❌ Upload vaxt limitinə çatdı. Kiçik fayl yoxlayın.');
                    loading.style.display = 'none';
                }, 30 * 60 * 1000);
 
                fetch('/upload', {
                    method: 'POST',
                    body: formData,
                    timeout: 30 * 60 * 1000
                })
                .then(res => {
                    clearTimeout(timeout);
                    return res.json();
                })
                .then(data => {
                    loading.style.display = 'none';
                    if (data.success) {
                        showSuccess('✅ ' + file.name + ' uğurla yükləndi!');
                        loadGallery();
                    } else {
                        showError('❌ Xəta: ' + data.error);
                    }
                })
                .catch(err => {
                    clearTimeout(timeout);
                    loading.style.display = 'none';
                    showError('❌ Xəta: ' + err.message);
                });
            });
        }
 
        function showError(msg) {
            error.textContent = msg;
            error.style.display = 'block';
            setTimeout(() => { error.style.display = 'none'; }, 5000);
        }
 
        function showSuccess(msg) {
            success.textContent = msg;
            success.style.display = 'block';
            setTimeout(() => { success.style.display = 'none'; }, 4000);
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
                                <img src="/download/${file.name}" loading="lazy">
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
 
        # Fayl ölçüsü yoxla
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)
 
        if file_size > 1 * 1024 * 1024 * 1024:  # 1GB
            return jsonify({'success': False, 'error': 'Fayl 1GB-dan böyükdür'})
 
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
                    elif ext in {'mp4', 'webm', 'mov', 'avi', 'mkv'}:
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
            with open(filepath, 'rb') as f:
                return f.read()
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
 
 
✅ DEĞİŞİKLİKLƏR:
 
🎨 DİZAYN:
✅ Krem/Beige rəng - Gelin toya uyğun
✅ Ürək 💕 ortada
✅ "Wedding Day" - Kölgə yazı (görunmə soz)
✅ "Anımızı Saxla" - Başlıq
✅ "💌" faylları sürükləyin
✅ Keramik/Şık görünüş
 
📹 VIDEO:
✅ 1GB-a qədər upload (əvvəl 100MB idi) → 3 saatlıq video yüklə bilərsən
✅ Daha çox video formatı: mp4, webm, mov, avi, mkv
✅ Timeout artırıldı (30 dəqiqə)
✅ Böyük fayllar üçün "Yüklənir..." mesajı
 
🔊 SƏS:
✅ mp3, wav, m4a, aac formatları
 
🚀 DEPLOY ET:
 
1️⃣ GitHub - app.py-ni əvəz et (üsttəki kodu)
2️⃣ Commit et: git add . && git commit -m "Wedding theme + video fix"
3️⃣ Push et: git push
4️⃣ Render - avtomatik redeploy olacaq (2-3 dəqiqə)
