import 'package:flutter_test/flutter_test.dart';
import 'package:savy_frontend/features/bills/data/models/bill_model.dart';

void main() {
  group('BillModel', () {
    test('fromJson should parse valid JSON correctly', () {
      // Arrange
      final json = {
        'id': 'bill-123',
        'user_id': 'user-123',
        'name': 'Netflix',
        'amount': 15.99,
        'due_day': 15,
        'category': 'Entertainment',
        'provider': 'Netflix Inc.',
        'is_active': true,
        'created_at': '2024-01-01T00:00:00',
      };

      // Act
      final model = BillModel.fromJson(json);

      // Assert
      expect(model.id, 'bill-123');
      expect(model.userId, 'user-123');
      expect(model.name, 'Netflix');
      expect(model.amount, 15.99);
      expect(model.dueDay, 15);
      expect(model.category, 'Entertainment');
      expect(model.provider, 'Netflix Inc.');
      expect(model.isActive, true);
    });

    test('fromJson should handle missing provider (nullable)', () {
      // Arrange
      final json = {
        'id': 'bill-123',
        'user_id': 'user-123',
        'name': 'Rent',
        'amount': 800.0,
        'due_day': 1,
        'category': 'Housing',
        'is_active': true,
        'created_at': '2024-01-01T00:00:00',
      };

      // Act
      final model = BillModel.fromJson(json);

      // Assert
      expect(model.provider, isNull);
    });

    test('fromJson should default is_active to true if missing', () {
      // Arrange
      final json = {
        'id': 'bill-123',
        'user_id': 'user-123',
        'name': 'Rent',
        'amount': 800.0,
        'due_day': 1,
        'category': 'Housing',
        'created_at': '2024-01-01T00:00:00',
      };

      // Act
      final model = BillModel.fromJson(json);

      // Assert
      expect(model.isActive, true);
    });

    test('toJson should convert model to map correctly', () {
      // Arrange
      final model = BillModel(
        id: 'bill-123',
        userId: 'user-123',
        name: 'Netflix',
        amount: 15.99,
        dueDay: 15,
        category: 'Entertainment',
        provider: 'Netflix Inc.',
        isActive: true,
        createdAt: DateTime(2024, 1, 1),
      );

      // Act
      final json = model.toJson();

      // Assert
      expect(json['name'], 'Netflix');
      expect(json['amount'], 15.99);
      expect(json['due_day'], 15);
      expect(json['provider'], 'Netflix Inc.');
      // toJson in BillModel doesn't include is_active based on previous file view
    });
  });
}
