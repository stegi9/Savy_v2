import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:fl_chart/fl_chart.dart';
import '../../../../core/theme/app_colors.dart';
import '../../../../core/providers/app_providers.dart';
import 'package:savy_frontend/features/affiliate/presentation/widgets/smart_suggestion_card.dart';
import 'package:savy_frontend/features/affiliate/presentation/providers/affiliate_provider.dart';

import 'package:savy_frontend/core/l10n/app_strings.dart';

class DashboardScreen extends ConsumerWidget {
  const DashboardScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final dashboardData = ref.watch(dashboardDataProvider);
    final theme = Theme.of(context);

    return Scaffold(
      backgroundColor: theme.scaffoldBackgroundColor,
      body: dashboardData.when(
        data: (data) => _buildDashboard(context, ref, data),
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (error, stack) => Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(Icons.error_outline, size: 48, color: theme.colorScheme.error),
              const SizedBox(height: 16),
              Text('Errore: ${error.toString()}', style: TextStyle(color: theme.colorScheme.onSurface)),
              const SizedBox(height: 16),
              ElevatedButton(
                onPressed: () => ref.invalidate(dashboardDataProvider),
                child: const Text('Riprova'),
              ),
            ],
          ),
        ),
      ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: () async {
          await context.push('/chat');
          ref.invalidate(dashboardDataProvider);
        },
        backgroundColor: theme.colorScheme.primary,
        icon: Icon(Icons.psychology_rounded, color: theme.colorScheme.onPrimary),
        label: Text('Coach AI', style: TextStyle(color: theme.colorScheme.onPrimary)),
      ),
    );
  }

  Widget _buildDashboard(BuildContext context, WidgetRef ref, Map<String, dynamic> data) {
    final profile = data['profile'];
    final settings = data['settings'];
    final bills = data['bills'] as List;
    final reportData = data['report'];

    final currentBalance = _parseDouble(profile['current_balance']);
    final monthlyBudget = _parseDouble(settings['monthly_budget']);
    final fullName = profile['full_name'] as String;
    final theme = Theme.of(context);

    return RefreshIndicator(
      onRefresh: () async {
        ref.invalidate(dashboardDataProvider);
        ref.invalidate(dashboardRecommendationProvider);
      },
      child: CustomScrollView(
        slivers: [
          // App Bar with Gradient
          SliverAppBar(
            expandedHeight: 180,
            floating: false,
            pinned: true,
            backgroundColor: theme.colorScheme.primary,
            flexibleSpace: FlexibleSpaceBar(
              titlePadding: const EdgeInsets.only(left: 20, bottom: 16),
              title: const Text(
                'Dashboard',
                style: TextStyle(
                  fontSize: 20,
                  fontWeight: FontWeight.bold,
                  color: Colors.white,
                ),
              ),
              background: Container(
                decoration: BoxDecoration(
                  gradient: LinearGradient(
                    begin: Alignment.topLeft,
                    end: Alignment.bottomRight,
                    colors: [
                      theme.colorScheme.primary,
                      AppColors.primaryDark,
                    ],
                  ),
                ),
                child: SafeArea(
                  child: Padding(
                    padding: const EdgeInsets.fromLTRB(20, 16, 20, 60),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      mainAxisAlignment: MainAxisAlignment.end,
                      children: [
                        Text(
                          'Ciao, $fullName 👋',
                          style: const TextStyle(
                            fontSize: 16,
                            fontWeight: FontWeight.w500,
                            color: Colors.white70,
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
              ),
            ),
            actions: [
              IconButton(
                icon: const Icon(Icons.notifications_outlined, color: Colors.white),
                onPressed: () {
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(content: Text('Nessuna notifica')),
                  );
                },
              ),
              IconButton(
                icon: const Icon(Icons.settings_outlined, color: Colors.white),
                onPressed: () async {
                  await context.push('/settings');
                  ref.invalidate(dashboardDataProvider);
                },
              ),
            ],
          ),

          SliverPadding(
            padding: const EdgeInsets.all(16),
            sliver: SliverList(
              delegate: SliverChildListDelegate([
                // Balance Card
                _BalanceCard(
                  balance: currentBalance,
                  budget: monthlyBudget,
                  reportData: reportData,
                ),
                const SizedBox(height: 16),

                // Affiliate Suggestion
                const SmartSuggestionCard(),
                const SizedBox(height: 16),

                // Quick Actions
                _QuickActions(onRefresh: () => ref.invalidate(dashboardDataProvider)),
                const SizedBox(height: 24),

                // Spending Chart
                _SpendingChart(reportData: reportData),
                const SizedBox(height: 24),

                // Bills Section
                _BillsList(bills: bills, onRefresh: () => ref.invalidate(dashboardDataProvider)),
              ]),
            ),
          ),
        ],
      ),
    );
  }

  static double _parseDouble(dynamic value) {
    if (value is num) return value.toDouble();
    if (value is String) return double.tryParse(value) ?? 0.0;
    return 0.0;
  }
}

// Balance Card Widget
class _BalanceCard extends StatelessWidget {
  final double balance;
  final double budget;
  final Map<String, dynamic> reportData;

  const _BalanceCard({
    required this.balance,
    required this.budget,
    required this.reportData,
  });

  @override
  Widget build(BuildContext context) {
    final report = reportData['data'] ?? {};
    final totalSpent = (report['total_spent'] as num?)?.toDouble() ?? 0.0;
    final remaining = balance;
    final percentUsed = budget > 0 ? (totalSpent / budget * 100).clamp(0, 100) : 0.0;
    final theme = Theme.of(context);

    return Container(
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: [
            theme.colorScheme.primary,
            theme.colorScheme.primary.withOpacity(0.8),
          ],
        ),
        borderRadius: BorderRadius.circular(24),
        boxShadow: [
          BoxShadow(
            color: theme.colorScheme.primary.withOpacity(0.3),
            blurRadius: 20,
            offset: const Offset(0, 10),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            AppStrings.get('availableBalance'),
            style: const TextStyle(
              fontSize: 14,
              color: Colors.white70,
              fontWeight: FontWeight.w500,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            '€${remaining.toStringAsFixed(2)}',
            style: const TextStyle(
              fontSize: 40,
              fontWeight: FontWeight.bold,
              color: Colors.white,
            ),
          ),
          const SizedBox(height: 16),
          Row(
            children: [
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      AppStrings.get('spent'),
                      style: const TextStyle(fontSize: 12, color: Colors.white60),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      '€${totalSpent.toStringAsFixed(2)}',
                      style: const TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                        color: Colors.white,
                      ),
                    ),
                  ],
                ),
              ),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      AppStrings.get('budget'),
                      style: const TextStyle(fontSize: 12, color: Colors.white60),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      '€${budget.toStringAsFixed(2)}',
                      style: const TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                        color: Colors.white,
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          ClipRRect(
            borderRadius: BorderRadius.circular(8),
            child: LinearProgressIndicator(
              value: percentUsed / 100,
              minHeight: 8,
              backgroundColor: Colors.white24,
              valueColor: AlwaysStoppedAnimation<Color>(
                percentUsed > 90 ? theme.colorScheme.error : AppColors.accent,
              ),
            ),
          ),
          const SizedBox(height: 8),
          Text(
            '${percentUsed.toStringAsFixed(1)}${AppStrings.get('budgetUsed')}',
            style: const TextStyle(
              fontSize: 12,
              color: Colors.white70,
            ),
          ),
        ],
      ),
    );
  }
}

