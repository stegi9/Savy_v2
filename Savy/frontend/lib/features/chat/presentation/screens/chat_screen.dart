import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../../core/services/api_client.dart';
import '../../../../core/l10n/app_strings.dart';

// Provider for ApiClient
final apiClientProvider = Provider<ApiClient>((ref) {
  return ApiClient(baseUrl: 'http://10.0.2.2:8000/api/v1');
});

// Provider for chat messages
final chatMessagesProvider = StateProvider<List<ChatMessage>>((ref) => []);

// Provider for loading state
final chatLoadingProvider = StateProvider<bool>((ref) => false);

class ChatMessage {
  final String content;
  final bool isUser;
  final String? decision; // affordable, caution, not_affordable
  final DateTime timestamp;

  ChatMessage({
    required this.content,
    required this.isUser,
    this.decision,
    DateTime? timestamp,
  }) : timestamp = timestamp ?? DateTime.now();
}

class ChatScreen extends ConsumerStatefulWidget {
  const ChatScreen({super.key});

  @override
  ConsumerState<ChatScreen> createState() => _ChatScreenState();
}

class _ChatScreenState extends ConsumerState<ChatScreen> {
  final TextEditingController _messageController = TextEditingController();
  final ScrollController _scrollController = ScrollController();

  @override
  void dispose() {
    _messageController.dispose();
    _scrollController.dispose();
    super.dispose();
  }

  void _scrollToBottom() {
    if (_scrollController.hasClients) {
      Future.delayed(const Duration(milliseconds: 100), () {
        _scrollController.animateTo(
          _scrollController.position.maxScrollExtent,
          duration: const Duration(milliseconds: 300),
          curve: Curves.easeOut,
        );
      });
    }
  }

  Future<void> _sendMessage() async {
    final message = _messageController.text.trim();
    if (message.isEmpty) return;

    // Add user message
    ref.read(chatMessagesProvider.notifier).update((state) => [
          ...state,
          ChatMessage(content: message, isUser: true),
        ]);

    _messageController.clear();
    _scrollToBottom();

    // Set loading
    ref.read(chatLoadingProvider.notifier).state = true;

    try {
      final apiClient = ref.read(apiClientProvider);
      final response = await apiClient.sendChatMessage(message);

      // Add AI response
      ref.read(chatMessagesProvider.notifier).update((state) => [
            ...state,
            ChatMessage(
              content: response['reasoning'] ?? 'Nessuna risposta disponibile',
              isUser: false,
              decision: response['decision'],
            ),
          ]);

      _scrollToBottom();
    } catch (e) {
      // Add error message
      ref.read(chatMessagesProvider.notifier).update((state) => [
            ...state,
            ChatMessage(
              content: 'Errore: ${e.toString()}',
              isUser: false,
            ),
          ]);
    } finally {
      ref.read(chatLoadingProvider.notifier).state = false;
    }
  }

