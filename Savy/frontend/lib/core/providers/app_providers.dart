import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../services/api_client.dart';

// API Client Provider
final apiClientProvider = Provider<ApiClient>((ref) {
  return ApiClient(baseUrl: 'http://10.0.2.2:8000/api/v1');
});

// Dashboard Data Provider
final dashboardDataProvider = FutureProvider<Map<String, dynamic>>((ref) async {
  final apiClient = ref.watch(apiClientProvider);
  final profile = await apiClient.getCurrentUser();
  final settings = await apiClient.getUserSettings();
  final bills = await apiClient.getBills(activeOnly: true);
  final reportData = await apiClient.getSpendingReport(period: 'monthly');
  
  return {
    'profile': profile,
    'settings': settings,
    'bills': bills,
    'report': reportData,
  };
});

// Transactions Provider
final transactionsProvider = FutureProvider<List<dynamic>>((ref) async {
  final apiClient = ref.watch(apiClientProvider);
  return await apiClient.getTransactions();
});

// Categories Provider
final categoriesProvider = FutureProvider<List<dynamic>>((ref) async {
  final apiClient = ref.watch(apiClientProvider);
  return await apiClient.getCategories();
});

// Bills Provider
final billsProvider = FutureProvider<List<dynamic>>((ref) async {
  final apiClient = ref.watch(apiClientProvider);
  return await apiClient.getBills(activeOnly: true);
});

// User Settings Provider
final userSettingsProvider = FutureProvider<Map<String, dynamic>>((ref) async {
  final apiClient = ref.watch(apiClientProvider);
  return await apiClient.getUserSettings();
});

// Spending Report Provider
final spendingReportProvider = FutureProvider<Map<String, dynamic>>((ref) async {
  final apiClient = ref.watch(apiClientProvider);
  return await apiClient.getSpendingReport(period: 'monthly');
});

// Deep Dive Analytics Provider (with period parameter)
final deepDiveAnalyticsProvider = FutureProvider.family<Map<String, dynamic>, String>((ref, period) async {
  final apiClient = ref.watch(apiClientProvider);
  return await apiClient.getDeepDiveAnalytics(period: period);
});


