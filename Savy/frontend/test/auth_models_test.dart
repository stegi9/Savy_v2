import 'package:flutter_test/flutter_test.dart';
import 'package:savy_frontend/features/auth/data/models/user_profile_model.dart';
// import 'package:savy_frontend/features/auth/domain/entities/auth.dart'; // Entity not implemented yet

void main() {
  // AuthTokenModel test removed as the file was not found in listing (auth_models.dart not found)
  // Focusing on UserProfileModel which exists

  group('UserProfileModel', () {
    test('fromJson should parse valid JSON correctly', () {
      // Arrange
      final json = {
        'id': '123e4567-e89b-12d3-a456-426614174000',
        'email': 'test@example.com',
        'full_name': 'Test User',
        'current_balance': 1500.50,
        'currency': 'EUR',
        'created_at': '2024-01-01T00:00:00',
        'updated_at': '2024-01-02T00:00:00',
      };

      // Act
      final model = UserProfileModel.fromJson(json);

      // Assert
      expect(model.id, '123e4567-e89b-12d3-a456-426614174000');
      expect(model.email, 'test@example.com');
      expect(model.fullName, 'Test User');
      expect(model.currentBalance, 1500.50);
      expect(model.currency, 'EUR');
    });

    test('fromJson should use default currency if missing', () {
      // Arrange
      final json = {
        'id': '123e4567-e89b-12d3-a456-426614174000',
        'email': 'test@example.com',
        'full_name': 'Test User',
        'current_balance': 1500.50,
        'created_at': '2024-01-01T00:00:00',
        'updated_at': '2024-01-02T00:00:00',
      };

      // Act
      final model = UserProfileModel.fromJson(json);

      // Assert
      expect(model.currency, 'EUR');
    });
  });
}

