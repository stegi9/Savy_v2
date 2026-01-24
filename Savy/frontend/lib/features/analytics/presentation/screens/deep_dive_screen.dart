import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'dart:math' as math;
import '../../../../core/theme/app_colors.dart';
import '../../../../core/providers/app_providers.dart';
import '../../../../core/l10n/app_strings.dart';
import '../widgets/cumulative_chart_widgets.dart';

class DeepDiveScreen extends ConsumerStatefulWidget {
  const DeepDiveScreen({super.key});

  @override
  ConsumerState<DeepDiveScreen> createState() => _DeepDiveScreenState();
}

class _DeepDiveScreenState extends ConsumerState<DeepDiveScreen> {
  String _selectedPeriod = 'monthly';
  int _selectedTabIndex = 0;
  String? _selectedCategoryId;

  @override
  Widget build(BuildContext context) {
    final analyticsAsync = ref.watch(deepDiveAnalyticsProvider(_selectedPeriod));
    final theme = Theme.of(context);

    return Scaffold(
      backgroundColor: theme.scaffoldBackgroundColor,
      appBar: AppBar(
        title: Text(AppStrings.get('analyticsTitle')),
        backgroundColor: theme.colorScheme.primary,
        foregroundColor: theme.colorScheme.onPrimary,
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: () {
              ref.invalidate(deepDiveAnalyticsProvider(_selectedPeriod));
            },
          ),
        ],
      ),
      body: analyticsAsync.when(
        data: (response) {
          final data = response['data'] ?? {};
          return _buildContent(data, theme);
        },
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (e, s) => Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(Icons.error_outline, size: 64, color: theme.colorScheme.error),
              const SizedBox(height: 16),
              Text('${AppStrings.get('error')}: $e', style: TextStyle(color: theme.colorScheme.error)),
              const SizedBox(height: 16),
              ElevatedButton(
                onPressed: () => ref.invalidate(deepDiveAnalyticsProvider(_selectedPeriod)),
                child: const Text('Riprova'), // 'Retry' key could be added, or use generic
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildContent(Map<String, dynamic> data, ThemeData theme) {
    return SingleChildScrollView(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          // Period Selector
          _buildPeriodSelector(theme),
          
          // Summary Cards
          Padding(
            padding: const EdgeInsets.all(16),
            child: _buildSummaryCards(data, theme),
          ),
          
          // AI Insights (horizontal scrollable)
          _buildAIInsightsSection(data, theme),
          
          // Visualization Tabs
          _buildVisualizationTabs(theme),
          
          // Main Chart Area
          _buildChartArea(data, theme),
          
          const SizedBox(height: 24),
        ],
      ),
    );
  }

