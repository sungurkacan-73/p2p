[app]

# (str) Title of your application
title = P2P Paylaş

# (str) Package name
package.name = p2pshare

# (str) Package domain (needed for android/ios packaging)
package.domain = org.p2p

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,kv,atlas,ttf,txt

# (list) List of inclusions using pattern matching
#source.include_patterns = assets/*,images/*.png

# (list) Source files to exclude (let empty to not exclude anything)
#source.exclude_exts = spec

# (list) List of directory to exclude (let empty to not exclude anything)
#source.exclude_dirs = tests, bin

# (list) List of exclusions using pattern matching
#source.exclude_patterns = license,images/*/*.jpg

# (str) Application versioning (method 1)
version = 1.0

# (str) Application versioning (method 2)
# version.regex = __version__ = ['"](.*)['"]
# version.filename = %(source.dir)s/main.py

# (list) Application requirements
# comma separated e.g. requirements = sqlite3,kivy
requirements = python3,kivy,kivymd,pillow,jnius

# (str) Supported orientations
# Valid values: landscape, portrait, sensorLandscape, sensorPortrait, userPortrait, userLandscape, sensor, user
orientation = portrait

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 0

# (string) Presplash of the application (image or drawable resource) optional
# presplash.filename = %(source.dir)s/data/presplash.png

# (str) Android API level to compile against
android.api = 31

# (int) Minimum API level (something > 12 is recommended)
android.minapi = 21

# (str) Android NDK version to use
android.ndk = 25b

# (bool) Use legacy toolchain, set to False to use NDK build-tools >= 24.0.0
android.build_loophole_ndk = False

# (bool) Copy library instead of making a libpymodules.so
android.copy_libs = 1

# (str) The Android arch to build for, choices: armeabi-v7a, arm64-v8a, x86, x86_64
android.archs = arm64-v8a,armeabi-v7a

# (bool) Enable AndroidX support
android.enable_androidx = True

# (list) Pattern to whitelist for the whole project
#android.whitelist = lib-dynload/termios.so

# (str) Android logcat filters to use
#android.logcat_filters = *:S python:D

# (bool) Copy library instead of making a libpymodules.so
# android.add_src =

# (bool) Indicate if the generated source code should be kept
android.keep_src = False

# (str) Android app theme, default is ok for Kivy-based app
# android.theme = "@android:style/Theme.NoTitleBar"

# (bool) Copy presplash into Android Studio project
# android.presplash_copy = True

# (str) Android logcat filters to use
android.logcat_filters = *:S python:D

# (bool) Android logcat only show python logs
android.logcat_python = True

# (str) Android don't strip symbols
android.skip_update = False

# (str) Android GIT sha, leave empty to download latest pullrequest
android.branch = develop

# (str) OUYA Console icon. It must be a 732x412 png image.
#android.ouya.icon.filename = %(source.dir)s/data/ouya_icon.png

# (str) OUYA Console category. Should be one of GAME or APP
# If you leave this blank, OUYA support will not be enabled.
#android.ouya.category = GAME

# (str) Filename of OUYA Console icon. It must be a 732x412 png image.
#android.ouya.icon.filename = %(source.dir)s/data/ouya_icon.png

# (str) XML file for custom backup rules (see the documentation)
# android.backup_rules =

# (str) If you need to insert variables into your buildozer.spec, you can
# do so by using the token maker feature. Take a look at the section "Token Maker"
# and "Module Configuration" from the buildozer/default.spec in android.py
#android.module_directives =

# (list) Pattern to whitelist for the whole project
#android.whitelist =

# (str) Path to a custom whitelist file
#android.whitelist_src =

# (str) Path to a custom blacklist file
# android.blacklist_src =