  @override
  Widget build(BuildContext context) {
    final messages = ref.watch(chatMessagesProvider);
    final isLoading = ref.watch(chatLoadingProvider);
    final theme = Theme.of(context);

    return Scaffold(
      backgroundColor: theme.scaffoldBackgroundColor,
      appBar: AppBar(
        title: Text(AppStrings.get('coachTitle')),
        centerTitle: true,
        backgroundColor: Colors.transparent,
        elevation: 0,
        flexibleSpace: Container(
          decoration: BoxDecoration(
            gradient: LinearGradient(
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
              colors: [
                theme.colorScheme.primary,
                theme.colorScheme.primary.withOpacity(0.8),
              ],
            ),
          ),
        ),
      ),
      body: Column(
        children: [
          // Suggestions (if no messages)
          if (messages.isEmpty) _buildSuggestions(context),

          // Messages list
          Expanded(
            child: messages.isEmpty
                ? _buildEmptyState(context)
                : ListView.builder(
                    controller: _scrollController,
                    padding: const EdgeInsets.all(16),
                    itemCount: messages.length,
                    itemBuilder: (context, index) {
                      return _MessageBubble(message: messages[index]);
                    },
                  ),
          ),

          // Loading indicator
          if (isLoading)
            Padding(
              padding: const EdgeInsets.all(8.0),
              child: Row(
                children: [
                  const SizedBox(width: 16),
                  CircleAvatar(
                    backgroundColor: theme.colorScheme.primary.withOpacity(0.1),
                    child: Icon(Icons.psychology, color: theme.colorScheme.primary),
                  ),
                  const SizedBox(width: 12),
                  Text(
                    AppStrings.get('coachThinking'),
                    style: TextStyle(
                      color: theme.colorScheme.onSurface.withOpacity(0.7),
                      fontStyle: FontStyle.italic,
                    ),
                  ),
                  const SizedBox(width: 8),
                  SizedBox(
                    width: 16,
                    height: 16,
                    child: CircularProgressIndicator(
                      strokeWidth: 2,
                      color: theme.colorScheme.primary,
                    ),
                  ),
                ],
              ),
            ),

          // Input area
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: theme.cardColor,
              boxShadow: [
                BoxShadow(
                  color: Colors.black.withOpacity(0.05),
                  blurRadius: 10,
                  offset: const Offset(0, -2),
                ),
              ],
            ),
            child: SafeArea(
              child: Row(
                children: [
                  Expanded(
                    child: TextField(
                      controller: _messageController,
                      style: TextStyle(color: theme.colorScheme.onSurface),
                      decoration: InputDecoration(
                        hintText: AppStrings.get('coachInputHint'),
                        hintStyle: TextStyle(color: theme.colorScheme.onSurface.withOpacity(0.6)),
                        filled: true,
                        fillColor: theme.scaffoldBackgroundColor,
                        border: OutlineInputBorder(
                          borderRadius: BorderRadius.circular(24),
                          borderSide: BorderSide.none,
                        ),
                        contentPadding: const EdgeInsets.symmetric(
                          horizontal: 20,
                          vertical: 12,
                        ),
                      ),
                      maxLines: null,
                      textCapitalization: TextCapitalization.sentences,
                      onSubmitted: (_) => _sendMessage(),
                    ),
                  ),
                  const SizedBox(width: 12),
                  Container(
                    decoration: BoxDecoration(
                      gradient: LinearGradient(
                        colors: [theme.colorScheme.primary, theme.colorScheme.primary.withOpacity(0.8)],
                      ),
                      shape: BoxShape.circle,
                    ),
                    child: IconButton(
                      icon: const Icon(Icons.send_rounded, color: Colors.white),
                      onPressed: _sendMessage,
                    ),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildEmptyState(BuildContext context) {
    final theme = Theme.of(context);
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Container(
            padding: const EdgeInsets.all(24),
            decoration: BoxDecoration(
              color: theme.colorScheme.primary.withOpacity(0.1),
              shape: BoxShape.circle,
            ),
            child: Icon(
              Icons.psychology_rounded,
              size: 64,
              color: theme.colorScheme.primary,
            ),
          ),
          const SizedBox(height: 24),
          Text(
            AppStrings.get('coachEmptyTitle'),
            style: TextStyle(
              fontSize: 24,
              fontWeight: FontWeight.bold,
              color: theme.colorScheme.onSurface,
            ),
          ),
          const SizedBox(height: 12),
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 48),
            child: Text(
              AppStrings.get('coachEmptySubtitle'),
              textAlign: TextAlign.center,
              style: TextStyle(
                fontSize: 14,
                color: theme.colorScheme.onSurface.withOpacity(0.7),
              ),
            ),
          ),
        ],
      ),
    );
  }

  // NOTE: Suggestions are not localized in key names for simplicity in this example, 
  // but they are fetched via AppStrings
  Widget _buildSuggestions(BuildContext context) {
    final theme = Theme.of(context);
    final suggestions = {
      'coachSuggest1': AppStrings.get('coachSuggest1'),
      'coachSuggest2': AppStrings.get('coachSuggest2'),
      'coachSuggest3': AppStrings.get('coachSuggest3'),
      'coachSuggest4': AppStrings.get('coachSuggest4'),
    };

    return Container(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Prova a chiedere:',
            style: TextStyle(
              fontSize: 12,
              fontWeight: FontWeight.w600,
              color: theme.colorScheme.onSurface.withOpacity(0.7),
            ),
          ),
          const SizedBox(height: 12),
          Wrap(
            spacing: 8,
            runSpacing: 8,
            children: suggestions.values.map((suggestion) {
              return GestureDetector(
                onTap: () {
                  // Only put the text content in the box, removing emoji if needed or keeping it
                  // Here we just use exact text from localization
                  _messageController.text = suggestion; 
                },
                child: Container(
                  padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
                  decoration: BoxDecoration(
                    color: theme.cardColor,
                    borderRadius: BorderRadius.circular(20),
                    border: Border.all(
                      color: theme.colorScheme.primary.withOpacity(0.2),
                    ),
                  ),
                  child: Text(
                    suggestion,
                    style: TextStyle(
                      fontSize: 13,
                      color: theme.colorScheme.onSurface,
                    ),
                  ),
                ),
              );
            }).toList(),
          ),
        ],
      ),
    );
  }
}

