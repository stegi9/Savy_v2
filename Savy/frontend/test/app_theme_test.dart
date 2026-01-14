import 'package:flutter_test/flutter_test.dart';
import 'package:savy_frontend/core/theme/app_theme.dart';
import 'package:savy_frontend/core/theme/app_colors.dart';

void main() {
  group('AppTheme', () {
    test('lightTheme has correct primary color', () {
      final theme = AppTheme.lightTheme;
      expect(theme.primaryColor, AppColors.primary);
      expect(theme.colorScheme.primary, AppColors.primary);
    });

    test('lightTheme has correct background color', () {
      final theme = AppTheme.lightTheme;
      expect(theme.scaffoldBackgroundColor, AppColors.background);
    });

    test('darkTheme has correct primary color', () {
      final theme = AppTheme.darkTheme;
      expect(theme.primaryColor, AppColors.primary);
      expect(theme.colorScheme.primary, AppColors.primary);
    });
    
    test('darkTheme has correct background color', () {
       final theme = AppTheme.darkTheme;
       expect(theme.scaffoldBackgroundColor, AppColors.backgroundDark);
    });
  });
}