# (list) List of Java .jar files to add to the libs so that pydroid can access
# their classes. Don't add jars that you do not need, since extra jars can slow
# down the build process. Allows wildcards matching with * pattern :
# OUYA-ODK/libs/*.jar
android.add_libs_armeabi_v7a = libs/armeabi-v7a/*.jar
android.add_libs_arm64_v8a = libs/arm64-v8a/*.jar

# (bool) Automatically add the Android dir to the build dir
android.add_src =

# (str) android.entrypoint = org.test.myapp.MainActivity

# (str) Full name including package path of the Java class that implements
# Activity class, don't change unless you know what you do (see Class doc to
# learn how to write your own Java class).
#android.activity_class_name = org.kivy.android.PythonActivity

# (str) The Android arch to build for, choices: armeabi-v7a, arm64-v8a, x86, x86_64
# In combination with android.bootstrap = sdl2
android.bootstrap = sdl2

# (int) port (default is 1099)
#android.port = 1099

# (bool) if enabled and you security features in Android is active, you will see the default
# pure python krupto wise with a rest for the key.
# Create a new request you will see a key with chain ideas.
#android.setup_proxy = False

# (bool) Indicate if the Kivy app should request the permission INTERNET
android.permissions = INTERNET,ACCESS_NETWORK_STATE,CHANGE_NETWORK_STATE,CHANGE_WIFI_STATE,ACCESS_WIFI_STATE,WAKE_LOCK

# (bool) Indicate if the Kivy app should have the Permission.INTERNET
android.features = android.hardware.wifi

# (int) Target API to compile against (default is using sdk - 25)
android.release_artifact = aab

# (int) Presplash animation delay, not used if android.presplash = False
android.presplash_animation_delay = 0

# List the toolchain programs to call to process the Java files
#android.gradle_options =

#############################################
# Python for android (p4a) specific
#############################################

# (bool) Indicate if the generated source code should be kept
p4a.source_dir =

# (str) python for android branch to use, defaults to master
p4a.branch = develop

# (str) python for android git specific commit to use, defaults to HEAD, must be within --clone-dir
# p4a.commit = HEAD

# (str) python for android directory (if empty, it will be automatically cloned from github)
#p4a.local_recipes =

# (str) Filename to the hook for p4a (if empty, it will try to find a prebuilt one)
#p4a.hook =

# (str) python for android log level (agg -> aggregate, eg. p4a:S, *:LL)
#p4a.log_level = p4a:S, *:LL

# (int) port number to specify an explicit --port= p4a argument (eg for bootstrap flask
# server etc)
# android.p4a_port =

#############################################
# buildozer logging
#############################################

# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) Display warnings (1 = yes always, 2 = yes when building with buildozer)
warn_on_root = 1

# (str) Path to build artifact storage, absolute or relative to spec file
# build_dir = ./.buildozer

# (str) Path to build output (i.e. .apk, .aab) storage
# bin_dir = ./bin

#############################################
# Gradle Options
#############################################
# (bool) Enable AndroidX support
android.enable_androidx = True

# (str) Android Gradle dependencies
android.gradle_dependencies = 

# (list) Pattern to whitelist for the whole project
#android.whitelist =

# (str) OUYA Console category. Should be one of GAME or APP
# If you leave this blank, OUYA support will not be enabled.
#android.ouya.category = APP

# (str) Filename of OUYA Console icon. It must be a 732x412 png image.
#android.ouya.icon.filename = %(source.dir)s/data/ouya_icon.png

# (str) XML file for custom backup rules (see the documentation)
# android.backup_rules =

#############################################
# iOS specific
#############################################

# (str) Path to a custom kivy-ios folder
#ios.kivy_ios_dir = ../kivy-ios
# Alternately, specify the URL and branch of a git checkout:
ios.kivy_ios_dir = https://github.com/kivy/kivy-ios.git

# Alternately, specify a Git commit to use, this needs kivy-ios master or develop branch
# ios.kivy_ios_commit = HEAD

# Alternately, specify a Git branch to use, if not master, in which case you MUST specify an ios.kivy_ios_commit as well.
# ios.kivy_ios_branch = master

# (bool) Whether or not to sign the code
ios.codesign.allowed = False

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) Display warning (0 = off, 1 = always, 2 = when buildozer is run as not root).
warn_on_root = 1

# (str) Path to build artifact storage, absolute or relative to spec file
# build_dir = ./.buildozer

# (str) Path to build output (i.e. .apk, .aab) storage
# bin_dir = ./bin
