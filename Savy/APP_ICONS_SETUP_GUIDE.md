# 🎨 App Icons & Assets Setup Guide - SAVY

Guida completa per configurare icone, splash screen e assets per Android e iOS.

---

## 📦 ASSETS NECESSARI

### 1. **App Icon** (Obbligatorio)
- **Dimensione**: 1024x1024px
- **Formato**: PNG con trasparenza (iOS) / PNG senza trasparenza (Android)
- **Background**: Colore solido o gradiente
- **Design**: Logo Savy centrato, margini sicuri di 10%

### 2. **Splash Screen**
- **Dimensione**: 2048x2048px (verrà ridimensionato)
- **Formato**: PNG con trasparenza
- **Design**: Logo Savy su background bianco/nero

### 3. **Notification Icon** (Android)
- **Dimensione**: 192x192px
- **Formato**: PNG monocromatico (bianco su trasparente)
- **Design**: Versione semplificata del logo

---

## 🚀 METODO 1: Automatico con flutter_launcher_icons

### 1. Installa Package

Già presente in `pubspec.yaml`:
```yaml
dev_dependencies:
  flutter_launcher_icons: ^0.13.1
```

### 2. Configura

Crea `flutter_launcher_icons.yaml`:

```yaml
flutter_launcher_icons:
  android: true
  ios: true
  image_path: "assets/icons/app_icon.png"
  
  # Android specifics
  adaptive_icon_background: "#667eea"  # Savy primary color
  adaptive_icon_foreground: "assets/icons/app_icon_foreground.png"
  
  # iOS specifics
  remove_alpha_ios: true
  
  # Web
  web:
    generate: true
    image_path: "assets/icons/app_icon.png"
    background_color: "#FFFFFF"
    theme_color: "#667eea"
  
  # Windows
  windows:
    generate: true
    image_path: "assets/icons/app_icon.png"
    icon_size: 48
```

### 3. Prepara Assets

Crea struttura:
```
frontend/
  assets/
    icons/
      app_icon.png              (1024x1024)
      app_icon_foreground.png   (1024x1024, solo foreground)
    images/
      splash_logo.png           (512x512)
      splash_logo_dark.png      (512x512)
```

### 4. Genera Icons

```bash
cd frontend
flutter pub get
flutter pub run flutter_launcher_icons
```

---

## 🎨 DESIGN ASSETS CON CANVA/FIGMA

### Template Figma Gratuito

1. Vai su https://www.figma.com/community
2. Cerca "App Icon Template"
3. Usa template con dimensioni corrette
4. Export PNG @1x, @2x, @3x

### Design Guidelines

#### **App Icon**
```
┌─────────────────────┐
│                     │  Safe area: 80%
│    ┌─────────┐      │  Evita angoli
│    │  SAVY   │      │  
│    │  LOGO   │      │  Background: Gradiente Savy
│    └─────────┘      │  (#667eea → #764ba2)
│                     │
└─────────────────────┘
```

#### **Splash Logo**
```
┌─────────────────────┐
│                     │
│                     │
│    ┌─────────┐      │  Logo centrato
│    │  SAVY   │      │  Background: Bianco/Nero
│    └─────────┘      │  
│                     │
│                     │
└─────────────────────┘
```

---

## 📱 ANDROID ADAPTIVE ICONS

### Cosa sono?

Android 8.0+ supporta "adaptive icons" con:
- **Foreground**: Logo (con trasparenza)
- **Background**: Colore solido o immagine

### Setup

1. **Foreground** (`app_icon_foreground.png`):
   - Solo logo centrato
   - Trasparenza attorno
   - Safe area: 66% centrale

2. **Background**:
   - Colore: `#667eea` (Savy primary)
   - Oppure gradiente come immagine

### Genera

```bash
flutter pub run flutter_launcher_icons
```

Verrà creato:
```
android/app/src/main/res/
  mipmap-hdpi/ic_launcher.png
  mipmap-mdpi/ic_launcher.png
  mipmap-xhdpi/ic_launcher.png
  mipmap-xxhdpi/ic_launcher.png
  mipmap-xxxhdpi/ic_launcher.png
```

---

## 🍎 iOS APP ICON

### Requisiti

- **NO trasparenza** (verrà aggiunta mask automaticamente)
- **Angoli squadrati** (iOS applica rounded corners)
- Tutte le dimensioni generate automaticamente

### Verifica in Xcode

1. Apri `ios/Runner.xcworkspace`
2. Navigator → **Assets.xcassets**
3. **AppIcon** dovrebbe contenere tutte le dimensioni
4. Check che non ci siano warning

