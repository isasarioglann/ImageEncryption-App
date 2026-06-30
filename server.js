const express = require('express');
const mysql = require('mysql2');
const multer = require('multer');
const bodyParser = require('body-parser');
require('dotenv').config();

const app = express();
app.use(bodyParser.json());

// Multer yapılandırması (binary veri almak için)
const storage = multer.memoryStorage();
const upload = multer({ storage: storage });

// Veritabanı bağlantısı
const db = mysql.createConnection({
    host: process.env.DB_HOST,
    user: process.env.DB_USER,
    password: process.env.DB_PASSWORD,
    database: process.env.DB_NAME
});

app.post('/save-image', (req, res) => {
    const { encryptedBase64, description } = req.body;

    const query = `
        INSERT INTO kayitlar (sifreli, aciklama)
        VALUES (?, ?)
    `;

    db.execute(query, [encryptedBase64, description], (err, results) => {
        if (err) {
            console.error('Veritabanına kaydetme hatası:', err);
            return res.status(500).send('Kaydedilemedi.');
        }
        res.status(200).json({ message: 'Veri başarıyla kaydedildi', data: results });
    });
});
// Sunucuyu başlat
app.listen(3000, () => {
    console.log('Sunucu çalışıyor...');
});
