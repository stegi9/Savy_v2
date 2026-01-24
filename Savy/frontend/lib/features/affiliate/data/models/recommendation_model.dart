class RecommendationModel {
  final String publicId;
  final String title;
  final String? body;
  final String actionToken;
  final double score;
  final String? imageUrl;
  final String? badge;

  RecommendationModel({
    required this.publicId,
    required this.title,
    this.body,
    required this.actionToken,
    required this.score,
    this.imageUrl,
    this.badge,
  });

  factory RecommendationModel.fromJson(Map<String, dynamic> json) {
    return RecommendationModel(
      publicId: json['public_id'] as String,
      title: json['title'] as String,
      body: json['body'] as String?,
      actionToken: json['action_token'] as String,
      score: (json['score'] as num).toDouble(),
      imageUrl: json['image_url'] as String?,
      badge: json['badge'] as String?,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'public_id': publicId,
      'title': title,
      'body': body,
      'action_token': actionToken,
      'score': score,
      'image_url': imageUrl,
      'badge': badge,
    };
  }
}

class RecommendationResponse {
  final String placement;
  final String abVariant;
  final List<RecommendationModel> items;

  RecommendationResponse({
    required this.placement,
    required this.abVariant,
    required this.items,
  });

  factory RecommendationResponse.fromJson(Map<String, dynamic> json) {
    return RecommendationResponse(
      placement: json['placement'] as String,
      abVariant: json['ab_variant'] as String? ?? 'CONTROL',
      items: (json['items'] as List<dynamic>?)
              ?.map((e) => RecommendationModel.fromJson(e as Map<String, dynamic>))
              .toList() ??
          [],
    );
  }
}
