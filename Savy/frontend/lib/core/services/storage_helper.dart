
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

/// Helper class to ensure consistent FlutterSecureStorage configuration
/// across the entire application, avoiding bugs on Android.
class StorageHelper {
  static const _androidOptions = AndroidOptions(
    encryptedSharedPreferences: true,
  );

  static const _iosOptions = IOSOptions(
    accessibility: KeychainAccessibility.first_unlock,
  );

  static const _storage = FlutterSecureStorage(
    aOptions: _androidOptions,
    iOptions: _iosOptions,
  );

  /// Get the configured instance
  static FlutterSecureStorage get instance => _storage;
}
