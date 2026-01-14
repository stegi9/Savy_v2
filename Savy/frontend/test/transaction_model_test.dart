import 'package:flutter_test/flutter_test.dart';
import 'package:savy_frontend/features/transactions/data/models/transaction_model.dart';

void main() {
  group('TransactionModel', () {
    test('fromJson should parse valid JSON correctly', () {
      // Arrange
      final json = {
        'id': '123e4567-e89b-12d3-a456-426614174000',
        'user_id': 'user-123',
        'amount': 50.0,
        'description': 'Test purchase',
        'category_id': 'cat-123',
        'category_name': 'Shopping',
        'transaction_type': 'expense',
        'date': '2024-01-01T10:00:00',
        'created_at': '2024-01-01T00:00:00',
        'needs_review': false,
      };

      // Act
      final model = TransactionModel.fromJson(json);

      // Assert
      expect(model.id, '123e4567-e89b-12d3-a456-426614174000');
      expect(model.userId, 'user-123');
      expect(model.amount, 50.0);
      expect(model.description, 'Test purchase');
      expect(model.categoryId, 'cat-123');
      expect(model.categoryName, 'Shopping');
      expect(model.transactionType, 'expense');
      expect(model.needsReview, false);
    });

    test('fromJson should map merchant to description if description is missing', () {
      // Arrange
      final json = {
        'id': '123e4567-e89b-12d3-a456-426614174000',
        'user_id': 'user-123',
        'amount': 50.0,
        'merchant': 'Test Store', // Merchant provided instead of description
        'transaction_type': 'expense',
        'date': '2024-01-01T10:00:00',
        'created_at': '2024-01-01T00:00:00',
      };

      // Act
      final model = TransactionModel.fromJson(json);

      // Assert
      expect(model.description, 'Test Store');
    });

    test('fromJson should handle null fields specifically', () {
      // Arrange
      final json = {
        'id': '123e4567-e89b-12d3-a456-426614174000',
        'user_id': 'user-123',
        'amount': 50.0,
        'date': '2024-01-01T10:00:00',
        'created_at': '2024-01-01T00:00:00',
      };

      // Act
      final model = TransactionModel.fromJson(json);

      // Assert
      expect(model.description, 'N/A'); // Default fallback
      expect(model.transactionType, 'expense'); // Default fallback
      expect(model.needsReview, false); // Default fallback
    });
  });
}