  Widget _buildPeriodSelector(ThemeData theme) {
    return Container(
      padding: const EdgeInsets.all(16),
      color: theme.cardColor,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(Icons.calendar_today, size: 18, color: theme.colorScheme.primary),
              const SizedBox(width: 8),
              Text(
                AppStrings.get('selectPeriod'),
                style: TextStyle(fontSize: 14, fontWeight: FontWeight.w600, color: theme.colorScheme.onSurface),
              ),
            ],
          ),
          const SizedBox(height: 12),
          SegmentedButton<String>(
            segments: [
              ButtonSegment(
                value: 'monthly',
                label: Text(AppStrings.get('periodMonth')),
              ),
              ButtonSegment(
                value: '3months',
                label: Text(AppStrings.get('period3Months')),
              ),
              ButtonSegment(
                value: 'yearly',
                label: Text(AppStrings.get('periodYear')),
              ),
            ],
            selected: {_selectedPeriod},
            onSelectionChanged: (Set<String> newSelection) {
              setState(() {
                _selectedPeriod = newSelection.first;
                _selectedCategoryId = null;
              });
            },
            style: ButtonStyle(
              backgroundColor: WidgetStateProperty.resolveWith((states) {
                if (states.contains(WidgetState.selected)) {
                  return theme.colorScheme.primary;
                }
                return Colors.transparent;
              }),
              foregroundColor: WidgetStateProperty.resolveWith((states) {
                if (states.contains(WidgetState.selected)) {
                  return theme.colorScheme.onPrimary;
                }
                return theme.colorScheme.onSurface;
              }),
              side: WidgetStateProperty.all(BorderSide(color: theme.colorScheme.outline)),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildSummaryCards(Map<String, dynamic> data, ThemeData theme) {
    final totalSpent = (data['total_spent'] as num?)?.toDouble() ?? 0.0;
    final totalIncome = (data['total_income'] as num?)?.toDouble() ?? 0.0;
    final netBalance = (data['net_balance'] as num?)?.toDouble() ?? 0.0;
    final velocity = (data['spending_velocity'] as num?)?.toDouble() ?? 0.0;

    return Column(
      children: [
        Row(
          children: [
            Expanded(
              child: _SummaryCard(
                title: AppStrings.get('totalSpent'),
                value: '€${totalSpent.toStringAsFixed(2)}',
                icon: Icons.arrow_upward,
                color: theme.colorScheme.error,
              ),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: _SummaryCard(
                title: AppStrings.get('totalIncome'),
                value: '€${totalIncome.toStringAsFixed(2)}',
                icon: Icons.arrow_downward,
                color: AppColors.success,
              ),
            ),
          ],
        ),
        const SizedBox(height: 12),
        Row(
          children: [
            Expanded(
              child: _SummaryCard(
                title: AppStrings.get('netBalance'),
                value: '${netBalance >= 0 ? '+' : ''}€${netBalance.toStringAsFixed(2)}',
                icon: netBalance >= 0 ? Icons.trending_up : Icons.trending_down,
                color: netBalance >= 0 ? AppColors.success : theme.colorScheme.error,
              ),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: _SummaryCard(
                title: AppStrings.get('spendingVelocity'),
                value: '${velocity >= 0 ? '+' : ''}${velocity.toStringAsFixed(1)}%',
                icon: Icons.speed,
                color: velocity >= 0 ? AppColors.warning : AppColors.success,
                subtitle: velocity >= 0 ? AppStrings.get('velocityFaster') : AppStrings.get('velocitySlower'),
              ),
            ),
          ],
        ),
      ],
    );
  }

  Widget _buildAIInsightsSection(Map<String, dynamic> data, ThemeData theme) {
    final insights = (data['ai_insights'] as List?)?.cast<Map<String, dynamic>>() ?? [];
    
    if (insights.isEmpty) return const SizedBox();

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Padding(
          padding: const EdgeInsets.fromLTRB(16, 8, 16, 12),
          child: Row(
            children: [
              Icon(Icons.auto_awesome, size: 20, color: theme.colorScheme.primary),
              const SizedBox(width: 8),
              Text(
                AppStrings.get('aiInsights'),
                style: TextStyle(
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                  color: theme.colorScheme.onSurface,
                ),
              ),
              const Spacer(),
              TextButton.icon(
                onPressed: () => context.push('/chat'),
                icon: const Icon(Icons.chat_bubble_outline, size: 18),
                label: Text(AppStrings.get('askCoach')),
                style: TextButton.styleFrom(
                  foregroundColor: theme.colorScheme.primary,
                ),
              ),
            ],
          ),
        ),
        SizedBox(
          height: 120,
          child: ListView.builder(
            scrollDirection: Axis.horizontal,
            padding: const EdgeInsets.symmetric(horizontal: 16),
            itemCount: insights.length,
            itemBuilder: (context, index) {
              return _AIInsightCard(insight: insights[index]);
            },
          ),
        ),
      ],
    );
  }

  Widget _buildVisualizationTabs(ThemeData theme) {
    return Container(
      margin: const EdgeInsets.fromLTRB(16, 16, 16, 0),
      decoration: BoxDecoration(
        color: theme.cardColor,
        borderRadius: BorderRadius.circular(12),
      ),
      child: Padding(
        padding: const EdgeInsets.all(8),
        child: SegmentedButton<int>(
          segments: [
            ButtonSegment(
              value: 0,
              label: FittedBox(child: Text(AppStrings.get('distribution'), maxLines: 1)),
              icon: const Icon(Icons.pie_chart, size: 18),
            ),
            ButtonSegment(
              value: 1,
              label: FittedBox(child: Text(AppStrings.get('trend'), maxLines: 1)),
              icon: const Icon(Icons.show_chart, size: 18),
            ),
            ButtonSegment(
              value: 2,
              label: FittedBox(child: Text(AppStrings.get('comparison'), maxLines: 1)),
              icon: const Icon(Icons.bar_chart, size: 18),
            ),
          ],
          selected: {_selectedTabIndex},
          onSelectionChanged: (Set<int> newSelection) {
            setState(() => _selectedTabIndex = newSelection.first);
          },
          style: ButtonStyle(
            backgroundColor: WidgetStateProperty.resolveWith((states) {
              if (states.contains(WidgetState.selected)) {
                return theme.colorScheme.primary;
              }
              return Colors.transparent;
            }),
            foregroundColor: WidgetStateProperty.resolveWith((states) {
              if (states.contains(WidgetState.selected)) {
                return theme.colorScheme.onPrimary;
              }
              return theme.colorScheme.onSurface;
            }),
             side: WidgetStateProperty.all(BorderSide(color: theme.colorScheme.outline)),
          ),
        ),
      ),
    );
  }