// Quick Actions
class _QuickActions extends StatelessWidget {
  final VoidCallback onRefresh;

  const _QuickActions({required this.onRefresh});

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    
    return Row(
      children: [
        Expanded(
          child: _ActionButton(
            icon: Icons.add,
            label: AppStrings.get('actionTransaction'),
            color: theme.colorScheme.primary,
            onTap: () async {
              await context.push('/transactions');
              onRefresh();
            },
          ),
        ),
        const SizedBox(width: 12),
        Expanded(
          child: _ActionButton(
            icon: Icons.category,
            label: AppStrings.get('actionCategories'),
            color: AppColors.secondary,
            onTap: () => context.push('/categories'),
          ),
        ),
        const SizedBox(width: 12),
        Expanded(
          child: _ActionButton(
            icon: Icons.receipt_long,
            label: AppStrings.get('actionBills'),
            color: AppColors.accent,
            onTap: () async {
              await context.push('/bills');
              onRefresh();
            },
          ),
        ),
      ],
    );
  }
}

class _ActionButton extends StatelessWidget {
  final IconData icon;
  final String label;
  final Color color;
  final VoidCallback onTap;

  const _ActionButton({
    required this.icon,
    required this.label,
    required this.color,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    
    return GestureDetector(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.symmetric(vertical: 16),
        decoration: BoxDecoration(
          color: theme.cardColor,
          borderRadius: BorderRadius.circular(16),
          border: Border.all(color: color.withOpacity(0.2)),
        ),
        child: Column(
          children: [
            Icon(icon, color: color, size: 28),
            const SizedBox(height: 8),
            Text(
              label,
              style: TextStyle(
                fontSize: 12,
                fontWeight: FontWeight.w600,
                color: theme.colorScheme.onSurface,
              ),
            ),
          ],
        ),
      ),
    );
  }
}

// Spending Chart
class _SpendingChart extends StatelessWidget {
  final Map<String, dynamic> reportData;

  const _SpendingChart({required this.reportData});

