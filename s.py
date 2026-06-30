import cv2
import numpy as np
from tkinter import *
from PIL import Image, ImageTk
import mysql.connector
import random
import io
import os  # Dosya kontrolü için gerekli
from tkinter import ttk  # ttk modülü eklendi

# Şifreleme adımlarının kısa açıklamaları
step_descriptions = [
    "1. Dijital Kilit (XOR): Her pikselin değeri gizli bir anahtar ile kilitlenir. (Ev kapısını kilitlemek gibi)",
    "2. Ayna Selfie (Yansıma): Görüntü yatayda ayna gibi ters çevrilir. (Kendine bakmak gibi)",
    "3. Elektromanyetık Yük Atamaları: Her piksele (+) veya (-) yük atar ve piksellere itme ve çekme gücü kazandırır."
    "4. Frekans Dansı (Modülasyon): Görüntüdeki pikseller müzikteki frekans gibi karıştırılır. (Dans pistinde karışmak gibi)",
    "5. Blok Tetris (Yer Değiştirme): 10x10'luk bloklar tetris taşları gibi yer değiştirir. (Tetris oynamak gibi)",
    "6. Yaş & BPM Partisi: Her 5x5 piksel grubuna rastgele yaş atanır, yaşa göre BPM değeri piksellere eklenir. (Bir partide farklı yaş gruplarının müzikle coşması gibi)"
]

# --- Şifreleme adımlarını topluca gösteren buton ve pencere ---
def show_all_steps():
    steps_win = Toplevel(window)
    steps_win.title("Tüm Şifreleme Adımları")
    steps_win.configure(bg="#222222")
    Label(steps_win, text="Şifreleme Adımları", bg="#222222", fg="orange", font=("Arial", 13, "bold")).pack(padx=10, pady=10)
    Label(steps_win, text="\n".join(step_descriptions), bg="#222222", fg="white", font=("Arial", 11), justify="left").pack(padx=10, pady=10)

# MySQL veritabanı bağlantısı ve tablo oluşturma
def create_db():
    # MySQL veritabanı bağlantısı
    conn = mysql.connector.connect(
        host="localhost",
        user="root",  # Kullanıcı adınızı buraya yazın
        password="1234",  # Şifrenizi buraya yazın
        database="goruntu_sifreleme"
    )
    c = conn.cursor()
    
    # Tablo oluşturma
    c.execute('''
        CREATE TABLE IF NOT EXISTS kayitlar (
            id INT AUTO_INCREMENT PRIMARY KEY,
            original_image LONGBLOB,
            encrypted_image LONGBLOB,
            numeric_representation TEXT
        )
    ''')
    conn.commit()
    conn.close()

# XOR şifreleme fonksiyonu (Özgün algoritma)
def xor_encrypt(image_data, key=123):
    encrypted_image = np.bitwise_xor(image_data, key)
    return encrypted_image

# Yansıma Efekti (Şifreleme algoritması)
def pixel_reflection(image_data):
    reflected_image = np.flip(image_data, axis=1)  # Yatay eksende ters çevir
    return reflected_image

# Frekans Modülasyonu ile Piksel Değişimi (FFT ile şifreleme)
def frequency_modulation(image_data):
    f = np.fft.fft2(image_data)
    fshift = np.fft.fftshift(f)
    rows, cols, _ = image_data.shape
    crow, ccol = rows // 120, cols // 120
    fshift[crow-10:crow+10, ccol-10:ccol+10] *= random.uniform(2.8, 1.2)
    f_ishift = np.fft.ifftshift(fshift)
    img_back = np.fft.ifft2(f_ishift)
    img_back = np.abs(img_back)
    img_back = np.uint8(np.clip(img_back, 0, 255))
    return img_back

# 2x2'lik Bloklar Halinde Yer Değiştirme
def pixel_block_shifting(image_data):
    height, width, _ = image_data.shape
    new_image = image_data.copy()
    block_size = 10
    for i in range(0, height, block_size):
        for j in range(0, width, block_size):
            block = image_data[i:min(i+block_size, height), j:min(j+block_size, width)]
            shift_x = random.choice([200, -200])
            shift_y = random.choice([200, -200])
            new_i = (i + shift_x * block_size) % height
            new_j = (j + shift_y * block_size) % width
            ni2 = min(new_i + block.shape[0], height)
            nj2 = min(new_j + block.shape[1], width)
            new_image[new_i:ni2, new_j:nj2] = block[:ni2-new_i, :nj2-new_j]
    return new_image