  Widget _buildChartArea(Map<String, dynamic> data, ThemeData theme) {
    return Padding(
      padding: const EdgeInsets.all(16),
      child: _buildSelectedChart(data, theme),
    );
  }

  Widget _buildSelectedChart(Map<String, dynamic> data, ThemeData theme) {
    switch (_selectedTabIndex) {
      case 0:
        return _buildTreemapChart(data, theme);
      case 1:
        return _buildCumulativeLineChart(data, theme);
      case 2:
        return _buildComparisonChart(data, theme);
      default:
        return const SizedBox();
    }
  }

  Widget _buildTreemapChart(Map<String, dynamic> data, ThemeData theme) {
    final categories = (data['categories_comparison'] as List?)?.cast<Map<String, dynamic>>() ?? [];
    
    if (categories.isEmpty) {
      return _buildEmptyState(AppStrings.get('noData'), theme);
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
          Text(
            AppStrings.get('expensesDistribution'),
            style: TextStyle(
              fontSize: 20,
              fontWeight: FontWeight.bold,
              color: theme.colorScheme.onSurface,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            AppStrings.get('tapForDetails'),
            style: const TextStyle(fontSize: 12, color: AppColors.textSecondary),
          ),
          const SizedBox(height: 24),
          _ImprovedTreemapWidget(
            categories: categories,
            onCategoryTap: (categoryId) {
              setState(() {
                _selectedCategoryId = _selectedCategoryId == categoryId ? null : categoryId;
              });
            },
            selectedCategoryId: _selectedCategoryId,
          ),
        ],
      ),
    );
  }

  Widget _buildCumulativeLineChart(Map<String, dynamic> data, ThemeData theme) {
    final currentCumulative = (data['current_cumulative'] as List?)?.cast<Map<String, dynamic>>() ?? [];
    final previousCumulative = (data['previous_cumulative'] as List?)?.cast<Map<String, dynamic>>() ?? [];
    final projected = (data['projected_end_of_month'] as num?)?.toDouble() ?? 0.0;
    final totalSpent = (data['total_spent'] as num?)?.toDouble() ?? 0.0;
    
    if (currentCumulative.isEmpty) {
      return _buildEmptyState(AppStrings.get('noData'), theme);
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
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      AppStrings.get('cumulativeTrend'),
                      style: TextStyle(
                        fontSize: 20,
                        fontWeight: FontWeight.bold,
                        color: theme.colorScheme.onSurface,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      AppStrings.get('comparePrevious'),
                      style: const TextStyle(fontSize: 12, color: AppColors.textSecondary),
                    ),
                  ],
                ),
              ),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                decoration: BoxDecoration(
                  color: AppColors.warning.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(20),
                  border: Border.all(color: AppColors.warning.withOpacity(0.3)),
                ),
                child: Column(
                  children: [
                    Text(
                      AppStrings.get('projection'),
                      style: const TextStyle(
                        fontSize: 10,
                        color: AppColors.warning,
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                    Text(
                      '€${projected.toStringAsFixed(0)}',
                      style: const TextStyle(
                        fontSize: 16,
                        fontWeight: FontWeight.bold,
                        color: AppColors.warning,
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
          const SizedBox(height: 24),
          CumulativeLineChartWidget(
            currentData: currentCumulative,
            previousData: previousCumulative,
            projected: projected,
            totalSpent: totalSpent,
          ),
          const SizedBox(height: 16),
          Wrap(
            spacing: 24,
            runSpacing: 8,
            alignment: WrapAlignment.center,
            children: [
              LegendItem(
                color: theme.colorScheme.primary,
                label: AppStrings.get('currentPeriod'),
                isArea: true,
              ),
              LegendItem(
                color: AppColors.textSecondary,
                label: AppStrings.get('previousPeriod'),
                isDashed: true,
              ),
              LegendItem(
                color: AppColors.warning,
                label: AppStrings.get('projection'),
                isDashed: true,
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildComparisonChart(Map<String, dynamic> data, ThemeData theme) {
    final categories = (data['categories_comparison'] as List?)?.cast<Map<String, dynamic>>() ?? [];
    
    if (categories.isEmpty) {
      return _buildEmptyState(AppStrings.get('noData'), theme);
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
          Text(
            AppStrings.get('periodComparison'),
            style: TextStyle(
              fontSize: 20,
              fontWeight: FontWeight.bold,
              color: theme.colorScheme.onSurface,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            AppStrings.get('comparePrevious'),
            style: const TextStyle(fontSize: 12, color: AppColors.textSecondary),
          ),
          const SizedBox(height: 24),
          _ComparisonBarsWidget(
            categories: categories,
            onCategoryTap: (categoryId) {
              setState(() {
                _selectedCategoryId = _selectedCategoryId == categoryId ? null : categoryId;
              });
            },
            selectedCategoryId: _selectedCategoryId,
          ),
        ],
      ),
    );
  }

  Widget _buildEmptyState(String message, ThemeData theme) {
    return Container(
      height: 300,
      alignment: Alignment.center,
      decoration: BoxDecoration(
        color: theme.cardColor,
        borderRadius: BorderRadius.circular(20),
      ),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(Icons.inbox_outlined, size: 64, color: AppColors.textSecondary.withOpacity(0.5)),
          const SizedBox(height: 16),
          Text(
            message,
            style: const TextStyle(fontSize: 16, color: AppColors.textSecondary),
          ),
        ],
      ),
    );
  }
}

// ============================================================================
// WIDGETS
// ============================================================================

class _SummaryCard extends StatelessWidget {
  final String title;
  final String value;
  final IconData icon;
  final Color color;
  final String? subtitle;

  const _SummaryCard({
    required this.title,
    required this.value,
    required this.icon,
    required this.color,
    this.subtitle,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: theme.cardColor,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: color.withOpacity(0.2)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Container(
                padding: const EdgeInsets.all(8),
                decoration: BoxDecoration(
                  color: color.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Icon(icon, size: 18, color: color),
              ),
              const SizedBox(width: 8),
              Expanded(
                child: Text(
                  title,
                  style: const TextStyle(
                    fontSize: 12,
                    color: AppColors.textSecondary,
                    fontWeight: FontWeight.w500,
                  ),
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          Text(
            value,
            style: TextStyle(
              fontSize: 18,
              fontWeight: FontWeight.bold,
              color: color,
            ),
          ),
          if (subtitle != null) ...[
            const SizedBox(height: 4),
            Text(
              subtitle!,
              style: const TextStyle(
                fontSize: 10,
                color: AppColors.textSecondary,
              ),
            ),
          ],
        ],
      ),
    );
  }
}

class _AIInsightCard extends StatelessWidget {
  final Map<String, dynamic> insight;

  const _AIInsightCard({required this.insight});

  @override
  Widget build(BuildContext context) {
    final type = insight['insight_type'] as String;
    final title = insight['title'] as String;
    final message = insight['message'] as String;
    final theme = Theme.of(context);

    Color color;
    IconData icon;
    switch (type) {
      case 'warning':
        color = AppColors.warning;
        icon = Icons.warning_amber_rounded;
        break;
      case 'success':
        color = AppColors.success;
        icon = Icons.check_circle_rounded;
        break;
      default:
        color = theme.colorScheme.primary;
        icon = Icons.info_rounded;
    }

    return Container(
      width: 280,
      margin: const EdgeInsets.only(right: 12),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: [color.withOpacity(0.1), color.withOpacity(0.05)],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: color.withOpacity(0.3)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(icon, size: 24, color: color),
              const SizedBox(width: 8),
              Expanded(
                child: Text(
                  title,
                  style: TextStyle(
                    fontSize: 14,
                    fontWeight: FontWeight.bold,
                    color: color,
                  ),
                  maxLines: 2,
                  overflow: TextOverflow.ellipsis,
                ),
              ),
            ],
          ),
          const SizedBox(height: 8),
          Expanded(
            child: Text(
              message,
              style: TextStyle(
                fontSize: 12,
                color: theme.colorScheme.onSurface,
                height: 1.4,
              ),
              maxLines: 3,
              overflow: TextOverflow.ellipsis,
            ),
          ),
        ],
      ),
    );
  }
}

class _ImprovedTreemapWidget extends StatelessWidget {
  final List<Map<String, dynamic>> categories;
  final Function(String) onCategoryTap;
  final String? selectedCategoryId;

  const _ImprovedTreemapWidget({
    required this.categories,
    required this.onCategoryTap,
    this.selectedCategoryId,
  });

  @override
  Widget build(BuildContext context) {
    // Sort by amount descending
    final sortedCategories = List<Map<String, dynamic>>.from(categories)
      ..sort((a, b) {
        final aAmount = (a['current_amount'] as num?)?.toDouble() ?? 0.0;
        final bAmount = (b['current_amount'] as num?)?.toDouble() ?? 0.0;
        return bAmount.compareTo(aAmount);
      });

    return GridView.builder(
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
        crossAxisCount: 2,
        childAspectRatio: 1.2,
        crossAxisSpacing: 12,
        mainAxisSpacing: 12,
      ),
      itemCount: sortedCategories.length,
      itemBuilder: (context, index) {
        final cat = sortedCategories[index];
        final amount = (cat['current_amount'] as num?)?.toDouble() ?? 0.0;
        final previousAmount = (cat['previous_amount'] as num?)?.toDouble() ?? 0.0;
        final name = cat['category_name'] as String;
        final colorHex = cat['color'] as String? ?? '#3B82F6';
        final isAnomaly = cat['is_anomaly'] as bool? ?? false;
        final categoryId = cat['category_id'] as String?;
        final isSelected = categoryId == selectedCategoryId;
        final changePercentage = (cat['change_percentage'] as num?)?.toDouble() ?? 0.0;
        
        Color color = _hexToColor(colorHex);
        if (isAnomaly) {
          color = changePercentage > 0 ? AppColors.error : AppColors.success;
        }

        return GestureDetector(
          onTap: () {
             if (categoryId != null) onCategoryTap(categoryId);
          },
          child: AnimatedContainer(
            duration: const Duration(milliseconds: 200),
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: color,
              borderRadius: BorderRadius.circular(16),
              border: isSelected ? Border.all(color: Colors.white, width: 3) : null,
              boxShadow: isSelected
                  ? [BoxShadow(color: color.withOpacity(0.5), blurRadius: 12, offset: const Offset(0, 4))]
                  : [BoxShadow(color: Colors.black.withOpacity(0.1), blurRadius: 4, offset: const Offset(0, 2))],
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Expanded(
                      child: Text(
                        name,
                        style: const TextStyle(
                          fontSize: 14,
                          fontWeight: FontWeight.bold,
                          color: Colors.white,
                        ),
                        maxLines: 2,
                        overflow: TextOverflow.ellipsis,
                      ),
                    ),
                    if (isAnomaly)
                      Container(
                        padding: const EdgeInsets.all(4),
                        decoration: BoxDecoration(
                          color: Colors.white.withOpacity(0.2),
                          borderRadius: BorderRadius.circular(6),
                        ),
                        child: Icon(
                          changePercentage > 0 ? Icons.trending_up : Icons.trending_down,
                          color: Colors.white,
                          size: 14,
                        ),
                      ),
                  ],
                ),
                Text(
                  '€${amount.toStringAsFixed(0)}',
                  style: const TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                    color: Colors.white,
                  ),
                ),
              ],
            ),
          ),
        );
      },
    );
  }

  Color _hexToColor(String hex) {
    final hexCode = hex.replaceAll('#', '');
    return Color(int.parse('FF$hexCode', radix: 16));
  }
}

