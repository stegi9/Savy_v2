/// Recurring bill entity (domain layer)
class Bill {
  final String id;
  final String userId;
  final String name;
  final double amount;
  final int dueDay;
  final String category;
  final String? provider;
  final bool isActive;
  final DateTime createdAt;

  const Bill({
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

  /// Get category display name
  String get categoryDisplayName {
    switch (category) {
      case 'energy':
        return 'Energia';
      case 'telco':
        return 'Telefonia/Internet';
      case 'rent':
        return 'Affitto';
      case 'insurance':
        return 'Assicurazione';
      case 'subscriptions':
        return 'Abbonamenti';
      case 'utilities':
        return 'Utenze';
      default:
        return 'Altro';
    }
  }

  /// Get category icon
  String get categoryIcon {
    switch (category) {
      case 'energy':
        return 'flash_on';
      case 'telco':
        return 'phone_android';
      case 'rent':
        return 'home';
      case 'insurance':
        return 'security';
      case 'subscriptions':
        return 'subscriptions';
      case 'utilities':
        return 'water_drop';
      default:
        return 'receipt';
    }
  }

  /// Get due date string
  String get dueDateString => '$dueDay del mese';
}

