
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../../core/providers/app_providers.dart';

final bankServiceProvider = Provider<BankService>((ref) {
  return BankService(ref);
});


class BankService {
  final Ref _ref;

  BankService(this._ref);


  Future<String> connectBank() async {
    try {
      final apiClient = _ref.read(apiClientProvider);
      // Salt Edge flow: Start Generic Connect Session -> Get URL -> Open in WebView
      return await apiClient.startBankLink();
    } catch (e) {
      throw Exception('Connection failed: $e');
    }
  }

  Future<void> syncData() async {
    try {
      final apiClient = _ref.read(apiClientProvider);
      await apiClient.syncBankData();
    } catch (e) {
      throw Exception('Data sync failed: $e');
    }
  }
}