---

## 💦 SPLASH SCREEN

Già configurato in `flutter_native_splash.yaml`. Assicurati di avere:

```yaml
flutter_native_splash:
  color: "#FFFFFF"
  color_dark: "#000000"
  image: assets/images/splash_logo.png
  image_dark: assets/images/splash_logo_dark.png
  android_12:
    image: assets/images/splash_logo.png
    color: "#667eea"
```

Genera:
```bash
flutter pub run flutter_native_splash:create
```

---

## 🔔 NOTIFICATION ICON (Android)

### Design

- **Solo bianco su trasparente**
- **Versione semplificata** del logo
- NO gradienti, NO colori (Android applica tint)

### Setup Manuale

1. Crea `notification_icon.png` (192x192, bianco monocromatico)
2. Genera tutte le densità:
   ```
   android/app/src/main/res/
     drawable-mdpi/ic_notification.png    (24x24)
     drawable-hdpi/ic_notification.png    (36x36)
     drawable-xhdpi/ic_notification.png   (48x48)
     drawable-xxhdpi/ic_notification.png  (72x72)
     drawable-xxxhdpi/ic_notification.png (96x96)
   ```

3. Update `AndroidManifest.xml`:
   ```xml
   <meta-data
       android:name="com.google.firebase.messaging.default_notification_icon"
       android:resource="@drawable/ic_notification" />
   ```

---

## 🖼 STORE ASSETS

### Google Play Store

Necessari per pubblicazione:

1. **Feature Graphic**: 1024x500px
2. **Screenshots**:
   - Phone: 1080x1920px (min 2, max 8)
   - Tablet 7": 1200x1920px (opzionale)
   - Tablet 10": 2048x2732px (opzionale)
3. **App Icon**: 512x512px
4. **Promo Video** (YouTube, opzionale)

### Apple App Store

1. **App Icon**: 1024x1024px (NO trasparenza)
2. **Screenshots**:
   - 6.5" (iPhone 14 Pro Max): 1284x2778px
   - 5.5" (iPhone 8 Plus): 1242x2208px
   - 12.9" iPad Pro: 2048x2732px
3. **App Preview** (video, opzionale)

---

## 🛠 TOOLS UTILI

### Online Generators

1. **App Icon Generator**:
   - https://appicon.co
   - Upload 1024x1024, download tutti i formati

2. **Adaptive Icon Generator**:
   - https://adapticon.tooo.io
   - Preview come apparirà su vari device

3. **Screenshot Frames**:
   - https://screenshots.pro
   - Aggiungi frame device attorno agli screenshot

### Design Tools

- **Figma**: https://figma.com (gratuito)
- **Canva**: https://canva.com (template app icon)
- **Sketch**: https://sketch.com (macOS)

---

## ✅ CHECKLIST PRE-LAUNCH

### Android
- [ ] App icon generato (tutte le densità)
- [ ] Adaptive icon configurato
- [ ] Notification icon monocromatico
- [ ] Splash screen configurato
- [ ] Feature graphic 1024x500
- [ ] Screenshots (min 2)

### iOS
- [ ] App icon 1024x1024 (senza trasparenza)
- [ ] Splash screen configurato
- [ ] Screenshots 6.5" e 5.5"
- [ ] App Store icon verificato in Xcode

### Both
- [ ] Assets in `.gitignore` (se contengono branding confidenziale)
- [ ] Test su device reali
- [ ] Verifica risoluzione corretta
- [ ] Check che non ci siano artefatti

---

## 🎨 BRAND COLORS SAVY

Per consistency:

```
Primary:   #667eea
Accent:    #764ba2
Success:   #10b981
Error:     #ef4444
Warning:   #f59e0b
Info:      #3b82f6
```

---

## 📦 EXPORT FINALE

### Da Figma/Canva

Export in PNG:
- **@1x**: Dimensione base
- **@2x**: 2x dimensione (Retina)
- **@3x**: 3x dimensione (iPhone Plus/Pro)

### Da Photoshop

File → Export → Export As:
- Format: PNG-24
- Transparency: Yes (per splash/icon foreground)
- Resize: Yes (per varie densità)

---

## 🚀 TEST FINALE

```bash
# Android
flutter build apk
flutter install

# iOS
flutter build ios
# Open in Xcode e test su Simulator/Device

# Verifica:
# - Icon appare correttamente nella home
# - Splash screen animato
# - Notifica mostra icon corretto
```

---

**Assets completati! 🎨**

La tua app ora ha tutti gli assets professionali per il launch.
