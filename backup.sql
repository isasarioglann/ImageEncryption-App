-- Veritabanı oluşturma
CREATE DATABASE goruntu_sifreleme;

-- Veritabanını kullanma
USE goruntu_sifreleme;

-- Tablo oluşturma
CREATE TABLE kayitlar (
    id INT AUTO_INCREMENT PRIMARY KEY,
    orijinal LONGTEXT,
    sifreli LONGTEXT,
    sayisal LONGTEXT
);
