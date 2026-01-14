import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:fl_chart/fl_chart.dart';
import '../../../../core/theme/app_colors.dart';
import '../../../../core/providers/app_providers.dart';

class SpendingReportScreen extends ConsumerWidget {
  const SpendingReportScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final reportAsync = ref.watch(spendingReportProvider);

    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        title: const Text('Report Finanziario'),
        backgroundColor: AppColors.primary,
        foregroundColor: Colors.white,
      ),
      body: RefreshIndicator(
        onRefresh: () async {
          ref.invalidate(spendingReportProvider);
        },
        color: AppColors.primary,
        child: reportAsync.when(
          data: (reportData) {
            final report = reportData['data'] ?? {};
            final categories = (report['categories'] as List?)?.cast<Map<String, dynamic>>() ?? [];
            final totalSpent = (report['total_spent'] as num?)?.toDouble() ?? 0.0;
            final totalIncome = (report['total_income'] as num?)?.toDouble() ?? 0.0;
            final budget = (report['total_budget'] as num?)?.toDouble() ?? 0.0;
            final netBalance = totalIncome - totalSpent;

            return ListView(
              padding: const EdgeInsets.all(16),
              children: [
                _BalanceSummaryCard(
                  totalIncome: totalIncome,
                  totalSpent: totalSpent,
                  netBalance: netBalance,
                ),
                const SizedBox(height: 16),
                _BudgetCard(
                  totalSpent: totalSpent,
                  budget: budget,
                ),
                const SizedBox(height: 24),
                if (categories.isNotEmpty) ...[
                  const _SectionHeader(title: 'Distribuzione Spese'),
                  const SizedBox(height: 16),
                  _PieChartWidget(categories: categories),
                  const SizedBox(height: 24),
                  const _SectionHeader(title: 'Dettaglio per Categoria'),
                  const SizedBox(height: 12),
                  _CategoryBreakdown(categories: categories, totalSpent: totalSpent),
                ] else
                  _EmptyState(),
              ],
            );
          },
          loading: () => const Center(child: CircularProgressIndicator()),
          error: (e, s) => Center(
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                const Icon(Icons.error_outline, size: 64, color: AppColors.error),
                const SizedBox(height: 16),
                Text('Errore: $e'),
                const SizedBox(height: 16),
                ElevatedButton(
                  onPressed: () => ref.invalidate(spendingReportProvider),
                  child: const Text('Riprova'),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

class _BalanceSummaryCard extends StatelessWidget {
  final double totalIncome;
  final double totalSpent;
  final double netBalance;

  const _BalanceSummaryCard({
    required this.totalIncome,
    required this.totalSpent,
    required this.netBalance,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: [
            netBalance >= 0 ? AppColors.success : AppColors.error,
            (netBalance >= 0 ? AppColors.success : AppColors.error).withOpacity(0.7),
          ],
        ),
        borderRadius: BorderRadius.circular(20),
        boxShadow: [
          BoxShadow(
            color: (netBalance >= 0 ? AppColors.success : AppColors.error).withOpacity(0.3),
            blurRadius: 20,
            offset: const Offset(0, 10),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(
                netBalance >= 0 ? Icons.trending_up : Icons.trending_down,
                color: Colors.white70,
                size: 20,
              ),
              const SizedBox(width: 8),
              const Text(
                'Bilancio Netto',
                style: TextStyle(
                  fontSize: 14,
                  color: Colors.white70,
                  fontWeight: FontWeight.w500,
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          Text(
            '${netBalance >= 0 ? '+' : ''}€${netBalance.toStringAsFixed(2)}',
            style: const TextStyle(
              fontSize: 40,
              fontWeight: FontWeight.bold,
              color: Colors.white,
            ),
          ),
          const SizedBox(height: 24),
          Row(
            children: [
              Expanded(
                child: _BalanceItem(
                  icon: Icons.arrow_downward,
                  label: 'Entrate',
                  amount: totalIncome,
                  color: Colors.white70,
                ),
              ),
              Container(
                width: 1,
                height: 40,
                color: Colors.white30,
                margin: const EdgeInsets.symmetric(horizontal: 16),
              ),
              Expanded(
                child: _BalanceItem(
                  icon: Icons.arrow_upward,
                  label: 'Uscite',
                  amount: totalSpent,
                  color: Colors.white70,
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }
}

class _BalanceItem extends StatelessWidget {
  final IconData icon;
  final String label;
  final double amount;
  final Color color;

  const _BalanceItem({
    required this.icon,
    required this.label,
    required this.amount,
    required this.color,
  });

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            Icon(icon, size: 16, color: color),
            const SizedBox(width: 6),
            Text(label, style: TextStyle(fontSize: 12, color: color)),
          ],
        ),
        const SizedBox(height: 6),
        Text(
          '€${amount.toStringAsFixed(2)}',
          style: const TextStyle(
            fontSize: 20,
            fontWeight: FontWeight.bold,
            color: Colors.white,
          ),
        ),
      ],
    );
  }
}

class _BudgetCard extends StatelessWidget {
  final double totalSpent;
  final double budget;

  const _BudgetCard({
    required this.totalSpent,
    required this.budget,
  });

  @override
  Widget build(BuildContext context) {
    final percentage = budget > 0 ? (totalSpent / budget * 100).clamp(0, 100) : 0.0;
    final isOverBudget = totalSpent > budget;

    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: AppColors.surface,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(
          color: isOverBudget
              ? AppColors.error.withOpacity(0.3)
              : AppColors.success.withOpacity(0.3),
          width: 2,
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              const Text(
                'Budget Mensile',
                style: TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.w600,
                  color: AppColors.textPrimary,
                ),
              ),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                decoration: BoxDecoration(
                  color: isOverBudget
                      ? AppColors.error.withOpacity(0.1)
                      : AppColors.success.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(20),
                ),
                child: Text(
                  '${percentage.toStringAsFixed(0)}%',
                  style: TextStyle(
                    fontSize: 12,
                    fontWeight: FontWeight.bold,
                    color: isOverBudget ? AppColors.error : AppColors.success,
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          ClipRRect(
            borderRadius: BorderRadius.circular(8),
            child: LinearProgressIndicator(
              value: percentage / 100,
              minHeight: 12,
              backgroundColor: AppColors.surfaceVariant,
              valueColor: AlwaysStoppedAnimation<Color>(
                isOverBudget ? AppColors.error : AppColors.success,
              ),
            ),
          ),
          const SizedBox(height: 12),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                'Speso: €${totalSpent.toStringAsFixed(2)}',
                style: const TextStyle(fontSize: 12, color: AppColors.textSecondary),
              ),
              Text(
                'Budget: €${budget.toStringAsFixed(2)}',
                style: const TextStyle(fontSize: 12, color: AppColors.textSecondary),
              ),
            ],
          ),
        ],
      ),
    );
  }
}

class _SectionHeader extends StatelessWidget {
  final String title;

  const _SectionHeader({required this.title});

  @override
  Widget build(BuildContext context) {
    return Text(
      title,
      style: const TextStyle(
        fontSize: 20,
        fontWeight: FontWeight.bold,
        color: AppColors.textPrimary,
      ),
    );
  }
}

class _PieChartWidget extends StatelessWidget {
  final List<Map<String, dynamic>> categories;

  const _PieChartWidget({required this.categories});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: AppColors.surface,
        borderRadius: BorderRadius.circular(20),
      ),
      child: Column(
        children: [
          SizedBox(
            height: 220,
            child: PieChart(
              PieChartData(
                sections: categories.map((cat) {
                  final spent = (cat['total_spent'] as num?)?.toDouble() ?? 0.0;
                  final percentage = (cat['percentage_of_total'] as num?)?.toDouble() ?? 0.0;
                  final colorHex = cat['color'] as String? ?? '#3B82F6';
                  final color = _hexToColor(colorHex);

                  return PieChartSectionData(
                    value: spent,
                    title: '${percentage.toStringAsFixed(0)}%',
                    color: color,
                    radius: 70,
                    titleStyle: const TextStyle(
                      fontSize: 14,
                      fontWeight: FontWeight.bold,
                      color: Colors.white,
                    ),
                    badgeWidget: null,
                  );
                }).toList(),
                sectionsSpace: 3,
                centerSpaceRadius: 50,
                borderData: FlBorderData(show: false),
              ),
            ),
          ),
        ],
      ),
    );
  }

  Color _hexToColor(String hex) {
    final hexCode = hex.replaceAll('#', '');
    return Color(int.parse('FF$hexCode', radix: 16));
  }
}

