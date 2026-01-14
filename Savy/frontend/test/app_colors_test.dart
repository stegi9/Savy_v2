import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:savy_frontend/core/theme/app_colors.dart';

void main() {
  group('AppColors', () {
    test('Primary colors are correct', () {
      expect(AppColors.primary, const Color(0xFF14B8A6));
      expect(AppColors.primaryLight, const Color(0xFF2DD4BF));
      expect(AppColors.primaryDark, const Color(0xFF0F766E));
    });

    test('Secondary colors are correct', () {
      expect(AppColors.secondary, const Color(0xFF475569));
      expect(AppColors.secondaryLight, const Color(0xFF64748B));
      expect(AppColors.secondaryDark, const Color(0xFF334155));
    });

    test('Accent colors are correct', () {
      expect(AppColors.accent, const Color(0xFFF59E0B));
      expect(AppColors.accentLight, const Color(0xFFFBBF24));
    });

    test('Background colors are correct', () {
      expect(AppColors.background, const Color(0xFFF8FAFC));
      expect(AppColors.surface, const Color(0xFFFFFFFF));
      expect(AppColors.surfaceVariant, const Color(0xFFF1F5F9));
    });

    test('Text colors are correct', () {
      expect(AppColors.textPrimary, const Color(0xFF0F172A));
      expect(AppColors.textSecondary, const Color(0xFF64748B));
      expect(AppColors.textTertiary, const Color(0xFF94A3B8));
    });

    test('Status colors are correct', () {
      expect(AppColors.success, const Color(0xFF10B981));
      expect(AppColors.warning, const Color(0xFFF59E0B));
      expect(AppColors.error, const Color(0xFFEF4444));
      expect(AppColors.info, const Color(0xFF3B82F6));
    });

    test('Category colors list contains 12 distinct colors', () {
      expect(AppColors.categoryColors.length, 12);
      expect(AppColors.categoryColors.toSet().length, 12); // All unique
    });

    test('Category colors start with Blue', () {
      expect(AppColors.categoryColors.first, const Color(0xFF3B82F6));
    });

    test('Dark mode colors are defined', () {
      expect(AppColors.backgroundDark, const Color(0xFF0F172A));
      expect(AppColors.surfaceDark, const Color(0xFF1E293B));
    });
  });
}