# --- Yeni şifreleme adımı: Yaş ve BPM'e göre 5x5 piksel gruplarına renk ekleme ---
def bpm_age_pixel_modulation(image_data):
    # Yaş aralıkları ve BPM değerleri
    age_bpm = [
        (0, 1, 120),
        (2, 10, 90),
        (11, 20, 72),
        (21, 40, 60),
        (41, 200, 55)
    ]
    height, width, _ = image_data.shape
    block_size = 5
    new_img = image_data.copy()
    for i in range(0, height, block_size):
        for j in range(0, width, block_size):
            # Random yaş ata
            yas = random.randint(0, 100)
            # Yaşa göre bpm bul
            bpm = 55
            for min_yas, max_yas, bpm_val in age_bpm:
                if min_yas <= yas <= max_yas:
                    bpm = bpm_val
                    break
            # 5x5 blokta her pikselin rgb'sine bpm ekle, 255'i aşarsa 50 mod al
            for y in range(i, min(i+block_size, height)):
                for x in range(j, min(j+block_size, width)):
                    for c in range(3):
                        val = int(new_img[y, x, c]) + bpm
                        if val > 255:
                            val = val % 50
                        new_img[y, x, c] = val
    return new_img

# Veritabanına kaydetme
def save_to_db(original, encrypted, numeric):
    conn = mysql.connector.connect(
        host="localhost",
        user="root",  # Kullanıcı adınızı buraya yazın
        password="1234",  # Şifrenizi buraya yazın
        database="goruntu_sifreleme"
    )
    c = conn.cursor()
    c.execute("INSERT INTO kayitlar (original_image, encrypted_image, numeric_representation) VALUES (%s, %s, %s)", 
              (original, encrypted, numeric))
    conn.commit()
    conn.close()

# Veritabanından şifreli görüntüleri çağırma fonksiyonu
def fetch_encrypted_images():
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="1234",
        database="goruntu_sifreleme"
    )
    c = conn.cursor()
    c.execute("SELECT encrypted_image FROM kayitlar ORDER BY id DESC LIMIT 10")
    results = c.fetchall()
    conn.close()
    return results

