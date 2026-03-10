import 'package:flutter/material.dart';

/// SAVY Modern Color Palette - iOS/Revolut Inspired
/// Ultra-modern, sophisticated, premium feel
class AppColors {
  // ============================================================================
  // PRIMARY PALETTE - Deep Blue/Purple (Premium & Trustworthy)
  // ============================================================================
  static const Color primary = Color(0xFF0A84FF); // iOS Blue
  static const Color primaryLight = Color(0xFF64B5F6); // Lighter blue
  static const Color primaryDark = Color(0xFF0066CC); // Darker blue
  static const Color primaryAccent = Color(0xFF5E5CE6); // iOS Purple accent
  
  // ============================================================================
  // GRADIENT COLORS - For premium cards & backgrounds
  // ============================================================================
  static const Color gradientStart = Color(0xFF667EEA); // Purple
  static const Color gradientEnd = Color(0xFF764BA2); // Deep Purple
  
  static const Color gradientBlueStart = Color(0xFF0A84FF);
  static const Color gradientBlueEnd = Color(0xFF5E5CE6);
  
  static const Color gradientGreenStart = Color(0xFF34C759);
  static const Color gradientGreenEnd = Color(0xFF30D158);
  
  // ============================================================================
  // BACKGROUNDS - Elegant & Clean
  // ============================================================================
  static const Color background = Color(0xFFF5F5F7); // iOS light gray
  static const Color surface = Color(0xFFFFFFFF); // Pure white
  static const Color surfaceVariant = Color(0xFFF2F2F7); // iOS light surface
  static const Color surfaceElevated = Color(0xFFFEFEFE); // Slightly elevated
  
  // ============================================================================
  // TEXT COLORS - High contrast & readable
  // ============================================================================
  static const Color textPrimary = Color(0xFF000000); // True black
  static const Color textSecondary = Color(0xFF8E8E93); // iOS gray
  static const Color textTertiary = Color(0xFFC7C7CC); // Light gray
  static const Color textInverse = Color(0xFFFFFFFF); // White
  
  // ============================================================================
  // STATUS COLORS - iOS System Colors
  // ============================================================================
  static const Color success = Color(0xFF34C759); // iOS Green
  static const Color warning = Color(0xFFFF9500); // iOS Orange
  static const Color error = Color(0xFFFF3B30); // iOS Red
  static const Color info = Color(0xFF0A84FF); // iOS Blue
  
  // ============================================================================
  // ACCENT COLORS - Vibrant & Modern
  // ============================================================================
  static const Color accent = Color(0xFFFF2D55); // iOS Pink
  static const Color accentOrange = Color(0xFFFF9500); // iOS Orange
  static const Color accentPurple = Color(0xFF5E5CE6); // iOS Purple
  static const Color accentTeal = Color(0xFF5AC8FA); // iOS Teal
  static const Color accentIndigo = Color(0xFF5856D6); // iOS Indigo
  
  // ============================================================================
  // CATEGORY COLORS - Distinct & Beautiful (iOS Inspired)
  // ============================================================================
  static const List<Color> categoryColors = [
    Color(0xFF10B981), // Emerald Green
    Color(0xFF3B82F6), // Blue
    Color(0xFFF59E0B), // Amber
    Color(0xFFEF4444), // Red
    Color(0xFF8B5CF6), // Purple
    Color(0xFFEC4899), // Pink
    Color(0xFF06B6D4), // Cyan
    Color(0xFFF97316), // Orange
    Color(0xFF14B8A6), // Teal
    Color(0xFF84CC16), // Lime
    Color(0xFFA855F7), // Violet
    Color(0xFFF43F5E), // Rose
    Color(0xFF0EA5E9), // Sky Blue
    Color(0xFF22C55E), // Green
    Color(0xFFFBBF24), // Yellow
    Color(0xFF6366F1), // Indigo
  ];
  
  // ============================================================================
  // GLASSMORPHISM COLORS
  // ============================================================================
  static const Color glassWhite = Color(0xCCFFFFFF); // 80% white
  static const Color glassDark = Color(0x66000000); // 40% black
  static const Color glassBlur = Color(0x33FFFFFF); // 20% white
  
  // ============================================================================
  // SHADOWS & ELEVATION
  // ============================================================================
  static const Color shadowLight = Color(0x1A000000); // 10% black
  static const Color shadowMedium = Color(0x33000000); // 20% black
  static const Color shadowHeavy = Color(0x4D000000); // 30% black
  
  // ============================================================================
  // DARK MODE PALETTE
  // ============================================================================
  static const Color backgroundDark = Color(0xFF000000); // Pure black (iOS)
  static const Color surfaceDark = Color(0xFF1C1C1E); // iOS dark surface
  static const Color surfaceVariantDark = Color(0xFF2C2C2E); // iOS elevated dark
  static const Color textPrimaryDark = Color(0xFFFFFFFF); // White
  static const Color textSecondaryDark = Color(0xFF8E8E93); // iOS gray (same)
  
  // ============================================================================
  // SPECIAL EFFECTS
  // ============================================================================
  static const Color shimmerBase = Color(0xFFE0E0E0);
  static const Color shimmerHighlight = Color(0xFFF5F5F5);
  static const Color shimmerBaseDark = Color(0xFF2C2C2E);
  static const Color shimmerHighlightDark = Color(0xFF3A3A3C);
}
