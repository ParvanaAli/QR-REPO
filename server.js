const express = require('express');
const multer = require('multer');
const cloudinary = require('cloudinary').v2;
const cors = require('cors');
require('dotenv').config();

const app = express();

// Cloudinary konfigurasi
cloudinary.config({
  cloud_name: process.env.CLOUDINARY_CLOUD_NAME,
  api_key: process.env.CLOUDINARY_API_KEY,
  api_secret: process.env.CLOUDINARY_API_SECRET
});

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.static('public'));

// Multer setup (memory storage)
const upload = multer({
  storage: multer.memoryStorage(),
  limits: { fileSize: 100 * 1024 * 1024 }, // 100MB
  fileFilter: (req, file, cb) => {
    const allowed = /\.(jpg|jpeg|png|gif|mp4|mp3|webm|wav|m4a)$/i;
    if (allowed.test(file.originalname)) {
      cb(null, true);
    } else {
      cb(new Error('Fayl tipi dəstəklənmir'), false);
    }
  }
});

// Upload endpoint
app.post('/api/upload', upload.single('file'), async (req, res) => {
  try {
    if (!req.file) {
      return res.status(400).json({ error: 'Fayl seçilməyib' });
    }

    const fileType = req.file.mimetype.split('/')[0]; // image, video, audio
    const resourceType = fileType === 'image' ? 'image' : fileType === 'video' ? 'video' : 'raw';

    // Cloudinary-ə upload
    const uploadStream = cloudinary.uploader.upload_stream(
      {
        resource_type: resourceType,
        folder: 'media-uploader',
        public_id: `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
      },
      (error, result) => {
        if (error) {
          console.error('Upload xətası:', error);
          return res.status(500).json({ error: 'Fayl yükləmə uğursuz oldu' });
        }

        res.json({
          success: true,
          url: result.secure_url,
          type: fileType,
          name: req.file.originalname,
          size: req.file.size
        });
      }
    );

    uploadStream.end(req.file.buffer);
  } catch (err) {
    console.error('Xəta:', err);
    res.status(500).json({ error: err.message });
  }
});

// Gallery endpoint (bütün uploads)
app.get('/api/gallery', async (req, res) => {
  try {
    const result = await cloudinary.api.resources({
      type: 'upload',
      prefix: 'media-uploader',
      max_results: 100
    });

    const files = result.resources.map(file => ({
      url: file.secure_url,
      type: file.type === 'image' ? 'image' : file.resource_type === 'video' ? 'video' : 'audio',
      name: file.public_id.split('/').pop(),
      size: file.bytes,
      uploadedAt: file.created_at
    }));

    res.json({ files, total: result.total_count });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// Delete endpoint
app.delete('/api/delete/:publicId', async (req, res) => {
  try {
    await cloudinary.uploader.destroy(`media-uploader/${req.params.publicId}`);
    res.json({ success: true });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Server ${PORT} portunda çalışır`);
});
