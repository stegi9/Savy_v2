import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../l10n/app_strings.dart';

// State class to hold preferences
class PreferencesState {
  final ThemeMode themeMode;
  final Locale locale;

  const PreferencesState({
    required this.themeMode,
    required this.locale,
  });

  PreferencesState copyWith({
    ThemeMode? themeMode,
    Locale? locale,
  }) {
    return PreferencesState(
      themeMode: themeMode ?? this.themeMode,
      locale: locale ?? this.locale,
    );
  }
}

// Notifier to manage state
class PreferencesNotifier extends StateNotifier<PreferencesState> {
  final SharedPreferences _prefs;

  PreferencesNotifier(this._prefs)
      : super(const PreferencesState(
          themeMode: ThemeMode.light,
          locale: Locale('it'),
        )) {
    _loadPreferences();
  }

  void _loadPreferences() {
    // Load Theme
    final isDark = _prefs.getBool('is_dark_mode') ?? false;
    // Load Locale
    final languageCode = _prefs.getString('language_code') ?? 'it';
    
    // Update State
    state = PreferencesState(
      themeMode: isDark ? ThemeMode.dark : ThemeMode.light,
      locale: Locale(languageCode),
    );
    
    // Update global string helper
    AppStrings.setLocale(languageCode);
  }

  Future<void> toggleTheme(bool isDark) async {
    await _prefs.setBool('is_dark_mode', isDark);
    state = state.copyWith(
      themeMode: isDark ? ThemeMode.dark : ThemeMode.light,
    );
  }

  Future<void> setLocale(String languageCode) async {
    if (!['it', 'en'].contains(languageCode)) return;
    
    await _prefs.setString('language_code', languageCode);
    state = state.copyWith(
      locale: Locale(languageCode),
    );
    AppStrings.setLocale(languageCode);
  }
  
  bool get isDarkMode => state.themeMode == ThemeMode.dark;
  bool get isItalian => state.locale.languageCode == 'it';
}

// Provider definition
final sharedPreferencesProvider = Provider<SharedPreferences>((ref) {
  throw UnimplementedError('SharedPreferences must be overridden in main.dart');
});

final preferencesProvider = StateNotifierProvider<PreferencesNotifier, PreferencesState>((ref) {
  final prefs = ref.watch(sharedPreferencesProvider);
  return PreferencesNotifier(prefs);
});