# Şifreli görüntüleri ekranda gösteren fonksiyon
def show_encrypted_images():
    # Yeni tam ekran pencere aç
    img_win = Toplevel(window)
    img_win.title("Şifreli Görseller")
    img_win.configure(bg="#181A20")
    img_win.state('zoomed')  # Windows için tam ekran

    # Ana çerçeve: solda şifreli görseller, sağda orijinal görsel
    main_frame = Frame(img_win, bg="#181A20")
    main_frame.pack(fill="both", expand=True)

    # Sol panel: şifreli görseller (scrollable, geniş ve dikey) - GENİŞLİK ARTIRILDI
    left_panel = Frame(main_frame, bg="#181A20")
    left_panel.pack(side=LEFT, fill="both", expand=True, padx=(0,0), pady=40)
    canvas = Canvas(left_panel, bg="#181A20", highlightthickness=0, width=520)
    scrollbar = Scrollbar(left_panel, orient="vertical", command=canvas.yview)
    scrollable_panel = Frame(canvas, bg="#181A20")
    scrollable_panel.bind(
        "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )
    canvas.create_window((0, 0), window=scrollable_panel, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.pack(side=LEFT, fill="both", expand=True)
    scrollbar.pack(side=RIGHT, fill="y")

    # Sağ panel: büyük orijinal görsel alanı - GENİŞLİK AZALTILDI
    right_panel = Frame(main_frame, bg="#181A20")
    right_panel.pack(side=LEFT, fill="both", expand=True, padx=(0,0), pady=0)
    ori_right_label = Label(right_panel, text="Orijinal Görsel", bg="#FFD166", fg="#23272F", font=("Segoe UI", 18, "bold"), pady=16, padx=32)
    ori_right_label.pack(pady=(60, 18), anchor="n")
    ori_right_img = Label(right_panel, bg="#23272F", width=480, height=360, relief="ridge", highlightbackground="#FFD166", highlightthickness=6)
    ori_right_img.pack(pady=24, anchor="n")

    images = fetch_encrypted_images_with_id_and_numeric()
    if not images:
        Label(scrollable_panel, text="Veritabanında şifreli görüntü yok.", bg="#181A20", fg="#fff", font=("Arial", 14)).pack(pady=40)
        return
    for idx, (img_id, img_bytes, numeric) in enumerate(images):
        row_frame = Frame(scrollable_panel, bg="#23272F", highlightbackground="#00C9A7", highlightthickness=2, bd=0)
        row_frame.pack(fill="x", padx=18, pady=18)
        # Şifreli görsel çerçevesi
        enc_img_frame = Frame(row_frame, bg="#23272F", highlightbackground="#6C63FF", highlightthickness=2, bd=0)
        enc_img_frame.pack(side=LEFT, padx=8, pady=8)
        arr = np.frombuffer(img_bytes, dtype=np.uint8)
        try:
            img_np = arr.reshape((480, 640, 3))
        except Exception:
            continue
        img_pil = Image.fromarray(img_np).resize((120, 90))
        img_tk = ImageTk.PhotoImage(img_pil)
        img_label = Label(enc_img_frame, image=img_tk, bg="#23272F", bd=0)
        img_label.image = img_tk
        img_label.pack()
        # Sayısal karşılık
        lbl_numeric = Label(row_frame, text=f"Sayısal: {numeric}", bg="#23272F", fg="#FFD166", font=("Arial", 10, "bold"))
        lbl_numeric.pack(side=LEFT, padx=18)
        # Deşifre Et butonu (modern, her zaman görünür)
        def make_decrypt_func(img_id):
            def decrypt():
                ori_bytes = fetch_original_image(img_id)
                if ori_bytes:
                    arr = np.frombuffer(ori_bytes, dtype=np.uint8)
                    try:
                        img_np = arr.reshape((480, 640, 3))
                    except Exception:
                        return
                    img_pil = Image.fromarray(img_np).resize((480, 360))
                    img_tk = ImageTk.PhotoImage(img_pil)
                    ori_right_img.config(image=img_tk)
                    ori_right_img.image = img_tk
            return decrypt
        decrypt_btn = ttk.Button(row_frame, text="Deşifre Et", style="Blue.TButton", command=make_decrypt_func(img_id))
        decrypt_btn.pack(side=RIGHT, padx=24, ipadx=16, ipady=8)

def fetch_encrypted_images_with_id():
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="1234",
        database="goruntu_sifreleme"
    )
    c = conn.cursor()
    c.execute("SELECT id, encrypted_image FROM kayitlar ORDER BY id DESC LIMIT 10")
    results = c.fetchall()
    conn.close()
    return results

def fetch_encrypted_images_with_id_and_numeric():
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="1234",
        database="goruntu_sifreleme"
    )
    c = conn.cursor()
    c.execute("SELECT id, encrypted_image, numeric_representation FROM kayitlar ORDER BY id DESC LIMIT 50")
    results = c.fetchall()
    conn.close()
    return results

def fetch_original_image(img_id):
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="1234",
        database="goruntu_sifreleme"
    )
    c = conn.cursor()
    c.execute("SELECT original_image FROM kayitlar WHERE id=%s", (img_id,))
    row = c.fetchone()
    conn.close()
    if row:
        return row[0]
    return None

def show_original_image(img_id):
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="1234",
        database="goruntu_sifreleme"
    )
    c = conn.cursor()
    c.execute("SELECT original_image FROM kayitlar WHERE id=%s", (img_id,))
    row = c.fetchone()
    conn.close()
    if row:
        arr = np.frombuffer(row[0], dtype=np.uint8)
        try:
            img_np = arr.reshape((480, 640, 3))
        except Exception:
            return
        img_pil = Image.fromarray(img_np)
        img_pil = img_pil.resize((200, 150))
        img_tk = ImageTk.PhotoImage(img_pil)
        win = Toplevel(window)
        win.title("Orijinal Görüntü")
        lbl = Label(win, image=img_tk)
        lbl.image = img_tk
        lbl.pack(padx=10, pady=10)

# Kamera açma ve görüntü alma
# Son frame'leri global değişkenlerde tut
last_original_frame = None
last_encrypted_frame = None

