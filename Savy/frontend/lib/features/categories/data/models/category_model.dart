class CategoryModel {
  final String id;
  final String userId;
  final String name;
  final String icon;
  final String color;
  final double budgetMonthly;
  final DateTime createdAt;

  CategoryModel({
    required this.id,
    required this.userId,
    required this.name,
    required this.icon,
    required this.color,
    required this.budgetMonthly,
    required this.createdAt,
  });

  factory CategoryModel.fromJson(Map<String, dynamic> json) {
    return CategoryModel(
      id: json['id'] as String,
      userId: json['user_id'] as String,
      name: json['name'] as String,
      icon: json['icon'] as String,
      color: json['color'] as String,
      budgetMonthly: _parseDouble(json['budget_monthly']),
      createdAt: DateTime.parse(json['created_at'] as String),
    );
  }

  static double _parseDouble(dynamic value) {
    if (value is num) return value.toDouble();
    if (value is String) return double.tryParse(value) ?? 0.0;
    return 0.0;
  }

  Map<String, dynamic> toJson() {
    return {
      'name': name,
      'icon': icon,
      'color': color,
      'budget_monthly': budgetMonthly,
    };
  }
}



