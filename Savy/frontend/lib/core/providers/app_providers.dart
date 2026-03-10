import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../services/api_client.dart';
import '../services/storage_helper.dart';
import 'auth_provider.dart';

// API Client Provider
final apiClientProvider = Provider<ApiClient>((ref) {
  return ApiClient(baseUrl: 'http://10.0.2.2:8000/api/v1');
});

// Helper to check if user is authenticated before making API calls
Future<bool> _isAuthenticated() async {
  final storage = StorageHelper.instance;
  final token = await storage.read(key: 'access_token');
  return token != null && token.isNotEmpty;
}

// Global Filter for Selected Account
final selectedAccountIdProvider = StateProvider<String?>((ref) => null);

// Dashboard Data Provider
final dashboardDataProvider = FutureProvider<Map<String, dynamic>>((ref) async {
  // Check authentication first
  if (!await _isAuthenticated()) {
    throw Exception('Not authenticated');
  }
  
  final apiClient = ref.watch(apiClientProvider);
  final profile = await apiClient.getCurrentUser();
  final settings = await apiClient.getUserSettings();
  final bills = await apiClient.getBills(activeOnly: true);
  
  return {
    'profile': profile,
    'settings': settings,
    'bills': bills,
  };
});

final transactionsProvider = FutureProvider<List<dynamic>>((ref) async {
  if (!await _isAuthenticated()) {
    return [];
  }
  final apiClient = ref.watch(apiClientProvider);
  final accountId = ref.watch(selectedAccountIdProvider);
  return await apiClient.getTransactions(bankAccountId: accountId);
});

// Categories Provider
final categoriesProvider = FutureProvider<List<dynamic>>((ref) async {
  if (!await _isAuthenticated()) {
    return [];
  }
  final apiClient = ref.watch(apiClientProvider);
  return await apiClient.getCategories();
});

// Bills Provider
final billsProvider = FutureProvider<List<dynamic>>((ref) async {
  if (!await _isAuthenticated()) {
    return [];
  }
  final apiClient = ref.watch(apiClientProvider);
  return await apiClient.getBills(activeOnly: true);
});

// User Settings Provider
final userSettingsProvider = FutureProvider<Map<String, dynamic>>((ref) async {
  if (!await _isAuthenticated()) {
    return {};
  }
  final apiClient = ref.watch(apiClientProvider);
  return await apiClient.getUserSettings();
});

final spendingReportProvider = FutureProvider<Map<String, dynamic>>((ref) async {
  if (!await _isAuthenticated()) {
    return {};
  }
  final apiClient = ref.watch(apiClientProvider);
  final accountId = ref.watch(selectedAccountIdProvider);
  return await apiClient.getSpendingReport(period: 'monthly', bankAccountId: accountId);
});

final deepDiveAnalyticsProvider = FutureProvider.family<Map<String, dynamic>, String>((ref, period) async {
  if (!await _isAuthenticated()) {
    return {};
  }
  final apiClient = ref.watch(apiClientProvider);
  final accountId = ref.watch(selectedAccountIdProvider);
  return await apiClient.getDeepDiveAnalytics(period: period, bankAccountId: accountId);
});