class _CategoryBreakdown extends StatelessWidget {
  final List<Map<String, dynamic>> categories;
  final double totalSpent;

  const _CategoryBreakdown({
    required this.categories,
    required this.totalSpent,
  });

  @override
  Widget build(BuildContext context) {
    return Column(
      children: categories.map((cat) {
        final name = cat['category_name'] as String;
        final spent = (cat['total_spent'] as num).toDouble();
        final count = cat['transaction_count'] as int;
        final colorHex = cat['color'] as String? ?? '#3B82F6';
        final color = _hexToColor(colorHex);
        final percentage = totalSpent > 0 ? (spent / totalSpent * 100) : 0.0;

        return Container(
          margin: const EdgeInsets.only(bottom: 12),
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: AppColors.surface,
            borderRadius: BorderRadius.circular(12),
            border: Border.all(color: color.withOpacity(0.2)),
          ),
          child: Row(
            children: [
              Container(
                width: 48,
                height: 48,
                decoration: BoxDecoration(
                  color: color.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Center(
                  child: Icon(
                    _getIconData(cat['icon'] as String? ?? 'category'),
                    color: color,
                    size: 24,
                  ),
                ),
              ),
              const SizedBox(width: 16),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      name,
                      style: const TextStyle(
                        fontWeight: FontWeight.w600,
                        fontSize: 16,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      '$count transazion${count == 1 ? 'e' : 'i'} • ${percentage.toStringAsFixed(1)}%',
                      style: const TextStyle(
                        fontSize: 12,
                        color: AppColors.textSecondary,
                      ),
                    ),
                  ],
                ),
              ),
              Text(
                '€${spent.toStringAsFixed(2)}',
                style: TextStyle(
                  fontWeight: FontWeight.bold,
                  fontSize: 18,
                  color: color,
                ),
              ),
            ],
          ),
        );
      }).toList(),
    );
  }

  Color _hexToColor(String hex) {
    final hexCode = hex.replaceAll('#', '');
    return Color(int.parse('FF$hexCode', radix: 16));
  }

  IconData _getIconData(String iconName) {
    final iconMap = {
      'shopping_cart': Icons.shopping_cart,
      'restaurant': Icons.restaurant,
      'local_gas_station': Icons.local_gas_station,
      'home': Icons.home,
      'shopping_bag': Icons.shopping_bag,
      'fitness_center': Icons.fitness_center,
      'flight': Icons.flight,
      'hotel': Icons.hotel,
      'local_cafe': Icons.local_cafe,
      'movie': Icons.movie,
    };
    return iconMap[iconName] ?? Icons.category;
  }
}

class _EmptyState extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(48),
      child: const Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(Icons.pie_chart_outline, size: 80, color: AppColors.textSecondary),
          SizedBox(height: 24),
          Text(
            'Nessuna spesa registrata',
            style: TextStyle(
              fontSize: 18,
              fontWeight: FontWeight.w600,
              color: AppColors.textPrimary,
            ),
          ),
          SizedBox(height: 12),
          Text(
            'Inizia ad aggiungere transazioni per vedere i report',
            textAlign: TextAlign.center,
            style: TextStyle(
              fontSize: 14,
              color: AppColors.textSecondary,
            ),
          ),
        ],
      ),
    );
  }
}