class _ComparisonBarsWidget extends StatelessWidget {
  final List<Map<String, dynamic>> categories;
  final Function(String) onCategoryTap;
  final String? selectedCategoryId;

  const _ComparisonBarsWidget({
    required this.categories,
    required this.onCategoryTap,
    this.selectedCategoryId,
  });

  @override
  Widget build(BuildContext context) {
     final theme = Theme.of(context);
    // Sort by current amount descending
    final sortedCategories = List<Map<String, dynamic>>.from(categories)
      ..sort((a, b) {
        final aAmount = (a['current_amount'] as num?)?.toDouble() ?? 0.0;
        final bAmount = (b['current_amount'] as num?)?.toDouble() ?? 0.0;
        return bAmount.compareTo(aAmount);
      });

    final maxVal = sortedCategories.fold(0.0, (prev, cat) {
      final current = (cat['current_amount'] as num?)?.toDouble() ?? 0.0;
      final previous = (cat['previous_amount'] as num?)?.toDouble() ?? 0.0;
      return math.max(prev, math.max(current, previous));
    });

    return ListView.builder(
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      itemCount: sortedCategories.length,
      itemBuilder: (context, index) {
        final cat = sortedCategories[index];
        final currentAmount = (cat['current_amount'] as num?)?.toDouble() ?? 0.0;
        final previousAmount = (cat['previous_amount'] as num?)?.toDouble() ?? 0.0;
        final name = cat['category_name'] as String;
        final colorHex = cat['color'] as String? ?? '#3B82F6';
        final categoryId = cat['category_id'] as String?;
        final isSelected = categoryId == selectedCategoryId;
        
        final color = _hexToColor(colorHex);

        return GestureDetector(
          onTap: () {
             if (categoryId != null) onCategoryTap(categoryId);
          },
          child: Container(
            margin: const EdgeInsets.only(bottom: 16),
            padding: const EdgeInsets.all(12),
            decoration: isSelected 
              ? BoxDecoration(
                  color: color.withOpacity(0.05),
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(color: color.withOpacity(0.3)),
                )
              : null,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text(
                      name,
                      style: TextStyle(
                        fontWeight: FontWeight.w600,
                        fontSize: 14,
                        color: theme.colorScheme.onSurface,
                      ),
                    ),
                    Text(
                      '€${currentAmount.toStringAsFixed(0)}',
                      style: TextStyle(
                        fontWeight: FontWeight.bold,
                        fontSize: 14,
                        color: theme.colorScheme.onSurface,
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 8),
                Stack(
                  children: [
                    // Background track
                    Container(
                      height: 12,
                      width: double.infinity,
                      decoration: BoxDecoration(
                        color: theme.colorScheme.surfaceContainerHighest,
                        borderRadius: BorderRadius.circular(6),
                      ),
                    ),
                    // Previous period marker (if larger)
                    if (previousAmount > currentAmount)
                      FractionallySizedBox(
                        widthFactor: (previousAmount / maxVal).clamp(0.0, 1.0),
                        child: Container(
                          height: 12,
                          decoration: BoxDecoration(
                            color: AppColors.textSecondary.withOpacity(0.3),
                            borderRadius: BorderRadius.circular(6),
                          ),
                        ),
                      ),
                    // Current period bar
                    FractionallySizedBox(
                      widthFactor: (currentAmount / maxVal).clamp(0.0, 1.0),
                      child: Container(
                        height: 12,
                        decoration: BoxDecoration(
                          color: color,
                          borderRadius: BorderRadius.circular(6),
                        ),
                      ),
                    ),
                     // Previous period marker (if smaller/overlay)
                    if (previousAmount <= currentAmount && previousAmount > 0)
                      FractionallySizedBox(
                        widthFactor: (previousAmount / maxVal).clamp(0.0, 1.0),
                        child: Container(
                          height: 12,
                          decoration: BoxDecoration(
                            border: Border(
                              right: BorderSide(
                                color: AppColors.textSecondary.withOpacity(0.5),
                                width: 2,
                              ),
                            ),
                          ),
                        ),
                      ),
                  ],
                ),
                if (isSelected) 
                  Padding(
                    padding: const EdgeInsets.only(top: 8),
                    child: Text(
                      'Precedente: €${previousAmount.toStringAsFixed(0)}',
                      style: const TextStyle(
                        fontSize: 12,
                        color: AppColors.textSecondary,
                        fontStyle: FontStyle.italic,
                      ),
                    ),
                  ),
              ],
            ),
          ),
        );
      },
    );
  }

  Color _hexToColor(String hex) {
    final hexCode = hex.replaceAll('#', '');
    return Color(int.parse('FF$hexCode', radix: 16));
  }
}
