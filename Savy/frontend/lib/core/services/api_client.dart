import 'package:dio/dio.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:logger/logger.dart';

import 'package:savy_frontend/core/services/storage_helper.dart';

/// Centralized API client for all backend communication
class ApiClient {
  final Dio _dio;
  final FlutterSecureStorage _storage;
  final Logger _logger = Logger(
    printer: PrettyPrinter(
      methodCount: 0,
      errorMethodCount: 5,
      lineLength: 50,
      colors: true,
      printEmojis: true,
    ),
  );

  ApiClient({
    required String baseUrl,
    FlutterSecureStorage? storage,
  })  : _storage = storage ?? StorageHelper.instance,
        _dio = Dio(BaseOptions(
          baseUrl: baseUrl,
          connectTimeout: const Duration(seconds: 30),
          receiveTimeout: const Duration(seconds: 60),
          headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
          },
        )) {
    _setupInterceptors();
  }

  String get baseUrl => _dio.options.baseUrl;

  Future<Response> get(String path, {Map<String, dynamic>? queryParameters}) async {
    return _dio.get(path, queryParameters: queryParameters);
  }

  Future<Response> post(String path, {Object? data, Map<String, dynamic>? queryParameters}) async {
    return _dio.post(path, data: data, queryParameters: queryParameters);
  }

  Future<Response> put(String path, {Object? data, Map<String, dynamic>? queryParameters}) async {
    return _dio.put(path, data: data, queryParameters: queryParameters);
  }

  Future<Response> delete(String path, {Object? data, Map<String, dynamic>? queryParameters}) async {
    return _dio.delete(path, data: data, queryParameters: queryParameters);
  }

  void _setupInterceptors() {
    _dio.interceptors.add(InterceptorsWrapper(
      onRequest: (options, handler) async {
        // Inject JWT token
        final token = await _storage.read(key: 'access_token');
        
        if (token != null && token.isNotEmpty) {
          options.headers['Authorization'] = 'Bearer $token';
          _logger.d('Token injected into request headers');
        } else {
          _logger.w('No auth token found in storage');
        }
        
        _logger.d('Request: ${options.method} ${options.uri}');
        return handler.next(options);
      },
      onResponse: (response, handler) {
        _logger.d('Response: ${response.statusCode} from ${response.requestOptions.uri}');
        return handler.next(response);
      },
      onError: (error, handler) async {
        _logger.e(
          'Request failed: ${error.message}',
          error: error.error,
          stackTrace: error.stackTrace,
        );

        // Handle 401 (token expired)
        if (error.response?.statusCode == 401) {
          final isRefreshRequest = error.requestOptions.path.contains('/auth/refresh');
          
          if (!isRefreshRequest) {
            final refreshToken = await _storage.read(key: 'refresh_token');
            if (refreshToken != null && refreshToken.isNotEmpty) {
              try {
                _logger.i('Attempting to refresh token...');
                
                final refreshDio = Dio(BaseOptions(baseUrl: _dio.options.baseUrl));
                final refreshResponse = await refreshDio.post(
                  '/auth/refresh',
                  data: {'refresh_token': refreshToken},
                );
                
                if (refreshResponse.statusCode == 200) {
                  final newAccessToken = refreshResponse.data['access_token'];
                  final newRefreshToken = refreshResponse.data['refresh_token'] ?? refreshToken;
                  
                  await _storage.write(key: 'access_token', value: newAccessToken);
                  await _storage.write(key: 'refresh_token', value: newRefreshToken);
                  
                  _logger.i('Token refreshed successfully. Retrying request.');
                  
                  // Retry original request
                  final opts = error.requestOptions;
                  opts.headers['Authorization'] = 'Bearer $newAccessToken';
                  
                  final retryResponse = await _dio.fetch(opts);
                  return handler.resolve(retryResponse);
                }
              } catch (e) {
                _logger.w('Failed to refresh token: $e');
              }
            }
          }

          _logger.w('Unauthorized - clearing tokens');
          await _storage.delete(key: 'access_token');
          await _storage.delete(key: 'refresh_token');
          // Navigation to login should be handled by the UI layer
        }

        return handler.next(error);
      },
    ));
  }

  // ============================================================================
  // AUTHENTICATION
  // ============================================================================

  Future<Map<String, dynamic>> login(String email, String password) async {
    final response = await _dio.post('/auth/login', data: {
      'email': email,
      'password': password,
    });
    return response.data;
  }

  Future<Map<String, dynamic>> register(
      String email, String password, String fullName) async {
    final response = await _dio.post('/auth/register', data: {
      'email': email,
      'password': password,
      'full_name': fullName,
    });
    return response.data;
  }

  Future<Map<String, dynamic>> getCurrentUser() async {
    final response = await _dio.get('/auth/me');
    return response.data;
  }

  // ============================================================================
  // USER SETTINGS
  // ============================================================================

  Future<Map<String, dynamic>> getUserSettings() async {
    final response = await _dio.get('/users/settings');
    return response.data;
  }

  Future<Map<String, dynamic>> updateUserSettings(
      Map<String, dynamic> settings) async {
    final response = await _dio.patch('/users/settings', data: settings);
    return response.data;
  }

  // ============================================================================
  // CATEGORIES
  // ============================================================================

  Future<List<dynamic>> getCategories() async {
    final response = await _dio.get('/categories');
    return response.data;
  }

  Future<Map<String, dynamic>> createCategory({
    required String name,
    required String icon,
    String? color,
    String categoryType = 'expense',
    double budgetMonthly = 0.0,
  }) async {
    final response = await _dio.post('/categories', data: {
      'name': name,
      'icon': icon,
      'color': color,
      'category_type': categoryType,
      'budget_monthly': budgetMonthly,
    });
    return response.data;
  }

  Future<void> deleteCategory(String categoryId) async {
    await _dio.delete('/categories/$categoryId');
  }

  Future<Map<String, dynamic>> updateCategory(
      String categoryId, Map<String, dynamic> data) async {
    final response = await _dio.put('/categories/$categoryId', data: data);
    return response.data;
  }

  // ============================================================================
  // TRANSACTIONS
  // ============================================================================

  Future<List<dynamic>> getTransactions({String? categoryId, String? bankAccountId}) async {
    final response = await _dio.get('/transactions', queryParameters: {
      if (categoryId != null) 'category_id': categoryId,
      if (bankAccountId != null) 'bank_account_id': bankAccountId,
    });
    // Backend returns {success: true, data: {transactions: [...], count: N}}
    final data = response.data['data'];
    return data['transactions'] as List;
  }

  Future<Map<String, dynamic>> createTransaction({
    required double amount,
    required String description,
    String? categoryId,
    String transactionType = 'expense',
    DateTime? transactionDate,
    String? bankAccountId,
  }) async {
    final date = transactionDate ?? DateTime.now();
    final response = await _dio.post('/transactions/', data: {
      'merchant': description, // Backend expects 'merchant', not 'description'
      'amount': amount,
      'transaction_type': transactionType,
      'date': '${date.year}-${date.month.toString().padLeft(2, '0')}-${date.day.toString().padLeft(2, '0')}', // YYYY-MM-DD format
      'bank_account_id': bankAccountId,
      'auto_categorize': true,
    });
    return response.data;
  }

  Future<void> deleteTransaction(String transactionId) async {
    await _dio.delete('/transactions/$transactionId');
  }

  Future<Map<String, dynamic>> updateTransactionCategory(
      String transactionId, String categoryId) async {
    final response = await _dio.patch('/transactions/$transactionId/category',
        data: {'category_id': categoryId});
    return response.data;
  }

  // ============================================================================
  // BILLS
  // ============================================================================

  Future<List<dynamic>> getBills({bool activeOnly = true}) async {
    final response = await _dio.get('/bills', queryParameters: {
      'active_only': activeOnly,
    });
    return response.data;
  }

  Future<Map<String, dynamic>> createBill({
    required String name,
    required double amount,
    required int dueDay,
    required String category,
    String? provider,
  }) async {
    final response = await _dio.post('/bills', data: {
      'name': name,
      'amount': amount,
      'due_day': dueDay,
      'category': category,
      'provider': provider,
    });
    return response.data;
  }

  Future<Map<String, dynamic>> updateBill(
      String billId, Map<String, dynamic> data) async {
    final response = await _dio.put('/bills/$billId', data: data);
    return response.data;
  }

  Future<void> deleteBill(String billId) async {
    await _dio.delete('/bills/$billId');
  }

  // ============================================================================
  // REPORTS
  // ============================================================================

  Future<Map<String, dynamic>> getSpendingReport({String period = 'monthly', String? bankAccountId}) async {
    final response = await _dio.post('/reports/spending', data: {
      'period': period,
      if (bankAccountId != null) 'bank_account_id': bankAccountId,
    });
    return response.data;
  }

  // ============================================================================
  // ANALYTICS (DEEP DIVE)
  // ============================================================================

  Future<Map<String, dynamic>> getDeepDiveAnalytics({String period = 'monthly', String? bankAccountId}) async {
    final response = await _dio.post('/analytics/deep-dive', data: {
      'period': period,
      if (bankAccountId != null) 'bank_account_id': bankAccountId,
    });
    return response.data;
  }

  // ============================================================================
  // CHAT (AI COACH)
  // ============================================================================

  Future<Map<String, dynamic>> sendChatMessage(String message) async {
    final response = await _dio.post('/chat', data: {
      'message': message,
    });
    return response.data;
  }

  // ============================================================================
  // OPTIMIZATION
  // ============================================================================

  Future<List<dynamic>> scanOptimizations() async {
    final response = await _dio.post('/optimization/scan');
    return response.data;
  }

  Future<Map<String, dynamic>> getOptimizationLeads() async {
    final response = await _dio.get('/optimization/leads');
    return response.data;
  }

  // ============================================================================
  // BANK INTEGRATION
  // ============================================================================


  Future<String> startBankLink() async {
    final response = await _dio.post('/banks/link/start');
    
    if (response.data['success'] == true) {
        return response.data['data']['link'];
    }
    throw Exception('Failed to initiate connection: ${response.data['message']}');
  }

  Future<Map<String, dynamic>> syncBankData() async {
    final response = await _dio.post('/banks/sync');
     if (response.data['success'] == true) {
        return response.data['data'] ?? {};
    }
    throw Exception('Failed to sync bank data: ${response.data['message']}');
  }
}

