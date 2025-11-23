# P2P Paylaş - Android APK Build Guide

## Overview
This guide explains how to build the P2P Paylaş application as an Android APK (Android Package).

**Current Status:** Buildozer is not compatible with Python 3.14 due to removed `FancyURLopener` from `urllib.request`. Follow the alternative methods below.

## Method 1: Using Python 3.11 Virtual Environment (Recommended)

### Step 1: Install Python 3.11
Download Python 3.11 from [python.org](https://www.python.org/downloads/) and install it.

### Step 2: Create Virtual Environment
```powershell
# Create a Python 3.11 virtual environment
py -3.11 -m venv venv_android

# Activate it
.\venv_android\Scripts\Activate.ps1

# Upgrade pip
python -m pip install --upgrade pip setuptools
```

### Step 3: Install Build Dependencies
```powershell
pip install buildozer cython kivy kivymd pillow jnius
```

### Step 4: Build APK
```powershell
# Navigate to project directory
cd "c:\Users\mehme\Desktop\p2p\p2p-main"

# Build APK
buildozer android debug
```

The APK will be created in the `bin/` directory.

## Method 2: Using Kivy Buildozer on Linux/WSL

If you have Windows Subsystem for Linux (WSL) installed:

```bash
# Install WSL dependencies
sudo apt-get update
sudo apt-get install -y python3.11 python3.11-venv build-essential libffi-dev libssl-dev

# Create virtual environment
python3.11 -m venv venv_android

# Activate
source venv_android/bin/activate

# Install buildozer
pip install buildozer cython

# Build
buildozer android debug
```

## Method 3: Using Kivy's Cloud Build Service

1. Visit [Kivy Cloud Build](https://buildozer.io)
2. Upload your `buildozer.spec` and source files
3. Select Android platform
4. Start build process
5. Download generated APK

## APK Configuration Details

The `buildozer.spec` includes:

- **App Name:** P2P Paylaş
- **Package:** org.p2p.p2pshare
- **Version:** 1.0
- **Minimum API:** 21 (Android 5.0)
- **Target API:** 31 (Android 12)
- **Architectures:** arm64-v8a, armeabi-v7a

### Permissions Included:
- `INTERNET` - TCP socket communication
- `ACCESS_NETWORK_STATE` - Check network connectivity
- `CHANGE_NETWORK_STATE` - Manage connections
- `CHANGE_WIFI_STATE` - Control WiFi
- `ACCESS_WIFI_STATE` - Monitor WiFi status
- `WAKE_LOCK` - Prevent device sleep during transfers

### Features:
- KivyMD Material Design UI
- Samsung One UI styling (squircles, Samsung Blue)
- Complete Turkish localization
- pyjnius integration for native Android APIs
- Dynamic buffer optimization
- Directory compression support

## Troubleshooting

### Issue: `FancyURLopener` ImportError
**Solution:** Use Python 3.11 or 3.12 instead of 3.14. Buildozer hasn't been updated for Python 3.13+.

### Issue: Java not found
**Solution:** Install Java Development Kit (JDK 11 or higher)
```powershell
# Using Chocolatey
choco install openjdk11
```

### Issue: Android SDK/NDK not found
**Solution:** Set environment variables in `buildozer.spec`:
```
android.sdk_path = C:\Android\sdk
android.ndk_path = C:\Android\ndk\25b
```

### Issue: Build fails with permission errors
**Solution:** Check antivirus software isn't blocking build process. Temporarily disable during build.

## APK Installation and Testing

### Install on Android Device
```powershell
# Using ADB (Android Debug Bridge)
adb install -r bin/p2pshare-1.0-debug.apk

# Or open APK directly on device and tap to install
```

### Testing Checklist
- [ ] App launches successfully
- [ ] Samsung One UI styling displays correctly
- [ ] Turkish UI text renders properly
- [ ] WiFi list appears
- [ ] Can connect to another device
- [ ] File transfer initiates
- [ ] WakeLock prevents sleep during transfer
- [ ] Directory compression works

## Build Output Structure

```
p2p-main/
├── buildozer.spec          # Build configuration
├── bin/
│   ├── p2pshare-1.0-debug.apk       # Final APK file
│   └── p2pshare-1.0-debug.apk.asc   # Signature file
├── .buildozer/
│   └── android/             # Build artifacts
├── main.py                  # KivyMD Android UI
├── p2p.py                   # Core P2P logic
└── README.md                # Documentation
```

## Performance Notes

- **APK Size:** Expected ~50-80 MB (includes Kivy, KivyMD, Python runtime)
- **Runtime:** First launch ~5-10 seconds (Kivy initialization)
- **Memory:** ~150-200 MB when running
- **Buffer Optimization:** Automatically adjusts chunk size for file size

## Release Build

To create a production release APK:

```powershell
# Modify buildozer.spec
# Change: android.release_artifact = aab (for Google Play)
# Or: android.release_artifact = apk

# Create signed APK
buildozer android release

# Sign with your keystore
jarsigner -verbose -sigalg SHA1withRSA -digestalg SHA1 \
  -keystore my-release-key.jks \
  bin/p2pshare-1.0-release.apk alias_name
```

## Files Generated

- **p2pshare-1.0-debug.apk** - Debug version for testing
- **p2pshare-1.0-release.apk** - Release version for distribution
- **p2pshare-1.0-release.aab** - Android App Bundle for Google Play

## Additional Resources

- [Buildozer Documentation](https://buildozer.readthedocs.io/)
- [Kivy Android Guide](https://kivy.org/doc/stable/guide/android.html)
- [KivyMD Documentation](https://kivymd.readthedocs.io/)
- [Android Developers](https://developer.android.com/)

## Support

For issues:
1. Check buildozer logs: `.buildozer/android/platform/build-<arch>/build/logs/`
2. Run with verbose: `buildozer android debug -v`
3. Clean build: `buildozer android debug --clean`

---
**Last Updated:** 2024
**Python Version:** 3.11+ (3.12 recommended)
**Buildozer Version:** Latest stable