def start_camera():
    global last_original_frame, last_encrypted_frame
    cap = cv2.VideoCapture(0)
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        # 1. Dijital Kilit (XOR)
        update_flow_panel(0)
        encrypted_frame = xor_encrypt(frame_rgb)
        window.update_idletasks()
        # 2. Ayna Selfie (Yansıma)
        update_flow_panel(1)
        reflected_frame = pixel_reflection(encrypted_frame)
        window.update_idletasks()
        # 3. Frekans Dansı (Modülasyon)
        update_flow_panel(2)
        modulated_frame = frequency_modulation(reflected_frame)
        window.update_idletasks()
        # 4. Blok Tetris (Yer Değiştirme)
        update_flow_panel(3)
        shifted_frame = pixel_block_shifting(modulated_frame)
        window.update_idletasks()
        # 5. Yaş&BPM Partisi
        update_flow_panel(4)
        bpm_modulated = bpm_age_pixel_modulation(shifted_frame)
        # Orijinal görüntü alanı
        if camera_on:
            header_img_ori = Image.fromarray(frame_rgb).resize((320, 240))
            header_img_ori_tk = ImageTk.PhotoImage(header_img_ori)
            header_ori_img.config(image=header_img_ori_tk)
            header_ori_img.image = header_img_ori_tk
        else:
            # Kamera kapalıysa orijinal görüntü kısmı siyah gösterilsin
            black_img = Image.new('RGB', (320, 240), color='black')
            black_img_tk = ImageTk.PhotoImage(black_img)
            header_ori_img.config(image=black_img_tk)
            header_ori_img.image = black_img_tk
        # Şifreli görüntü her zaman güncellensin
        header_img_enc = Image.fromarray(bpm_modulated).resize((320, 240))
        header_img_enc_tk = ImageTk.PhotoImage(header_img_enc)
        header_enc_img.config(image=header_img_enc_tk)
        header_enc_img.image = header_img_enc_tk
        last_original_frame = frame_rgb.copy()
        last_encrypted_frame = bpm_modulated.copy()
        window.update_idletasks()
        window.update()
    cap.release()

# Kamera açma/kapama fonksiyonu
def toggle_camera():
    global camera_on
    camera_on = not camera_on
    update_camera_button()

# Kaydetme butonuna basıldığında çağrılacak fonksiyon
def save_image():
    global last_original_frame, last_encrypted_frame
    if last_original_frame is None or last_encrypted_frame is None:
        print("Hata: Görüntü alınamadı. Lütfen kameradan görüntü geldiğinden emin olun.")
        return
    numeric_rep = str(np.sum(last_encrypted_frame))
    save_to_db(last_original_frame.tobytes(), last_encrypted_frame.tobytes(), numeric_rep)
    print("Veritabanına kaydedildi.")
    # Kayıt başarılıysa kullanıcıya bilgi ver
    from tkinter import messagebox
    messagebox.showinfo("Başarılı", "Kaydetme işlemi başarıyla tamamlandı.")

# Tkinter arayüzü
window = Tk()
window.title("Görüntü Şifreleme Uygulaması")

screen_width = window.winfo_screenwidth()
screen_height = window.winfo_screenheight()
window.geometry(f"{screen_width}x{screen_height}")
window.update_idletasks()
window.configure(bg="#181A20")

# --- Arka plan resmi ekle ---
bg_image = Image.open("arkaplan.png")
bg_image = bg_image.resize((screen_width, screen_height))
bg_photo = ImageTk.PhotoImage(bg_image)
bg_label = Label(window, image=bg_photo)
bg_label.place(x=0, y=0, relwidth=1, relheight=1)

# --- Akan bilgi paneli için ---
from collections import deque
step_names = [
    ("Dijital Kilit (XOR)", "Her pikselin değeri sabit bir anahtar ile XOR'lanır."),
    ("Ayna Selfie (Yansıma)", "Görüntü yatayda ayna gibi ters çevrilir."),
    ("Frekans Dansı (Modülasyon)", "Görüntü frekans bileşenleriyle oynanır, pikseller karıştırılır."),
    ("Blok Tetris (Yer Değiştirme)", "10x10'luk bloklar rastgele yer değiştirir."),
    ("Yaş&BPM Partisi", "Her 5x5 piksel grubuna rastgele yaş atanır, yaşa göre BPM değeri RGB'ye eklenir.")
]
step_queue = deque(maxlen=3)
flow_panel = Frame(window, bg="#23272F")
flow_panel.pack(side=BOTTOM, fill="x", pady=(10, 0))
flow_label = Label(flow_panel, text="", bg="#23272F", fg="#FFD166", font=("Segoe UI", 13, "bold"), anchor="w", justify="left")
flow_label.pack(fill="x", padx=20, pady=10)

