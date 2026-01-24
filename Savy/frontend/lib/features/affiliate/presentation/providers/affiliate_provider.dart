import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:savy_frontend/features/affiliate/data/models/recommendation_model.dart';
import 'package:savy_frontend/features/affiliate/data/repositories/affiliate_repository.dart';

// Provider to fetch Dashboard Recommendations
final dashboardRecommendationProvider = FutureProvider<RecommendationResponse>((ref) async {
  final repository = ref.read(affiliateRepositoryProvider);
  return repository.getRecommendations(placement: "DASHBOARD");
});

// Controller for actions (Dismiss, Click)
final affiliateControllerProvider = Provider((ref) {
  return AffiliateController(ref.read(affiliateRepositoryProvider), ref);
});

class AffiliateController {
  final AffiliateRepository _repository;
  final Ref _ref;

  AffiliateController(this._repository, this._ref);

  Future<void> dismiss(String publicId) async {
    // 1. Optimistic Update: Remove from UI immediately?
    // For FutureProvider, we can force refresh or invalidate.
    // Ideally we maintain a local list of "hidden" IDs if we don't want to re-fetch.
    // For MVP, tracking interaction is enough, user probably won't see it again until refresh.
    
    await _repository.trackInteraction(
      publicId: publicId,
      event: "DISMISS",
      placement: "DASHBOARD"
    );
    
    // Refresh to update state (empty list if dismissed)
    // Or simpler: The UI card handles the hiding locally.
    // _ref.refresh(dashboardRecommendationProvider);
  }

  Future<void> logImpression(String publicId) async {
     await _repository.trackInteraction(
      publicId: publicId,
      event: "IMPRESSION",
      placement: "DASHBOARD"
    );
  }
}
