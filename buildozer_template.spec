[app]
# Application title and package
title = P2P Paylaş
package.name = p2pshare
package.domain = org.p2p

# Source and build
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf

# Version
version = 1.0

# Main script
main.py

# Requirements
requirements = python3,kivy,kivymd,pillow,jnius

# Permissions
android.permissions = INTERNET,ACCESS_NETWORK_STATE,CHANGE_NETWORK_STATE,CHANGE_WIFI_STATE,ACCESS_WIFI_STATE

# Features (optional)
android.features = android.hardware.wifi

# API level
android.api = 31
android.minapi = 21
android.ndk = 25b

# Architecture
android.archs = arm64-v8a,armeabi-v7a

# Orientation
orientation = portrait

# Icons and assets
# icon.filename = %(source.dir)s/data/icon.png
# presplash.filename = %(source.dir)s/data/presplash.png

# Android specific
android.logcat_filters = *:S python:D
android.bootstrap = sdl2

# Services (optional, for background transfers)
# services = P2P:service.P2PService

[buildozer]
log_level = 2
warn_on_root = 1