def update_flow_panel(step_idx):
    if 0 <= step_idx < len(step_names):
        step_queue.appendleft(f"{step_names[step_idx][0]}: {step_names[step_idx][1]}")
        flow_label.config(text="\n".join(step_queue))

# --- Modern ve şık çerçeveli görüntü alanı ---
header_frame = Frame(window, bg="#181A20")
header_frame.pack(pady=30)

ori_frame = Frame(
    header_frame,
    bg="#181A20",
    highlightbackground="#6C63FF",
    highlightcolor="#6C63FF",
    highlightthickness=6,
    bd=0,
    relief="ridge"
)
ori_frame.grid(row=0, column=0, padx=30)
header_ori_label = Label(
    ori_frame,
    text="Orijinal",
    bg="#6C63FF",
    fg="#fff",
    font=("Segoe UI", 14, "bold"),
    pady=7, padx=18,
    bd=0,
    relief="flat"
)
header_ori_label.pack(fill="x", pady=(0, 7))
header_ori_img = Label(ori_frame, bg="#23272F", bd=0)
header_ori_img.pack(padx=14, pady=14)

enc_frame = Frame(
    header_frame,
    bg="#181A20",
    highlightbackground="#00C9A7",
    highlightcolor="#00C9A7",
    highlightthickness=6,
    bd=0,
    relief="ridge"
)
enc_frame.grid(row=0, column=1, padx=30)
header_enc_label = Label(
    enc_frame,
    text="Şifreli",
    bg="#00C9A7",
    fg="#fff",
    font=("Segoe UI", 14, "bold"),
    pady=7, padx=18,
    bd=0,
    relief="flat"
)
header_enc_label.pack(fill="x", pady=(0, 7))
header_enc_img = Label(enc_frame, bg="#23272F", bd=0)
header_enc_img.pack(padx=14, pady=14)

# Kamera durumu
camera_on = True  # Kamera başlangıçta açık

# --- Modern butonlar için özel stiller ---
style = ttk.Style()
style.theme_use("clam")
style.configure("Green.TButton", font=("Arial", 13, "bold"), foreground="#fff", background="#22C55E", borderwidth=0, relief="flat")
style.map("Green.TButton", background=[('active', '#16A34A')])
style.configure("Red.TButton", font=("Arial", 13, "bold"), foreground="#fff", background="#EF4444", borderwidth=0, relief="flat")
style.map("Red.TButton", background=[('active', '#B91C1C')])
style.configure("Blue.TButton", font=("Arial", 13, "bold"), foreground="#fff", background="#3B82F6", borderwidth=0, relief="flat")
style.map("Blue.TButton", background=[('active', '#1D4ED8')])
style.configure("Yellow.TButton", font=("Arial", 13, "bold"), foreground="#23272F", background="#FACC15", borderwidth=0, relief="flat")
style.map("Yellow.TButton", background=[('active', '#CA8A04')])
style.configure("Purple.TButton", font=("Arial", 13, "bold"), foreground="#fff", background="#A21CAF", borderwidth=0, relief="flat")
style.map("Purple.TButton", background=[('active', '#6D28D9')])

# ttk ile border-radius doğrudan desteklenmez, ancak Windows 11 ve yeni temalarda köşeler daha yuvarlatılmış görünür.
# Daha belirgin radius için, ttk yerine klasik Button ile 'highlightthickness', 'bd', 'relief' ve 'bg' ile oynanabilir.
# Alternatif olarak, ttkbootstrap veya customtkinter gibi modern kütüphaneler kullanılabilir.

# Eğer daha fazla radius isterseniz, customtkinter önerilir.

