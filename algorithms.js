const encryptedBase64 = canvasToBase64(encryptedCanvas);
// canvasToBase64 fonksiyonu
// canvas'ı base64 formatına dönüştürme
function canvasToBase64(canvas) {
    return canvas.toDataURL();
}

saveBtn.addEventListener('click', () => {
    const encryptedBase64 = canvasToBase64(encryptedCanvas);

    // Backend'e gönderme
    fetch('/save-image', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            encryptedBase64: encryptedBase64,  // Şifrelenmiş base64 verisi
            description: 'Şifrelenmiş görüntü',
        })
    })
    .then(response => response.json())
    .then(data => {
        console.log('Veritabanına kaydedildi:', data);

        // Kaydedilen base64'i ekranda tekrar göster
        const img = new Image();
        img.src = encryptedBase64;
        img.onload = () => {
            // Şifreli görseli ekrana gösterme
            encryptedCanvas.getContext('2d').drawImage(img, 0, 0);
        };
    })
    .catch(error => console.error('Veritabanına kaydedilemedi:', error));
});



// Canvas'ı gizleyip gösteren buton işlevi
const toggleCanvasBtn = document.getElementById('toggleCanvas');



// Butona tıklanınca canvas'ın görünürlüğünü değiştir
toggleCanvasBtn.addEventListener('click', () => {
    // Eğer canvas görünürse, gizleyelim; gizliyse, gösterelim
    if (originalCanvas.style.visibility === 'hidden') {
        originalCanvas.style.visibility = 'visible';  // Canvas'ı göster
    } else {
        originalCanvas.style.visibility = 'hidden';  // Canvas'ı gizle
    }
});


// Yaş aralığına göre BPM değerleri
const bpmTable = [
    { ageRange: "0-1", bpm: 120 },
    { ageRange: "2-10", bpm: 90 },
    { ageRange: "11-20", bpm: 72 },
    { ageRange: "21-40", bpm: 60 },
    { ageRange: "41+", bpm: 55 }
];

// Yaş aralığına göre BPM değerini almak için fonksiyon
function getBPMForAge(age) {
    if (age >= 0 && age <= 1) return 120;
    if (age >= 2 && age <= 10) return 90;
    if (age >= 11 && age <= 20) return 72;
    if (age >= 21 && age <= 40) return 60;
    return 55;  // 41+ yaş için
}

// Video ve canvas elemanları
const video = document.getElementById('video');
const originalCanvas = document.getElementById('originalCanvas');
const encryptedCanvas = document.getElementById('encryptedCanvas');
const saveBtn = document.getElementById('saveBtn');

const ctxOriginal = originalCanvas.getContext('2d');
const ctxEncrypted = encryptedCanvas.getContext('2d');

// Kamera başlatma
navigator.mediaDevices.getUserMedia({ video: true })
    .then(stream => {
        video.srcObject = stream;
    })
    .catch(err => {
        console.error("Kamera hatası: ", err);
    });

// Görüntüyü almak ve şifrelemek
function processImage() {
    ctxOriginal.drawImage(video, 0, 0, originalCanvas.width, originalCanvas.height);
    const imageData = ctxOriginal.getImageData(0, 0, originalCanvas.width, originalCanvas.height);
    const data = imageData.data;

    // Şifreleme işlemi
    xorEncrypt(data);
    pixelReflection(data);
    frequencyModulation(data);
    pixelBlockShifting(data);
    
    // Yaş ve BPM işlemi
    applyBPMtoPixels(data, originalCanvas.width, originalCanvas.height);

    // Rastgele pikselleri karıştırma
    randomPixelShuffle(data, originalCanvas.width, originalCanvas.height, 0.1);  // %10 karıştırma

    // Görüntüyü tamamen tanınmaz hale getirecek işlem
    extremePixelShuffle(data, originalCanvas.width, originalCanvas.height);

    // Şifrelenmiş görüntüyü canvas'ta göster
    ctxEncrypted.putImageData(imageData, 0, 0);
}

// XOR şifreleme
function xorEncrypt(data, key = 123) {
    for (let i = 0; i < data.length; i += 4) {
        data[i] ^= key;
        data[i + 1] ^= key;
        data[i + 2] ^= key;
    }
}

// Yansıma efekti
function pixelReflection(data) {
    let width = originalCanvas.width;
    let height = originalCanvas.height;
    for (let y = 0; y < height; y++) {
        for (let x = 0; x < width / 2; x++) {
            let idx1 = (y * width + x) * 4;
            let idx2 = (y * width + (width - x - 1)) * 4;
            for (let i = 0; i < 4; i++) {
                let temp = data[idx1 + i];
                data[idx1 + i] = data[idx2 + i];
                data[idx2 + i] = temp;
            }
        }
    }
}

