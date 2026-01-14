import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:savy_frontend/core/l10n/app_strings.dart';
import 'package:savy_frontend/core/providers/preferences_provider.dart';

void main() {
  group('AppStrings', () {
    test('Default locale is Italian', () {
      expect(AppStrings.isItalian, isTrue);
      expect(AppStrings.currentLocale, 'it');
      expect(AppStrings.get('settingsTitle'), 'Impostazioni');
    });

    test('Switching to English works', () {
      AppStrings.setLocale('en');
      expect(AppStrings.currentLocale, 'en');
      expect(AppStrings.isItalian, isFalse);
      expect(AppStrings.get('settingsTitle'), 'Settings');
    });

    test('Switching back to Italian works', () {
      AppStrings.setLocale('it');
      expect(AppStrings.isItalian, isTrue);
      expect(AppStrings.get('settingsTitle'), 'Impostazioni');
    });

    test('Invalid locale is ignored', () {
      AppStrings.setLocale('it');
      AppStrings.setLocale('fr'); // Not supported
      expect(AppStrings.currentLocale, 'it');
    });
  });

  group('PreferencesNotifier', () {
    test('Initializes with default values from SharedPreferences', () async {
      SharedPreferences.setMockInitialValues({}); // Empty prefs
      final prefs = await SharedPreferences.getInstance();
      
      final container = ProviderContainer(
        overrides: [
          sharedPreferencesProvider.overrideWithValue(prefs),
        ],
      );

      final state = container.read(preferencesProvider);
      expect(state.themeMode, ThemeMode.light);
      expect(state.locale.languageCode, 'it');
    });

    test('Initializes with saved values', () async {
      SharedPreferences.setMockInitialValues({
        'is_dark_mode': true,
        'language_code': 'en',
      });
      final prefs = await SharedPreferences.getInstance();

      final container = ProviderContainer(
        overrides: [
          sharedPreferencesProvider.overrideWithValue(prefs),
        ],
      );

      // Force load
      final notifier = container.read(preferencesProvider.notifier);
      // Wait for async load if needed, but constructor runs synchronously with mock data usually?
      // Actually _loadPreferences is synchronous in my implementation.
      
      final state = container.read(preferencesProvider);
      expect(state.themeMode, ThemeMode.dark);
      expect(state.locale.languageCode, 'en');
      expect(AppStrings.currentLocale, 'en'); // Side effect check
    });

    test('toggleTheme updates state and prefs', () async {
      SharedPreferences.setMockInitialValues({});
      final prefs = await SharedPreferences.getInstance();
      final container = ProviderContainer(
        overrides: [
          sharedPreferencesProvider.overrideWithValue(prefs),
        ],
      );
      final notifier = container.read(preferencesProvider.notifier);

      await notifier.toggleTheme(true);
      
      expect(container.read(preferencesProvider).themeMode, ThemeMode.dark);
      expect(prefs.getBool('is_dark_mode'), isTrue);
    });

    test('setLocale updates state and prefs', () async {
      SharedPreferences.setMockInitialValues({});
      final prefs = await SharedPreferences.getInstance();
      final container = ProviderContainer(
        overrides: [
          sharedPreferencesProvider.overrideWithValue(prefs),
        ],
      );
      final notifier = container.read(preferencesProvider.notifier);

      await notifier.setLocale('en');

      expect(container.read(preferencesProvider).locale.languageCode, 'en');
      expect(prefs.getString('language_code'), 'en');
      expect(AppStrings.currentLocale, 'en');
    });
  });
}