# --- view_db_table fonksiyonu en üste taşındı ---
def view_db_table():
    db_win = Toplevel(window)
    db_win.title("Veritabanı Tablosu")
    db_win.state('zoomed')
    db_win.configure(bg="#181A20")
    main_frame = Frame(db_win, bg="#181A20")
    main_frame.pack(fill="both", expand=True)
    canvas = Canvas(main_frame, bg="#181A20", highlightthickness=0)
    scrollbar = Scrollbar(main_frame, orient="vertical", command=canvas.yview)
    table_panel = Frame(canvas, bg="#181A20")
    table_panel.bind(
        "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )
    canvas.create_window((0, 0), window=table_panel, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.pack(side=LEFT, fill="both", expand=True)
    scrollbar.pack(side=RIGHT, fill="y")
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="1234",
        database="goruntu_sifreleme"
    )
    c = conn.cursor()
    c.execute("SHOW COLUMNS FROM kayitlar")
    columns = [col[0] for col in c.fetchall()]
    c.execute(f"SELECT * FROM kayitlar ORDER BY id DESC")
    rows = c.fetchall()
    conn.close()
    for col, h in enumerate(columns):
        Label(table_panel, text=h, bg="#FFD166", fg="#23272F", font=("Segoe UI", 13, "bold"), padx=10, pady=8, borderwidth=2, relief="ridge").grid(row=0, column=col, sticky="nsew", padx=2, pady=2)
    sil_col = len(columns)
    Label(table_panel, text="Sil", bg="#EF4444", fg="#fff", font=("Segoe UI", 13, "bold"), padx=10, pady=8, borderwidth=2, relief="ridge").grid(row=0, column=sil_col, sticky="nsew", padx=2, pady=2)
    for row_idx, row in enumerate(rows, start=1):
        for col_idx, value in enumerate(row):
            if columns[col_idx] in ("original_image", "orijinal", "sifreli", "encrypted_image"):
                try:
                    arr = np.frombuffer(value, dtype=np.uint8)
                    img_np = arr.reshape((480, 640, 3))
                    img_pil = Image.fromarray(img_np).resize((80, 60))
                    img_tk = ImageTk.PhotoImage(img_pil)
                    lbl = Label(table_panel, image=img_tk, bg="#23272F", bd=0)
                    lbl.image = img_tk
                    lbl.grid(row=row_idx, column=col_idx, padx=2, pady=2)
                except Exception:
                    Label(table_panel, text="-", bg="#23272F", fg="#fff").grid(row=row_idx, column=col_idx, padx=2, pady=2)
            else:
                Label(table_panel, text=str(value), bg="#23272F", fg="#FFD166" if col_idx==0 else "#fff", font=("Arial", 11), padx=8, pady=6, borderwidth=1, relief="ridge").grid(row=row_idx, column=col_idx, sticky="nsew", padx=2, pady=2)
        def make_delete_func(row_id, row_widget=row_idx):
            def delete():
                conn = mysql.connector.connect(
                    host="localhost",
                    user="root",
                    password="1234",
                    database="goruntu_sifreleme"
                )
                c = conn.cursor()
                c.execute("DELETE FROM kayitlar WHERE id=%s", (row_id,))
                conn.commit()
                conn.close()
                for widget in table_panel.grid_slaves(row=row_widget):
                    widget.grid_forget()
            return delete
        del_btn = ttk.Button(table_panel, text="Sil", style="Red.TButton", command=make_delete_func(row[0], row_idx))
        del_btn.grid(row=row_idx, column=sil_col, padx=4, pady=4, ipadx=8, ipady=4)

# --- Butonları yan yana üstte bir frame içinde modern şekilde diz ---
button_frame = Frame(window, bg="#23272F")
button_frame.pack(pady=(10, 0))

camera_button = ttk.Button(button_frame, text="Kamera Açık", command=toggle_camera, style="Green.TButton")
camera_button.grid(row=0, column=0, padx=8)

save_button = ttk.Button(button_frame, text="Kaydet", command=save_image, style="Blue.TButton")
save_button.grid(row=0, column=1, padx=8)

fetch_button = ttk.Button(button_frame, text="Şifreli Görüntüleri Çağır", command=show_encrypted_images, style="Yellow.TButton")
fetch_button.grid(row=0, column=2, padx=8)

show_steps_btn = ttk.Button(button_frame, text="Tüm Şifreleme Adımlarını Göster", command=show_all_steps, style="Purple.TButton")
show_steps_btn.grid(row=0, column=3, padx=8)

view_db_button = ttk.Button(button_frame, text="Veritabanını Görüntüle", style="Red.TButton", command=view_db_table)
view_db_button.grid(row=0, column=4, padx=8)

# Kamera butonunun rengini dinamik olarak güncelle
def update_camera_button():
    if camera_on:
        camera_button.config(text="Kamera Açık", style="Green.TButton")
    else:
        camera_button.config(text="Kamera Kapalı", style="Red.TButton")

# Uygulama başlarken buton rengi doğru başlasın
update_camera_button()

# Veritabanı oluşturma
create_db()

# Tkinter penceresini başlatma
window.after(100, start_camera)  # Kamera başlatmayı zamanlayıcı ile çağır
window.mainloop()
