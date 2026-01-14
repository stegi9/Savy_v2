class BillModel {
  final String id;
  final String userId;
  final String name;
  final double amount;
  final int dueDay;
  final String category;
  final String? provider;
  final bool isActive;
  final DateTime createdAt;

  BillModel({
    required this.id,
    required this.userId,
    required this.name,
    required this.amount,
    required this.dueDay,
    required this.category,
    this.provider,
    required this.isActive,
    required this.createdAt,
  });

  factory BillModel.fromJson(Map<String, dynamic> json) {
    return BillModel(
      id: json['id'] as String,
      userId: json['user_id'] as String,
      name: json['name'] as String,
      amount: _parseDouble(json['amount']),
      dueDay: json['due_day'] as int,
      category: json['category'] as String,
      provider: json['provider'] as String?,
      isActive: json['is_active'] as bool? ?? true,
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
      'amount': amount,
      'due_day': dueDay,
      'category': category,
      'provider': provider,
    };
  }
}



