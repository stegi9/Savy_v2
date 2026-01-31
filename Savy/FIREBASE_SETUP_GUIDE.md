# 🔥 Firebase Configuration Guide - SAVY

Guida completa per configurare Firebase Cloud Messaging (push notifications) in Savy.

---

## 📋 PREREQUISITI

- Account Firebase (gratuito): https://console.firebase.google.com
- Flutter SDK installato
- Android Studio / Xcode
- FlutterFire CLI installato: `dart pub global activate flutterfire_cli`

---

## 🚀 SETUP FIREBASE PROJECT

### 1. Crea Progetto Firebase

1. Vai su https://console.firebase.google.com
2. Click **"Aggiungi progetto"**
3. Nome progetto: `Savy` (o altro nome)
4. Abilita Google Analytics (opzionale ma consigliato)
5. Click **"Crea progetto"**

### 2. Aggiungi App Android

1. Nel dashboard Firebase, click icona **Android**
2. **Package name**: `com.savy.app` (deve corrispondere a `android/app/build.gradle`)
3. **App nickname** (opzionale): `Savy Android`
4. **SHA-1** (opzionale, ma necessario per autenticazione Google):
   ```bash
   cd frontend/android
   ./gradlew signingReport
   # Copia SHA-1 dalla sezione "debug"
   ```
5. Click **"Registra app"**
6. **Scarica `google-services.json`**
7. Posiziona in: `frontend/android/app/google-services.json`

### 3. Aggiungi App iOS

1. Nel dashboard Firebase, click icona **Apple**
2. **iOS bundle ID**: `com.savy.app` (deve corrispondere a Xcode project)
3. **App nickname**: `Savy iOS`
4. **App Store ID** (opzionale, per ora lascia vuoto)
5. Click **"Registra app"**
6. **Scarica `GoogleService-Info.plist`**
7. Posiziona in: `frontend/ios/Runner/GoogleService-Info.plist`
   - Apri progetto in Xcode
   - Trascina file nella cartella `Runner`
   - **Assicurati** che "Copy items if needed" sia selezionato

---

## ⚙️ CONFIGURAZIONE ANDROID

### 1. Modifica `android/build.gradle`

```gradle
buildscript {
    dependencies {
        // Aggiungi questa linea
        classpath 'com.google.gms:google-services:4.4.0'
    }
}
```

### 2. Modifica `android/app/build.gradle`

```gradle
apply plugin: 'com.android.application'
apply plugin: 'kotlin-android'
apply plugin: 'dev.flutter.flutter-gradle-plugin'

// Aggiungi questa linea ALLA FINE
apply plugin: 'com.google.gms.google-services'
```

### 3. Verifica `AndroidManifest.xml`

Assicurati che `android/app/src/main/AndroidManifest.xml` contenga:

```xml
<manifest>
    <application>
        <!-- ... -->
        
        <!-- Firebase Cloud Messaging -->
        <meta-data
            android:name="com.google.firebase.messaging.default_notification_channel_id"
            android:value="high_importance_channel" />
        
        <meta-data
            android:name="com.google.firebase.messaging.default_notification_icon"
            android:resource="@drawable/ic_notification" />
            
        <meta-data
            android:name="com.google.firebase.messaging.default_notification_color"
            android:resource="@color/notification_color" />
    </application>
</manifest>
```

---

## 🍎 CONFIGURAZIONE iOS

### 1. Abilita Push Notifications in Xcode

1. Apri `frontend/ios/Runner.xcworkspace` in Xcode
2. Seleziona target **Runner**
3. Tab **"Signing & Capabilities"**
4. Click **"+ Capability"**
5. Aggiungi **"Push Notifications"**
6. Aggiungi **"Background Modes"**
   - Seleziona: **"Remote notifications"**

### 2. Modifica `Info.plist`

Aggiungi in `ios/Runner/Info.plist`:

```xml
<key>FirebaseAppDelegateProxyEnabled</key>
<false/>
```

### 3. Configura APNs (Apple Push Notification service)

