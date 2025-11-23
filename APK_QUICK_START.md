# 🚀 Android APK Build - Quick Reference

## ⚡ Ultra-Quick Start (5 minutes)

### Option 1: PowerShell (Easiest - Windows)
```powershell
cd "c:\Users\mehme\Desktop\p2p\p2p-main"
.\build_apk.ps1
```
**That's it!** The script handles everything.

### Option 2: Python Helper
```powershell
cd "c:\Users\mehme\Desktop\p2p\p2p-main"
python build_apk.py
```

### Option 3: Manual (if scripts don't work)
```powershell
# Create Python 3.11 venv
py -3.11 -m venv venv_android
.\venv_android\Scripts\Activate.ps1

# Install & build
pip install buildozer cython kivy kivymd pillow jnius
buildozer android debug

# Your APK: bin/p2pshare-1.0-debug.apk
```

---

## 🐛 Troubleshooting

### "FancyURLopener" Error
→ Use Python 3.11/3.12, not 3.14:
```powershell
py -3.11 -m venv venv_android
.\venv_android\Scripts\Activate.ps1
pip install buildozer cython
buildozer android debug
```

### Java Not Found
→ Install Java 11+:
```powershell
# Via Chocolatey
choco install openjdk11

# Or download from oracle.com
```

### Build Takes Forever
→ Normal! First build takes 10-20 minutes. Subsequent builds are faster.

### "Android SDK not found"
→ Buildozer will download it. Just wait for the first build.

---

## 📱 Installation on Phone

### USB Method
```powershell
adb install -r bin/p2pshare-1.0-debug.apk
```

### Manual Method
1. Transfer APK file to phone
2. Tap the file
3. Tap "Install"
4. Grant permissions
5. Done!

---

## ✅ Quick Checklist

- [ ] Python 3.11 or 3.12 installed
- [ ] Java installed
- [ ] Run build script (`.\build_apk.ps1`)
- [ ] Wait for build (10-20 minutes first time)
- [ ] Find APK in `bin/` folder
- [ ] Transfer to Android device
- [ ] Install via tap or ADB
- [ ] Launch app

---

## 📊 Build Info

| Item | Value |
|------|-------|
| App | P2P Paylaş |
| Package | org.p2p.p2pshare |
| Min Android | 5.0 (API 21) |
| Target Android | 12 (API 31) |
| APK Size | ~60 MB |
| Build Time | 10-20 min (first), 5 min (subsequent) |

---

## 🆘 Need Help?

1. **Read:** `APK_BUILD_GUIDE.md` (detailed guide)
2. **Check:** `.buildozer/android/platform/build-*/build/logs/` (error logs)
3. **Retry:** `buildozer android debug --clean` (clean build)
4. **Verbose:** `buildozer android debug -v` (detailed output)

---

## ✨ That's it!

Your P2P Paylaş Android app will be ready in the `bin/` folder. 🎉

Questions? Check the full documentation in the project folder.

---
