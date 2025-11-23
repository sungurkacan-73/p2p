# p2p (PIN protected, serverless file transfer)

Hizli, dogrudan (sunucusuz) P2P dosya aktarimi. Her iki taraf ayni betigi kullanir; PIN ile HMAC dogrulamasi ve SHA-256 butunluk kontrolu yapar.

## Hizi baslangic
1) Python 3.10+ kurulu olsun.  
2) Ayni agda iki makine secin (NAT varsa portu iletin).  
3) Aynı PIN'i paylasin.  

### Alici (dinleme)
```bash
python p2p.py receive --port 5000 --pin 123456 --output-dir ./gelenler
```

### Gonderici
```bash
python p2p.py send --host 192.168.1.50 --port 5000 --pin 123456 --file ./dosya.iso
```

## Ozellikler
- Sunucusuz: iki uc arasinda dogrudan TCP.
- PIN tabanli HMAC kimlik dogrulama.
- SHA-256 butunluk dogrulamasi; hatali ise dosya silinir.
- Hiz odakli: varsayilan 1 MiB blok; `--chunk-size` ile buyutulebilir.

## Parametreler
- `--pin`: Paylasilan sir, HMAC icin.
- `--chunk-size`: Blok boyutu (bayt); 1-8 MiB arasi buyuk dosyalar icin iyi.
- `--bind`: Alici dinleme adresi (varsayilan `0.0.0.0`).
- `--host` / `--port`: Gonderici icin alicinin adresi/portu.
- `--output-dir`: Alicinin yazacagi klasor.
- `--local-only`: Sadece yerel/ozel IP kullanmaya zorlar (192.168.x.x, 10.x.x.x, 172.16-31.x.x, 127.0.0.1).

## GUI (tkinter)
Form ile calismak icin:
```bash
python p2p_gui.py
```
- Mod: Gonder / Al
- PIN, port, blok boyutu girin.
- Gonder: host ve dosya secin.
- Al: dinleme adresi ve cikis klasoru secin.
- Log penceresi ilerlemeyi gosterir.
- Ag modu secici: "Yerel ag (LAN)" tikli ise sadece yerel IP/loopback kabul edilir; "Genel" secilirse WAN/IP serbesttir.

## Android icin Kivy arayuz
Mobil uyumlu arayuz: `p2p_kivy.py`. Dogrudan `python p2p_kivy.py` (masaustu) veya buildozer ile APK.
Temel alanlar: Gonder/Al modu, PIN/port/blok boyutu, dosya/klasor secici, log.
Ag modu: "Yerel ag" acik ise IP yerel/loopback olmalidir; kapali ise genel IP kullanabilirsiniz.

## Windows icin tek `.exe`
PyInstaller:
```bash
pip install pyinstaller
pyinstaller --onefile --noconsole --name p2p_gui p2p_gui.py
```
Konsol ister misiniz? `--noconsole` kaldirin. Cikti `dist/p2p_gui.exe`. Imzaniz yoksa SmartScreen uyarir.

## Android (APK) paketleme adimlari
1) `pip install buildozer` (Linux ortaminda).  
2) `buildozer init`  
3) `buildozer.spec` icin oneriler:
   - `requirements = python3,kivy`
   - `source.include_exts = py`
   - `android.permissions = INTERNET,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE`
   - `title = P2P`
   - `package.name = p2p`
   - `package.domain = org.example` (kendinize gore degistirin)
   - `main.py` olarak `p2p_kivy.py` kullanin (gerekirse kopyalayip isimlendirin).
4) `buildozer -v android debug`  
APK `bin/` altinda olusur.

## Notlar
- NAT arkasindaysaniz alici portunu iletin; merkezi kesif sunucusu yok.
- Aktarim sonunda `OK` gormezseniz hash tutmadi demektir; dosya otomatik silinir.
- Yerel agda kalmak icin: hem alici `--bind` adresi hem de gonderici `--host` adresi olarak yerel IP (192.168.x.x vb) kullanin ve `--local-only` ekleyin. Bu yontem internete cikis yapmaz; baglanti dogrudan LAN icinde kurulur. Ekstra guvenlik icin Windows/Linux guvenlik duvari kuralini sadece yerel ag alt agina acabilirsiniz.