  @override
  Widget build(BuildContext context) {
    final report = reportData['data'] ?? {};
    final categories = (report['categories'] as List?)?.cast<Map<String, dynamic>>() ?? [];
    final theme = Theme.of(context);

    if (categories.isEmpty) {
      return _EmptyChartCard();
    }

    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: theme.cardColor,
        borderRadius: BorderRadius.circular(20),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                AppStrings.get('expensesByCategory'),
                style: TextStyle(
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                  color: theme.colorScheme.onSurface,
                ),
              ),
              TextButton(
                onPressed: () => context.push('/analytics/deep-dive'),
                child: Text(AppStrings.get('advancedAnalytics')),
              ),
            ],
          ),
          const SizedBox(height: 20),
          SizedBox(
            height: 200,
            child: PieChart(
              PieChartData(
                sections: categories.map((cat) {
                  final total = (cat['total_spent'] as num?)?.toDouble() ?? 0.0;
                  final percentage = (cat['percentage_of_total'] as num?)?.toDouble() ?? 0.0;
                  final colorHex = cat['color'] as String? ?? '#3B82F6';
                  final color = _hexToColor(colorHex);

                  return PieChartSectionData(
                    value: total,
                    title: '${percentage.toStringAsFixed(0)}%',
                    color: color,
                    radius: 60,
                    titleStyle: const TextStyle(
                      fontSize: 14,
                      fontWeight: FontWeight.bold,
                      color: Colors.white,
                    ),
                  );
                }).toList(),
                sectionsSpace: 2,
                centerSpaceRadius: 40,
              ),
            ),
          ),
          const SizedBox(height: 16),
          ...categories.map((cat) {
            final name = cat['category_name'] as String;
            final total = (cat['total_spent'] as num?)?.toDouble() ?? 0.0;
            final colorHex = cat['color'] as String? ?? '#3B82F6';
            final color = _hexToColor(colorHex);

            return Padding(
              padding: const EdgeInsets.only(bottom: 8),
              child: Row(
                children: [
                  Container(
                    width: 16,
                    height: 16,
                    decoration: BoxDecoration(
                      color: color,
                      shape: BoxShape.circle,
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(child: Text(name, style: TextStyle(color: theme.colorScheme.onSurface))),
                  Text(
                    '€${total.toStringAsFixed(2)}',
                    style: TextStyle(fontWeight: FontWeight.bold, color: theme.colorScheme.onSurface),
                  ),
                ],
              ),
            );
          }),
        ],
      ),
    );
  }

  Color _hexToColor(String hex) {
    final hexCode = hex.replaceAll('#', '');
    return Color(int.parse('FF$hexCode', radix: 16));
  }
}

class _EmptyChartCard extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    
    return Container(
      padding: const EdgeInsets.all(40),
      decoration: BoxDecoration(
        color: theme.cardColor,
        borderRadius: BorderRadius.circular(20),
      ),
      child: Center(
        child: Column(
          children: [
            const Icon(Icons.pie_chart_outline, size: 64, color: AppColors.textSecondary),
            const SizedBox(height: 16),
            Text(
              'Nessuna spesa registrata',
              style: TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.w600,
                color: theme.colorScheme.onSurface,
              ),
            ),
            const SizedBox(height: 8),
            const Text(
              'Inizia ad aggiungere transazioni',
              style: TextStyle(
                fontSize: 14,
                color: AppColors.textSecondary,
              ),
            ),
          ],
        ),
      ),
    );
  }
}

// Bills List
class _BillsList extends StatelessWidget {
  final List bills;
  final VoidCallback onRefresh;

  const _BillsList({required this.bills, required this.onRefresh});

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final isDark = theme.brightness == Brightness.dark;
    
    if (bills.isEmpty) {
      return const SizedBox.shrink();
    }

    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: theme.cardColor,
        borderRadius: BorderRadius.circular(20),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                'Bollette in Scadenza',
                style: TextStyle(
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                  color: theme.colorScheme.onSurface,
                ),
              ),
              TextButton(
                onPressed: () async {
                  await context.push('/bills');
                  onRefresh();
                },
                child: const Text('Vedi tutto'),
              ),
            ],
          ),
          const SizedBox(height: 12),
          ...bills.take(3).map((bill) {
            final name = bill['name'] as String;
            final amount = (bill['amount'] is num) 
                ? (bill['amount'] as num).toDouble()
                : double.tryParse(bill['amount'].toString()) ?? 0.0;
            final dueDay = bill['due_day'] as int;

            return Container(
              margin: const EdgeInsets.only(bottom: 12),
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: isDark ? theme.scaffoldBackgroundColor : AppColors.background,
                borderRadius: BorderRadius.circular(12),
              ),
              child: Row(
                children: [
                  Container(
                    padding: const EdgeInsets.all(10),
                    decoration: BoxDecoration(
                      color: AppColors.warning.withOpacity(0.1),
                      borderRadius: BorderRadius.circular(10),
                    ),
                    child: const Icon(Icons.receipt, color: AppColors.warning),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          name,
                          style: TextStyle(
                            fontWeight: FontWeight.w600,
                            fontSize: 15,
                            color: theme.colorScheme.onSurface,
                          ),
                        ),
                        Text(
                          'Scadenza: $dueDay del mese',
                          style: const TextStyle(
                            fontSize: 13,
                            color: AppColors.textSecondary,
                          ),
                        ),
                      ],
                    ),
                  ),
                  Text(
                    '€${amount.toStringAsFixed(2)}',
                    style: TextStyle(
                      fontWeight: FontWeight.bold,
                      fontSize: 16,
                      color: theme.colorScheme.onSurface,
                    ),
                  ),
                ],
              ),
            );
          }),
        ],
      ),
    );
  }
}
