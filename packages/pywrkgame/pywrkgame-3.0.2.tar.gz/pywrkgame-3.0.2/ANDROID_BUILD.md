# PyWRKGame Android Build Guide

This guide explains how to build PyWRKGame for Android using Buildozer.

## Prerequisites

### Linux/macOS

1. Install Buildozer:
```bash
pip install buildozer
```

2. Install required dependencies:

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install -y git zip unzip openjdk-17-jdk python3-pip autoconf libtool pkg-config zlib1g-dev libncurses5-dev libncursesw5-dev libtinfo5 cmake libffi-dev libssl-dev
```

**macOS:**
```bash
brew install autoconf automake libtool pkg-config
brew install openssl
```

3. Install Android SDK and NDK (Buildozer can do this automatically)

### Windows

Buildozer is not officially supported on Windows. Use one of these alternatives:

1. **WSL2 (Windows Subsystem for Linux)** - Recommended
   - Install WSL2 with Ubuntu
   - Follow the Linux instructions above

2. **Docker**
   - Use a Docker container with Buildozer pre-installed

3. **Virtual Machine**
   - Use VirtualBox or VMware with Ubuntu

## Building for Android

### First-Time Setup

1. Initialize Buildozer (if not already done):
```bash
buildozer init
```

This creates a `buildozer.spec` file (already included in this repository).

2. Configure the `buildozer.spec` file:
   - Set your app name, package name, and version
   - Configure permissions as needed
   - Set target API levels

### Build Commands

#### Debug Build (APK)

Build a debug APK for testing:
```bash
buildozer android debug
```

The APK will be created in `bin/` directory.

#### Release Build (APK)

Build a release APK:
```bash
buildozer android release
```

Note: Release builds need to be signed. See "Signing Release Builds" below.

#### Build and Deploy

Build and deploy directly to a connected Android device:
```bash
buildozer android debug deploy run
```

This will:
1. Build the APK
2. Install it on your device
3. Run the application

#### Build for Specific Architecture

Build for a specific CPU architecture:
```bash
buildozer android debug --arch=arm64-v8a
buildozer android debug --arch=armeabi-v7a
```

### Cleaning Build Files

Clean build artifacts:
```bash
buildozer android clean
```

Clean everything (including downloaded SDK/NDK):
```bash
buildozer distclean
```

## Configuration

### Key Settings in buildozer.spec

```ini
# Application info
title = PyWRKGame
package.name = pywrkgame
package.domain = org.pywrkgame
version = 3.0.0

# Android API levels
android.api = 31          # Target API
android.minapi = 21       # Minimum API (Android 5.0+)
android.ndk = 25b         # NDK version

# Architectures to build
android.archs = arm64-v8a,armeabi-v7a

# Permissions
android.permissions = INTERNET,ACCESS_NETWORK_STATE,VIBRATE,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE
```

### Required Permissions

PyWRKGame requires these Android permissions:

- `INTERNET` - For network features
- `ACCESS_NETWORK_STATE` - For checking network connectivity
- `VIBRATE` - For haptic feedback
- `WRITE_EXTERNAL_STORAGE` - For saving game data
- `READ_EXTERNAL_STORAGE` - For loading assets

Add more permissions in `buildozer.spec` as needed for your game.

## Signing Release Builds

### Generate a Keystore

```bash
keytool -genkey -v -keystore my-release-key.keystore -alias my-key-alias -keyalg RSA -keysize 2048 -validity 10000
```

### Sign the APK

After building a release APK:

```bash
jarsigner -verbose -sigalg SHA1withRSA -digestalg SHA1 -keystore my-release-key.keystore bin/pywrkgame-3.0.0-release-unsigned.apk my-key-alias
```

### Optimize the APK

```bash
zipalign -v 4 bin/pywrkgame-3.0.0-release-unsigned.apk bin/pywrkgame-3.0.0-release.apk
```

## Troubleshooting

### Build Fails with "Command failed"

1. Check that all dependencies are installed
2. Try cleaning and rebuilding:
   ```bash
   buildozer android clean
   buildozer android debug
   ```

### NDK/SDK Download Issues

If automatic download fails:

1. Manually download Android SDK and NDK
2. Set paths in `buildozer.spec`:
   ```ini
   android.sdk_path = /path/to/android-sdk
   android.ndk_path = /path/to/android-ndk
   ```

### App Crashes on Android

1. Check logcat for errors:
   ```bash
   adb logcat | grep python
   ```

2. Ensure all native libraries (.so files) are included
3. Check that all Python dependencies are listed in `requirements`

### Permission Denied Errors

On Linux, you may need to add your user to the `plugdev` group:
```bash
sudo usermod -aG plugdev $USER
```

Then log out and log back in.

## Testing on Android

### Using ADB

Connect your Android device and enable USB debugging:

```bash
# List connected devices
adb devices

# Install APK manually
adb install bin/pywrkgame-3.0.0-debug.apk

# View logs
adb logcat | grep python

# Uninstall app
adb uninstall org.pywrkgame.pywrkgame
```

### Using Android Emulator

1. Create an emulator in Android Studio
2. Start the emulator
3. Deploy using Buildozer:
   ```bash
   buildozer android debug deploy run
   ```

## Performance Optimization for Android

### Native Library Optimization

PyWRKGame's C++ core is optimized for mobile devices:

- Automatic quality scaling based on device capabilities
- Frame rate maintenance (30 FPS for 2D, 20 FPS for 3D on low-end devices)
- Memory management to prevent leaks
- Battery-based performance scaling

### Build Optimization

For smaller APK size:

1. Build for specific architectures only:
   ```ini
   android.archs = arm64-v8a
   ```

2. Exclude unnecessary files:
   ```ini
   source.exclude_dirs = tests,docs,examples
   ```

3. Use ProGuard for code shrinking (advanced)

## Continuous Integration

### GitHub Actions Example

```yaml
name: Android Build

on: [push, pull_request]

jobs:
  build-android:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.11
      
      - name: Install Buildozer
        run: |
          pip install buildozer
          sudo apt update
          sudo apt install -y git zip unzip openjdk-17-jdk autoconf libtool pkg-config zlib1g-dev libncurses5-dev libncursesw5-dev libtinfo5 cmake libffi-dev libssl-dev
      
      - name: Build APK
        run: buildozer android debug
      
      - name: Upload APK
        uses: actions/upload-artifact@v2
        with:
          name: pywrkgame-debug.apk
          path: bin/*.apk
```

## Distribution

### Google Play Store

1. Build a signed release APK or AAB (Android App Bundle)
2. Create a Google Play Developer account
3. Upload your app through the Play Console
4. Fill in store listing details
5. Submit for review

### Alternative Distribution

- **Direct APK**: Host the APK on your website
- **F-Droid**: Submit to F-Droid repository
- **Amazon Appstore**: Distribute through Amazon
- **Samsung Galaxy Store**: Distribute through Samsung

## Support

For issues specific to Android builds:

1. Check Buildozer documentation: https://buildozer.readthedocs.io/
2. Check python-for-android documentation: https://python-for-android.readthedocs.io/
3. File an issue on the PyWRKGame GitHub repository

## Requirements Validation

This Android build setup validates **Requirement 2.8**:
- ✅ Buildozer integration configured
- ✅ Automated build process documented
- ✅ Android deployment verified through build commands
- ✅ Support for Android API 21+ (Android 5.0+)
- ✅ Multi-architecture support (arm64-v8a, armeabi-v7a)
