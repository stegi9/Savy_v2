import 'package:flutter_test/flutter_test.dart';
import 'package:savy_frontend/features/categories/data/models/category_model.dart';

void main() {
  group('CategoryModel', () {
    test('fromJson should parse valid JSON correctly', () {
      // Arrange
      final json = {
        'id': 'cat-123',
        'user_id': 'user-123',
        'name': 'Groceries',
        'icon': 'shopping_cart',
        'color': '#FF5733',
        'budget_monthly': 500.0,
        'created_at': '2024-01-01T00:00:00',
      };

      // Act
      final model = CategoryModel.fromJson(json);

      // Assert
      expect(model.id, 'cat-123');
      expect(model.userId, 'user-123');
      expect(model.name, 'Groceries');
      expect(model.icon, 'shopping_cart');
      expect(model.color, '#FF5733');
      expect(model.budgetMonthly, 500.0);
      expect(model.createdAt, DateTime(2024, 1, 1));
    });

    test('fromJson should handle integer budget as double', () {
      // Arrange
      final json = {
        'id': 'cat-123',
        'user_id': 'user-123',
        'name': 'Groceries',
        'icon': 'shopping_cart',
        'color': '#FF5733',
        'budget_monthly': 500, // Integer
        'created_at': '2024-01-01T00:00:00',
      };

      // Act
      final model = CategoryModel.fromJson(json);

      // Assert
      expect(model.budgetMonthly, 500.0);
    });

    test('fromJson should handle string budget as double', () {
      // Arrange
      final json = {
        'id': 'cat-123',
        'user_id': 'user-123',
        'name': 'Groceries',
        'icon': 'shopping_cart',
        'color': '#FF5733',
        'budget_monthly': '500.50', // String
        'created_at': '2024-01-01T00:00:00',
      };

      // Act
      final model = CategoryModel.fromJson(json);

      // Assert
      expect(model.budgetMonthly, 500.50);
    });

    test('toJson should convert model to map correctly', () {
      // Arrange
      final model = CategoryModel(
        id: 'cat-123',
        userId: 'user-123',
        name: 'Groceries',
        icon: 'shopping_cart',
        color: '#FF5733',
        budgetMonthly: 500.0,
        createdAt: DateTime(2024, 1, 1),
      );

      // Act
      final json = model.toJson();

      // Assert
      expect(json['name'], 'Groceries');
      expect(json['icon'], 'shopping_cart');
      expect(json['color'], '#FF5733');
      expect(json['budget_monthly'], 500.0);
      // id and user_id are typically not in toJson for update/create payloads
      expect(json.containsKey('id'), false); 
    });
  });
}
