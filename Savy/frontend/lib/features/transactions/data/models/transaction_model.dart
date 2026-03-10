class TransactionModel {
  final String id;
  final String userId;
  final double amount;
  final String description;
  final String? categoryId;
  final String? categoryName;
  final String? categoryIcon;
  final String? categoryColor;
  final String? bankAccountId;
  final String transactionType; // 'expense' or 'income'
  final DateTime transactionDate;
  final DateTime createdAt;
  final bool needsReview;

  TransactionModel({
    required this.id,
    required this.userId,
    required this.amount,
    required this.description,
    this.categoryId,
    this.categoryName,
    this.categoryIcon,
    this.categoryColor,
    this.bankAccountId,
    required this.transactionType,
    required this.transactionDate,
    required this.createdAt,
    this.needsReview = false,
  });

  factory TransactionModel.fromJson(Map<String, dynamic> json) {
    return TransactionModel(
      id: json['id'] as String,
      userId: json['user_id'] as String,
      amount: _parseDouble(json['amount']),
      description: json['description'] as String? ?? json['merchant'] as String? ?? 'N/A',
      categoryId: json['category_id'] as String?,
      categoryName: json['category_name'] as String? ?? json['category'] as String?,
      categoryIcon: json['category_icon'] as String?,
      categoryColor: json['category_color'] as String?,
      bankAccountId: json['bank_account_id'] as String?,
      transactionType: json['transaction_type'] as String? ?? 'expense',
      transactionDate: DateTime.parse(json['date'] as String? ?? json['transaction_date'] as String),
      createdAt: DateTime.parse(json['created_at'] as String),
      needsReview: json['needs_review'] as bool? ?? false,
    );
  }

  static double _parseDouble(dynamic value) {
    if (value is num) return value.toDouble();
    if (value is String) return double.tryParse(value) ?? 0.0;
    return 0.0;
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'user_id': userId,
      'amount': amount,
      'description': description,
      'category_id': categoryId,
      'bank_account_id': bankAccountId,
      'transaction_type': transactionType,
      'transaction_date': transactionDate.toIso8601String(),
    };
  }
}