// Frekans modülasyonu (FFT) (basitleştirilmiş versiyon)
function frequencyModulation(data) {
    for (let i = 0; i < data.length; i += 4) {
        if (Math.random() > 0.85) {
            data[i] = Math.random() * 255;
            data[i + 1] = Math.random() * 255;
            data[i + 2] = Math.random() * 255;
        }
    }
}

// 2x2 bloklar halinde piksel yer değiştirme
function pixelBlockShifting(data) {
    let width = originalCanvas.width;
    let height = originalCanvas.height;
    const blockSize = 10;
    for (let y = 0; y < height; y += blockSize) {
        for (let x = 0; x < width; x += blockSize) {
            let idx1 = (y * width + x) * 4;
            let idx2 = ((y + blockSize) * width + (x + blockSize)) * 4;
            for (let i = 0; i < 4; i++) {
                let temp = data[idx1 + i];
                data[idx1 + i] = data[idx2 + i];
                data[idx2 + i] = temp;
            }
        }
    }
}

// Yaş ve BPM değerini her piksele uygulama
function applyBPMtoPixels(data, width, height) {
    for (let i = 0; i < data.length; i += 4) {
        const age = Math.floor(Math.random() * 100) + 1;
        const bpm = getBPMForAge(age);
        data[i] = (data[i] + bpm) % 256;  
        data[i + 1] = (data[i + 1] + bpm) % 256;  
        data[i + 2] = (data[i + 2] + bpm) % 256;
    }
    return data;
}

// Görüntüdeki bazı pikselleri rastgele seçip karıştıran fonksiyon
function randomPixelShuffle(data, width, height, shufflePercentage = 0.1) {
    const totalPixels = width * height;
    const shuffleCount = Math.floor(totalPixels * shufflePercentage);  // Kaç pikselin karıştırılacağı
    const pixelsToShuffle = [];

    for (let i = 0; i < shuffleCount; i++) {
        const randomIndex = Math.floor(Math.random() * totalPixels);
        pixelsToShuffle.push(randomIndex);
    }

    for (let i = 0; i < pixelsToShuffle.length; i++) {
        const pixel1 = pixelsToShuffle[i];
        const pixel2 = pixelsToShuffle[Math.floor(Math.random() * pixelsToShuffle.length)];
        const idx1 = pixel1 * 4;
        const idx2 = pixel2 * 4;

        for (let j = 0; j < 4; j++) {
            const temp = data[idx1 + j];
            data[idx1 + j] = data[idx2 + j];
            data[idx2 + j] = temp;
        }
    }

    return data;
}

// Görüntüyü tanınmaz hale getirecek tam piksel yer değiştirme fonksiyonu
function extremePixelShuffle(data, width, height, blockSize = 30) {
    const totalBlocks = Math.floor(width / blockSize) * Math.floor(height / blockSize);
    const blockPositions = [];

    for (let i = 0; i < totalBlocks; i++) {
        const randomBlock = {
            x: Math.floor(Math.random() * (width - blockSize)),
            y: Math.floor(Math.random() * (height - blockSize)),
        };
        blockPositions.push(randomBlock);
    }

    for (let i = 0; i < blockPositions.length; i++) {
        const block1 = blockPositions[i];
        const block2 = blockPositions[Math.floor(Math.random() * blockPositions.length)];
        swapBlockPixels(data, width, height, block1, block2, blockSize);
    }

    return data;
}

// Bloklar arasındaki pikselleri yer değiştirme fonksiyonu
function swapBlockPixels(data, width, height, block1, block2, blockSize) {
    for (let y = 0; y < blockSize; y++) {
        for (let x = 0; x < blockSize; x++) {
            const idx1 = ((block1.y + y) * width + (block1.x + x)) * 4;
            const idx2 = ((block2.y + y) * width + (block2.x + x)) * 4;

            for (let i = 0; i < 4; i++) {
                const temp = data[idx1 + i];
                data[idx1 + i] = data[idx2 + i];
                data[idx2 + i] = temp;
            }
        }
    }
}

// Kaydet butonuna basıldığında şifreli görüntüyü veritabanına kaydetme
saveBtn.addEventListener('click', () => {
    const imageData = ctxEncrypted.getImageData(0, 0, encryptedCanvas.width, encryptedCanvas.height);

    // Base64 formatına dönüştürme
    const encryptedBase64 = canvasToBase64(encryptedCanvas);

    // Veritabanına kaydetme için backend'e gönderme
    fetch('/save-image', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            original: encryptedBase64,
            description: 'Şifrelenmiş görüntü',
        })
    })
    .then(response => response.json())
    .then(data => console.log('Veritabanına kaydedildi:', data))
    .catch(error => console.error('Veritabanına kaydedilemedi:', error));
});

// Canvas'ı base64'e dönüştürme
function canvasToBase64(canvas) {
    return canvas.toDataURL();
}

// Görüntüyü işleme işlemini başlat
setInterval(processImage, 100);  // 100ms'de bir görüntü işleme
