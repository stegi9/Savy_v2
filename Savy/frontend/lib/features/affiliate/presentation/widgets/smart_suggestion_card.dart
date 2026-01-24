import 'dart:async';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:url_launcher/url_launcher.dart';
import 'package:visibility_detector/visibility_detector.dart'; // Ensure strictly this package is in pubspec
import 'package:savy_frontend/core/theme/app_colors.dart'; // Assuming theme exists
import 'package:savy_frontend/features/affiliate/data/models/recommendation_model.dart';
import 'package:savy_frontend/features/affiliate/presentation/providers/affiliate_provider.dart';
import 'package:savy_frontend/features/affiliate/data/repositories/affiliate_repository.dart';

class SmartSuggestionCard extends ConsumerStatefulWidget {
  const SmartSuggestionCard({Key? key}) : super(key: key);

  @override
  ConsumerState<SmartSuggestionCard> createState() => _SmartSuggestionCardState();
}

class _SmartSuggestionCardState extends ConsumerState<SmartSuggestionCard> {
  Timer? _impressionTimer;
  bool _isVisible = false;
  bool _isHiddenLocally = false;
  
  @override
  void dispose() {
    _impressionTimer?.cancel();
    super.dispose();
  }

  void _onVisibilityChanged(VisibilityInfo info, String publicId) {
    if (info.visibleFraction > 0.5) {
      if (!_isVisible) {
        _isVisible = true;
        // Start Timer for 1.5s impression
        _impressionTimer = Timer(const Duration(milliseconds: 1500), () {
          if (mounted && _isVisible && !_isHiddenLocally) {
             ref.read(affiliateControllerProvider).logImpression(publicId);
          }
        });
      }
    } else {
      _isVisible = false;
      _impressionTimer?.cancel();
    }
  }

  void _hideCard(String publicId) {
    setState(() {
      _isHiddenLocally = true;
    });
    ref.read(affiliateControllerProvider).dismiss(publicId);
  }

  Future<void> _launchOffer(RecommendationModel offer) async {
    final repo = ref.read(affiliateRepositoryProvider);
    // Use repository to get full URL if needed, or assume actionToken is URL (it's a token)
    // The spec says: api.savy.app/affiliate/redirect/{token}
    // The model has 'actionToken'.
    
    final urlString = repo.getRedirectUrl(offer.actionToken);
    final url = Uri.parse(urlString);

    try {
      if (await canLaunchUrl(url)) {
        await launchUrl(url, mode: LaunchMode.externalApplication);
        // Tracking CLICK is handled by backend redirect usually, 
        // but we can enforce it here too? Spec says Backend logs click on redirect.
      } else {
        // Fallback?
      }
    } catch (e) {
      debugPrint("Could not launch $url");
    }
  }

  @override
  Widget build(BuildContext context) {
    final recommendationAsync = ref.watch(dashboardRecommendationProvider);

    if (_isHiddenLocally) return const SizedBox.shrink();

    return recommendationAsync.when(
      data: (response) {
        if (response.items.isEmpty) return const SizedBox.shrink();
        final offer = response.items.first;

        return VisibilityDetector(
          key: Key(offer.publicId),
          onVisibilityChanged: (info) => _onVisibilityChanged(info, offer.publicId),
          child: Container(
            margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
            decoration: BoxDecoration(
              color: Colors.white, // Or specialized card color
              borderRadius: BorderRadius.circular(16),
              boxShadow: [
                BoxShadow(
                  color: Colors.black.withOpacity(0.05),
                  blurRadius: 10,
                  offset: const Offset(0, 4),
                )
              ],
              border: Border.all(color: Colors.blueAccent.withOpacity(0.2)),
            ),
            child: Material(
              color: Colors.transparent,
              child: InkWell(
                borderRadius: BorderRadius.circular(16),
                onTap: () => _launchOffer(offer),
                child: Padding(
                  padding: const EdgeInsets.all(16.0),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        children: [
                          Icon(Icons.savings, color: Colors.blueAccent),
                          const SizedBox(width: 8),
                          Text(
                            "RISPARMIO SUGGERITO",
                            style: TextStyle(
                              fontSize: 12,
                              fontWeight: FontWeight.bold,
                              color: Colors.blueAccent,
                            ),
                          ),
                          const Spacer(),
                          IconButton(
                            icon: const Icon(Icons.close, size: 18, color: Colors.grey),
                            onPressed: () => _hideCard(offer.publicId),
                            padding: EdgeInsets.zero,
                            constraints: const BoxConstraints(),
                          )
                        ],
                      ),
                      const SizedBox(height: 8),
                      Text(
                        offer.title,
                        style: const TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.bold,
                          color: Colors.black87,
                        ),
                      ),
                      if (offer.body != null) ...[
                        const SizedBox(height: 4),
                        Text(
                          offer.body!,
                          style: const TextStyle(
                            fontSize: 14,
                            color: Colors.black54,
                          ),
                        ),
                      ],
                      const SizedBox(height: 12),
                      Row(
                        mainAxisAlignment: MainAxisAlignment.end,
                        children: [
                          Text(
                            "Guarda Offerta ->",
                            style: TextStyle(
                              fontWeight: FontWeight.bold,
                              color: Colors.blueAccent,
                            ),
                          )
                        ],
                      )
                    ],
                  ),
                ),
              ),
            ),
          ),
        );
      },
      loading: () => const SizedBox.shrink(), // Or Skeleton
      error: (_, __) => const SizedBox.shrink(),
    );
  }
}
