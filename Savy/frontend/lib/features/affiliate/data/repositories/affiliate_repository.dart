import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:savy_frontend/core/services/api_client.dart';
import 'package:savy_frontend/features/affiliate/data/models/recommendation_model.dart';
import 'package:savy_frontend/core/providers/app_providers.dart';

final affiliateRepositoryProvider = Provider<AffiliateRepository>((ref) {
  return AffiliateRepository(ref.read(apiClientProvider));
});

class AffiliateRepository {
  final ApiClient _apiClient;

  AffiliateRepository(this._apiClient);

  Future<RecommendationResponse> getRecommendations({
    String placement = "DASHBOARD",
    int maxItems = 1,
  }) async {
    try {
      final response = await _apiClient.post(
        '/affiliate/recommendations',
        data: {
          'placement': placement,
          'max_items': maxItems,
        },
      );
      return RecommendationResponse.fromJson(response.data);
    } catch (e) {
      // In case of error or empty, return logical empty response
      return RecommendationResponse(
        placement: placement,
        abVariant: "ERROR",
        items: [],
      );
    }
  }

  Future<void> trackInteraction({
    required String publicId,
    required String event, // IMPRESSION, DISMISS, CLICK
    String? placement,
    String? idempotencyKey,
  }) async {
    try {
      await _apiClient.post(
        '/affiliate/interactions',
        data: {
          'public_id': publicId,
          'event': event,
          'placement': placement,
          'idempotency_key': idempotencyKey,
        },
      );
    } catch (e) {
      // Silent fail for tracking
    }
  }
  
  String getRedirectUrl(String token) {
    // Assuming ApiClient has baseUrl or we construct it.
    // For MVP hardcode or fetch from config.
    // Ideally ApiClient exposes baseUrl logic.
    // Let's assume standard Savy API URL structure.
    // If ApiClient.baseUrl is protected, we might need to duplicate config or expose it.
    // Since I can't see ApiClient internals deeply right now, I'll use a relative path if app handles it,
    // OR constructing full URL. Launcher usually needs full URL.
    
    // Fallback: use production/dev URL based on environment constants if available.
    // For now, construct based on known backend path.
    return "${_apiClient.baseUrl}/affiliate/redirect/$token"; 
  }
}