class _MessageBubble extends StatelessWidget {
  final ChatMessage message;

  const _MessageBubble({required this.message});

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Padding(
      padding: const EdgeInsets.only(bottom: 12),
      child: Row(
        mainAxisAlignment:
            message.isUser ? MainAxisAlignment.end : MainAxisAlignment.start,
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          if (!message.isUser) ...[
            CircleAvatar(
              backgroundColor: theme.colorScheme.primary.withOpacity(0.1),
              child: Icon(Icons.psychology, color: theme.colorScheme.primary, size: 20),
            ),
            const SizedBox(width: 12),
          ],
          Flexible(
            child: Column(
              crossAxisAlignment: message.isUser
                  ? CrossAxisAlignment.end
                  : CrossAxisAlignment.start,
              children: [
                Container(
                  padding: const EdgeInsets.all(16),
                  decoration: BoxDecoration(
                    color: message.isUser
                        ? theme.colorScheme.primary
                        : theme.cardColor,
                    borderRadius: BorderRadius.circular(16).copyWith(
                      topLeft: message.isUser ? null : const Radius.circular(4),
                      topRight: message.isUser ? const Radius.circular(4) : null,
                    ),
                  ),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      if (message.decision != null) ...[
                        _DecisionBadge(decision: message.decision!),
                        const SizedBox(height: 8),
                      ],
                      Text(
                        message.content,
                        style: TextStyle(
                          color: message.isUser
                              ? theme.colorScheme.onPrimary
                              : theme.colorScheme.onSurface,
                          fontSize: 15,
                          height: 1.4,
                        ),
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  _formatTime(message.timestamp),
                  style: TextStyle(
                    fontSize: 11,
                    color: theme.colorScheme.onSurface.withOpacity(0.6),
                  ),
                ),
              ],
            ),
          ),
          if (message.isUser) ...[
            const SizedBox(width: 12),
            CircleAvatar(
              backgroundColor: theme.colorScheme.secondary.withOpacity(0.2),
              child: Icon(Icons.person, color: theme.colorScheme.secondary, size: 20),
            ),
          ],
        ],
      ),
    );
  }

  String _formatTime(DateTime time) {
    final now = DateTime.now();
    final diff = now.difference(time);

    if (diff.inMinutes < 1) return AppStrings.get('timeNow');
    if (diff.inHours < 1) return '${diff.inMinutes}m fa'; // Could be localized better but ok for now
    if (diff.inDays < 1) return '${diff.inHours}h fa';
    return '${time.day}/${time.month} ${time.hour}:${time.minute.toString().padLeft(2, '0')}';
  }
}

class _DecisionBadge extends StatelessWidget {
  final String decision;

  const _DecisionBadge({required this.decision});

  @override
  Widget build(BuildContext context) {
    Color color;
    IconData icon;
    String labelKey;

    switch (decision.toLowerCase()) {
      case 'affordable':
        color = Colors.green; // Semantic colors usually hardcoded or from theme extension
        icon = Icons.check_circle;
        labelKey = 'decisionAffordable';
        break;
      case 'caution':
        color = Colors.orange;
        icon = Icons.warning_amber_rounded;
        labelKey = 'decisionCaution';
        break;
      case 'not_affordable':
        color = Colors.red;
        icon = Icons.cancel;
        labelKey = 'decisionNotAffordable';
        break;
      default:
        color = Colors.grey;
        icon = Icons.help_outline;
        labelKey = 'decisionAnalysis';
    }

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
      decoration: BoxDecoration(
        color: color.withOpacity(0.15),
        borderRadius: BorderRadius.circular(12),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, size: 16, color: color),
          const SizedBox(width: 6),
          Text(
            AppStrings.get(labelKey),
            style: TextStyle(
              color: color,
              fontSize: 12,
              fontWeight: FontWeight.w600,
            ),
          ),
        ],
      ),
    );
  }
}