1. Vai su https://developer.apple.com
2. **Certificates, IDs & Profiles** → **Keys**
3. Click **"+"** per creare nuova key
4. Nome: `Savy Push Notifications`
5. Abilita **"Apple Push Notifications service (APNs)"**
6. Download `.p8` file (salvalo in luogo sicuro!)
7. Torna su Firebase Console:
   - **Project Settings** → **Cloud Messaging**
   - Tab **Apple**
   - Upload `.p8` file
   - Inserisci **Key ID** e **Team ID**

---

## 🧪 TEST PUSH NOTIFICATIONS

### 1. Run App

```bash
cd frontend
flutter run
```

### 2. Ottieni FCM Token

Il token viene stampato nei log al primo avvio:
```
FCM Token: fXXXXXXXXXXXXXX...
```

### 3. Invia Notifica Test da Firebase Console

1. Firebase Console → **Cloud Messaging**
2. Click **"Send your first message"**
3. Inserisci titolo e testo
4. Click **"Send test message"**
5. Incolla FCM token
6. Click **"Test"**

---

## 📱 VERIFICA FUNZIONAMENTO

### Test Completo

1. **Foreground (app aperta)**:
   - Notifica appare come banner in-app
   - Check log: `Foreground message: ...`

2. **Background (app in background)**:
   - Notifica appare nella barra notifiche
   - Tap per aprire app
   - Check log: `Background message: ...`

3. **Terminated (app chiusa)**:
   - Notifica appare nella barra notifiche
   - Tap per lanciare app
   - Check log: `Notification tapped: ...`

---

## 🔐 SICUREZZA

### Produzione

1. **Android**: Usa **release keystore** (non debug)
2. **iOS**: Usa **production APNs key** (non development)
3. **Firebase Rules**: Limita accesso a Cloud Messaging

### `.gitignore` (GIÀ CONFIGURATO)

```
android/app/google-services.json
ios/Runner/GoogleService-Info.plist
```

---

## ❌ TROUBLESHOOTING

### Android: "google-services.json not found"

```bash
# Verifica posizione file
ls frontend/android/app/google-services.json

# Sync Gradle
cd frontend/android
./gradlew clean
./gradlew build
```

### iOS: "FirebaseApp.configure() not called"

Assicurati che `main.dart` contenga:

```dart
void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await Firebase.initializeApp();
  runApp(MyApp());
}
```

### Token non viene generato

```dart
// Check permissions
final settings = await FirebaseMessaging.instance.requestPermission();
print('Permission: ${settings.authorizationStatus}');

// Force token refresh
await FirebaseMessaging.instance.deleteToken();
final token = await FirebaseMessaging.instance.getToken();
print('New token: $token');
```

### Notifiche non arrivano

1. Check che l'app sia in foreground/background
2. Verifica FCM token sia salvato nel backend
3. Check Firebase Console → Cloud Messaging logs
4. Verifica device abbia connessione internet

---

## 📊 ANALYTICS (OPZIONALE)

Firebase include gratuitamente Google Analytics:

1. Firebase Console → **Analytics**
2. View eventi automatici (app_open, screen_view, ecc.)
3. Track custom events dal codice:

```dart
import 'package:firebase_analytics/firebase_analytics.dart';

final analytics = FirebaseAnalytics.instance;
await analytics.logEvent(
  name: 'transaction_created',
  parameters: {'amount': 50.0, 'category': 'food'},
);
```

---

## 🚀 DEPLOY

### Before Production

1. **Android**:
   - Genera release keystore
   - Firma APK con release key
   - Update SHA-1 in Firebase

2. **iOS**:
   - Use production APNs key
   - Enable push notifications in App Store Connect
   - Test su device reale (non simulator)

3. **Backend**:
   - Save FCM tokens in database
   - Implement notification scheduling
   - Rate limit notifications

---

## 📚 RISORSE

- **Firebase Docs**: https://firebase.google.com/docs/flutter/setup
- **FlutterFire**: https://firebase.flutter.dev/
- **FCM Docs**: https://firebase.google.com/docs/cloud-messaging
- **APNs Guide**: https://developer.apple.com/documentation/usernotifications

---

**Setup completato! 🎉**

Le notifiche push sono ora configurate per Savy.
