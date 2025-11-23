# P2P Dosya Aktarımı - Windows Executable

## 📦 Kurulu EXE Dosyaları

### Konumu
```
dist/
└── p2p_gui.exe (10.96 MB)
```

## 🚀 Nasıl Çalıştırılır?

### EXE ve kurulum paketini oluşturma
Windows üzerinde derlemek için PowerShell'de:
```powershell
# Sadece taşınabilir EXE
./build_exe.ps1

# EXE + Inno Setup installer (ISCC gerektirir)
./build_exe.ps1 -WithInstaller
```

### Seçenek 1: Doğrudan Çalıştırma
Masaüstüne kısayol oluşturun veya:
```powershell
.\dist\p2p_gui.exe
```

### Seçenek 2: Komut İsteminden
```powershell
cd "c:\Users\mehme\Desktop\p2p\p2p-main\dist"
p2p_gui.exe
```

### Seçenek 3: Dosya Gezgininden
1. `dist` klasörünü açın
2. `p2p_gui.exe` dosyasına çift tıklayın

## ⚙️ Sistem Gereksinimleri

- **İşletim Sistemi:** Windows 10/11 (64-bit)
- **Disk Alanı:** ~11 MB
- **RAM:** 128 MB (minimum)
- **Python Yüklü Değil:** Çalıştırmak için Python kurulması gerekmez

## 🎨 Özellikler

✅ Graphical User Interface (GUI)  
✅ Dosya ve Klasör Gönderme  
✅ PIN Korumalı Aktarım  
✅ Otomatik Buffer Optimizasyonu  
✅ Dizin Zipleme (Klasör Aktarımı)  
✅ Gerçek Zamanlı İşlem Günlükleri  
✅ LAN/WAN Ağ Seçimi  

## 📖 Kullanım Adımları

### Gönderme Modu
1. **Modu Seç:** "Gönder" radio düğmesini tıklayın
2. **Host Girin:** Alıcı IP adresini girin (örn: 192.168.1.100)
3. **Port:** 5000 (varsayılan)
4. **PIN:** Alıcıyla aynı PIN kullanın
5. **Dosya:** "Seç" düğmesiyle dosya/klasör seçin
6. **Başlat:** "Başlat" düğmesini tıklayın

### Alma Modu
1. **Modu Seç:** "Al" radio düğmesini tıklayın
2. **Dinlenecek Adres:** 0.0.0.0 (tüm ağ kartları)
3. **Port:** 5000 (varsayılan)
4. **PIN:** Gönderici ile aynı PIN
5. **Çıkış Klasörü:** Dosyaların kaydedileceği yer
6. **Başlat:** "Başlat" düğmesini tıklayın

## 🔒 Güvenlik

- HMAC-SHA256 PIN doğrulaması
- SHA256 hash integriti kontrolü
- Yerel ağ doğrulaması (RFC 1918)
- Başarısız doğrulama sonrası otomatik silme

## 🛠️ Sorun Giderme

### EXE Başlatılmıyor
**Çözüm:** Windows 11 SmartScreen uyarısını kapat
1. "Yine de çalıştır" tıklayın
2. Bu çıkmazı yok saymak için "Daha Fazla Bilgi" → "Yine de Çalıştır"

### "Port Zaten Kullanımda" Hatası
**Çözüm:** Farklı port kullanın
1. GUI'de Port alanını değiştirin
2. Gönderici ve alıcı aynı port kullanmalıdır

### PIN Doğrulama Hatası
**Çözüm:** PIN'ler eşleştiğinden emin olun
1. Gönderici PIN: "123456"
2. Alıcı PIN: "123456" (aynı olmalı)

### Dosya Alınamıyor
**Çözüm:** Çıkış klasörü yazma izni kontrol edin
1. Farklı klasör seçin
2. Administrator olarak çalıştırmayı deneyin

## 📊 Dosya Boyutuna Göre Performans

| Dosya Boyutu | Chunk | RAM | Hız |
|-------------|-------|-----|-----|
| < 10 MB | 64 KB | ~2 MB | ★☆☆ |
| 10-100 MB | 1 MB | ~5 MB | ★★☆ |
| 100 MB-1 GB | 4 MB | ~10 MB | ★★★ |
| > 1 GB | 8 MB | ~20 MB | ★★★ |

## 🌐 Ağ Gereksinimleri

### Yerel Ağ (LAN)
- **Hız:** 400-950 Mbps (Gigabit)
- **Gerekli Uyarı:** Aktarım sırasında bağlantıyı kesmeyin

### WiFi 5G
- **Hız:** 150-350 Mbps
- **Tavsiye:** Dosya aktarımı için LAN kullanın

### WiFi 2.4G
- **Hız:** 30-100 Mbps
- **Durumu:** Yavaş, sadece küçük dosyalar için uygun

## 📝 Türkçe Arayüz Öğeleri

| Öğe | Türkçe |
|-----|--------|
| Başlık | Sunucusuz, PIN korumalı P2P aktarım |
| Gönder | Gönder (radio) |
| Al | Al (radio) |
| Başlat | Başlat (düğme) |
| Pin | Pin |
| Port | Port |
| Blok Boyutu | Blok boyutu (bayt) |
| Alıcı Host | Alıcı host (send) |
| Gönderilecek | Gönderilecek dosya |
| Dinlenecek | Dinlenecek adres (receive) |
| Çıkış | Çıkış klasörü |
| LAN | Yerel ağ (LAN) |
| WAN | Genel (WAN) |

## 💾 Versiyon Bilgileri

- **Uygulama:** P2P Dosya Aktarımı v1.0
- **GUI Framework:** Tkinter (Windows Yerleşik)
- **Python:** 3.8+ (PyInstaller ile gömülü)
- **Derleme Tarihi:** 2025-01-22
- **Executable Tipi:** Windows x64

## 📂 Ek Dosyalar

Kökü projedeki diğer dosyalar:
- `p2p.py` - Temel backend
- `p2p_gui.py` - GUI kaynak kodu
- `README.md` - Detaylı dokümantasyon

## 🔄 Güncellemeler

EXE'yi güncellemek için:
1. `p2p_gui.py` dosyasını düzenleyin
2. Bu komutla yeniden derleyin:
```powershell
pyinstaller p2p_gui.py --onefile --windowed -y
```

## ⚠️ Yasal Uyarı

Bu yazılım sadece öğrenme ve meşru kullanım için sunulmaktadır. Telif hakkına tabi dosyaların yasalsız aktarımı yapılmayabilir.

## 📧 Destek

Sorunlar için:
1. `DEBUG_REPORT.md` kontrol edin
2. `QUICKSTART.md` referans alın
3. `IMPLEMENTATION.md` detaylı bilgi için

---

**Son Güncelleme:** 2025-01-22  
**Durum:** ✅ Üretim Hazır
