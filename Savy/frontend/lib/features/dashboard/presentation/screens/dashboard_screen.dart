import 'dart:ui';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:fl_chart/fl_chart.dart';
import '../../../../core/theme/app_colors.dart';
import '../../../../core/providers/app_providers.dart';
import '../../../../core/widgets/modern_widgets.dart';
import '../../../affiliate/presentation/widgets/smart_suggestion_card.dart';
import '../../../affiliate/presentation/providers/affiliate_provider.dart';
import '../../../../core/l10n/app_strings.dart';
import '../../../accounts/data/providers/account_provider.dart';
import '../../../accounts/presentation/widgets/account_card.dart';

/// SAVY Dashboard - Ultra-Modern Design
/// iOS/Revolut inspired with glassmorphism and fluid animations
class DashboardScreen extends ConsumerWidget {
  const DashboardScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final dashboardData = ref.watch(dashboardDataProvider);

    return Scaffold(
      extendBodyBehindAppBar: true,
      backgroundColor: Theme.of(context).scaffoldBackgroundColor,
      body: RefreshIndicator(
        onRefresh: () async {
          ref.invalidate(dashboardDataProvider);
          await Future.delayed(const Duration(milliseconds: 500));
        },
        color: AppColors.primary,
        child: dashboardData.when(
          data: (data) => _buildDashboard(context, ref, data),
          loading: () => _buildLoadingState(context),
          error: (error, stack) => _buildErrorState(context, ref, error),
        ),
      ),
      floatingActionButton: _buildAICoachButton(context, ref),
      floatingActionButtonLocation: FloatingActionButtonLocation.endFloat,
    );
  }

  Widget _buildLoadingState(BuildContext context) {
    return CustomScrollView(
      slivers: [
        _buildModernAppBar(context, 'Ciao 👋'),
        SliverPadding(
          padding: const EdgeInsets.all(20),
          sliver: SliverList(
            delegate: SliverChildListDelegate([
              ShimmerLoading(
                child: Container(
                  height: 220,
                  decoration: BoxDecoration(
                    color: Colors.white,
                    borderRadius: BorderRadius.circular(24),
                  ),
                ),
              ),
              const SizedBox(height: 20),
              ShimmerLoading(
                child: Container(
                  height: 120,
                  decoration: BoxDecoration(
                    color: Colors.white,
                    borderRadius: BorderRadius.circular(20),
                  ),
                ),
              ),
            ]),
          ),
        ),
      ],
    );
  }

  Widget _buildErrorState(BuildContext context, WidgetRef ref, Object error) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(32),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            IconContainer(
              icon: Icons.error_outline_rounded,
              color: AppColors.error,
              size: 80,
              iconSize: 48,
            ),
            const SizedBox(height: 24),
            Text(
              'Ops! Qualcosa è andato storto',
              style: Theme.of(context).textTheme.headlineSmall,
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 12),
            Text(
              error.toString(),
              style: Theme.of(context).textTheme.bodyMedium,
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 32),
            FilledButton.icon(
              onPressed: () => ref.invalidate(dashboardDataProvider),
              icon: const Icon(Icons.refresh_rounded),
              label: const Text('Riprova'),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildDashboard(BuildContext context, WidgetRef ref, Map<String, dynamic> data) {
    final profile = data['profile'];
    final settings = data['settings'];
    final bills = data['bills'] as List;

    final currentBalance = _parseDouble(profile['current_balance']);
    final monthlyBudget = _parseDouble(settings['monthly_budget']);
    final fullName = profile['full_name'] as String;

    return RefreshIndicator(
      onRefresh: () async {
        ref.invalidate(dashboardDataProvider);
        ref.invalidate(dashboardRecommendationProvider);
      },
      child: CustomScrollView(
        physics: const BouncingScrollPhysics(),
        slivers: [
          // Modern App Bar with blur effect
          _buildModernAppBar(context, 'Ciao, $fullName 👋'),

          SliverPadding(
            padding: const EdgeInsets.fromLTRB(20, 0, 20, 100),
            sliver: SliverList(
              delegate: SliverChildListDelegate([
                const SizedBox(height: 20),
                
                // Accounts Carousel (Total + Individuals)
                _AccountsCarousel(
                  totalBalance: currentBalance,
                  budget: monthlyBudget,
                ),
                
                const SizedBox(height: 24),
                
                // Stats Row
                const _StatsRow(),
                
                const SizedBox(height: 24),
                
                // Smart Suggestion
                const SmartSuggestionCard(),
                
                const SizedBox(height: 24),
                
                // Quick Actions Grid
                _ModernQuickActions(
                  onRefresh: () => ref.invalidate(dashboardDataProvider),
                ),
                
                const SizedBox(height: 32),
                
                // Spending Chart
                const _ModernSpendingChart(),
                
                const SizedBox(height: 32),
                
                // Bills Section
                if (bills.isNotEmpty)
                  _ModernBillsList(
                    bills: bills,
                    onRefresh: () => ref.invalidate(dashboardDataProvider),
                  ),
              ]),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildModernAppBar(BuildContext context, String greeting) {
    return SliverAppBar(
      expandedHeight: 120,
      floating: false,
      pinned: true,
      stretch: true,
      backgroundColor: Colors.transparent,
      elevation: 0,
      flexibleSpace: ClipRRect(
        child: BackdropFilter(
          filter: ImageFilter.blur(sigmaX: 10, sigmaY: 10),
          child: Container(
            decoration: BoxDecoration(
              gradient: LinearGradient(
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
                colors: [
                  AppColors.primary.withOpacity(0.95),
                  AppColors.primaryAccent.withOpacity(0.95),
                ],
              ),
            ),
            child: FlexibleSpaceBar(
              titlePadding: const EdgeInsets.only(left: 20, bottom: 16),
              title: Text(
                greeting,
                style: const TextStyle(
                  fontSize: 28,
                  fontWeight: FontWeight.w700,
                  color: Colors.white,
                  letterSpacing: -0.5,
                ),
              ),
              stretchModes: const [
                StretchMode.zoomBackground,
                StretchMode.fadeTitle,
              ],
            ),
          ),
        ),
      ),
      actions: [
        IconButton(
          icon: Container(
            padding: const EdgeInsets.all(8),
            decoration: BoxDecoration(
              color: Colors.white.withOpacity(0.2),
              shape: BoxShape.circle,
            ),
            child: const Icon(Icons.notifications_none_rounded, color: Colors.white, size: 22),
          ),
          onPressed: () {
            ScaffoldMessenger.of(context).showSnackBar(
              const SnackBar(
                content: Text('Nessuna notifica'),
                behavior: SnackBarBehavior.floating,
              ),
            );
          },
        ),
        IconButton(
          icon: Container(
            padding: const EdgeInsets.all(8),
            decoration: BoxDecoration(
              color: Colors.white.withOpacity(0.2),
              shape: BoxShape.circle,
            ),
            child: const Icon(Icons.settings_outlined, color: Colors.white, size: 22),
          ),
          onPressed: () async {
            await context.push('/settings');
          },
        ),
        const SizedBox(width: 8),
      ],
    );
  }

  Widget _buildAICoachButton(BuildContext context, WidgetRef ref) {
    return Container(
      decoration: BoxDecoration(
        gradient: const LinearGradient(
          colors: [AppColors.gradientBlueStart, AppColors.gradientBlueEnd],
        ),
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(
            color: AppColors.primary.withOpacity(0.4),
            blurRadius: 20,
            offset: const Offset(0, 10),
          ),
        ],
      ),
      child: Material(
        color: Colors.transparent,
        child: InkWell(
          onTap: () async {
            await context.push('/chat');
            ref.invalidate(dashboardDataProvider);
          },
          borderRadius: BorderRadius.circular(16),
          child: Padding(
            padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 16),
            child: Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                const Icon(
                  Icons.psychology_rounded,
                  color: Colors.white,
                  size: 24,
                ),
                const SizedBox(width: 12),
                Text(
                  'AI Coach',
                  style: Theme.of(context).textTheme.labelLarge?.copyWith(
                    color: Colors.white,
                    fontWeight: FontWeight.w600,
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  static double _parseDouble(dynamic value) {
    if (value is num) return value.toDouble();
    if (value is String) return double.tryParse(value) ?? 0.0;
    return 0.0;
  }
}

// Accounts Carousel (Total Balance + Individual Accounts)
// ============================================================================
class _AccountsCarousel extends ConsumerStatefulWidget {
  final double totalBalance;
  final double budget;

  const _AccountsCarousel({
    required this.totalBalance,
    required this.budget,
  });

  @override
  ConsumerState<_AccountsCarousel> createState() => _AccountsCarouselState();
}

class _AccountsCarouselState extends ConsumerState<_AccountsCarousel> {
  final PageController _pageController = PageController(viewportFraction: 0.93);
  int _currentIndex = 0;

  @override
  void dispose() {
    _pageController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final accountsState = ref.watch(accountsProvider);

    return Column(
      children: [
        SizedBox(
          height: 360, // Fixed height for cards, increased for modern balance card contents
          child: PageView(
            controller: _pageController,
            onPageChanged: (index) {
              setState(() => _currentIndex = index);
              // Update global selected account filter based on carousel swipe
              final accounts = ref.read(accountsProvider).valueOrNull ?? [];
              if (index == 0) {
                ref.read(selectedAccountIdProvider.notifier).state = null; // Total Wealth
              } else if (index - 1 < accounts.length) {
                ref.read(selectedAccountIdProvider.notifier).state = accounts[index - 1].id;
              }
            },
            physics: const BouncingScrollPhysics(),
            children: [
              // 1. Total Wealth Card inside a slightly padded container for the viewport fraction
              Padding(
                padding: const EdgeInsets.symmetric(horizontal: 6),
                child: _ModernBalanceCard(
                  balance: widget.totalBalance,
                  budget: widget.budget,
                ),
              ),
              // 2+. Individual Accounts
              ...accountsState.maybeWhen(
                data: (accounts) => accounts.map((account) => Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 6),
                  child: AccountCard(
                    account: account,
                    onTap: () => context.push('/accounts'), // Optional quick action
                  ),
                )).toList(),
                orElse: () => [],
              ),
              // 3. Add Account Prompt
              Padding(
                padding: const EdgeInsets.symmetric(horizontal: 6),
                child: GestureDetector(
                  onTap: () => context.push('/accounts'),
                  child: Container(
                    decoration: BoxDecoration(
                      color: Colors.white.withOpacity(0.05),
                      borderRadius: BorderRadius.circular(24),
                      border: Border.all(color: Colors.white.withOpacity(0.2), width: 1, style: BorderStyle.solid),
                    ),
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Container(
                          padding: const EdgeInsets.all(16),
                          decoration: BoxDecoration(
                            color: Theme.of(context).colorScheme.primary.withOpacity(0.2),
                            shape: BoxShape.circle,
                          ),
                          child: Icon(Icons.add, color: Theme.of(context).colorScheme.primary, size: 32),
                        ),
                        const SizedBox(height: 16),
                        Text('Aggiungi Conto', style: TextStyle(color: Theme.of(context).colorScheme.primary, fontWeight: FontWeight.bold, fontSize: 16)),
                      ],
                    ),
                  ),
                ),
              ),
            ],
          ),
        ),
        const SizedBox(height: 16),
        // Page Indicators
        accountsState.maybeWhen(
          data: (accounts) => Row(
            mainAxisAlignment: MainAxisAlignment.center,
            children: List.generate(
              accounts.length + 2, // Total + Accounts + Add Card
              (index) => AnimatedContainer(
                duration: const Duration(milliseconds: 300),
                margin: const EdgeInsets.symmetric(horizontal: 4),
                height: 6,
                width: _currentIndex == index ? 24 : 6,
                decoration: BoxDecoration(
                  color: _currentIndex == index 
                      ? Theme.of(context).colorScheme.primary 
                      : Colors.white.withOpacity(0.2),
                  borderRadius: BorderRadius.circular(3),
                ),
              ),
            ),
          ),
          orElse: () => const SizedBox(),
        ),
      ],
    );
  }
}

// ============================================================================
// Modern Balance Card with Glassmorphism
// ============================================================================
class _ModernBalanceCard extends ConsumerWidget {
  final double balance;
  final double budget;

  const _ModernBalanceCard({
    required this.balance,
    required this.budget,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final reportAsync = ref.watch(spendingReportProvider);
    
    final reportData = reportAsync.valueOrNull ?? {};
    final report = reportData['data'] ?? {};
    final totalSpent = (report['total_spent'] as num?)?.toDouble() ?? 0.0;
    final percentUsed = budget > 0 ? (totalSpent / budget * 100).clamp(0, 100) : 0.0;

    return GradientCard(
      colors: const [
        AppColors.gradientBlueStart,
        AppColors.gradientBlueEnd,
      ],
      padding: const EdgeInsets.all(28),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Flexible(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      AppStrings.get('availableBalance'),
                      style: const TextStyle(
                        fontSize: 15,
                        color: Colors.white70,
                        fontWeight: FontWeight.w500,
                        letterSpacing: -0.2,
                      ),
                    ),
                    const SizedBox(height: 12),
                    AnimatedCounter(
                      value: balance,
                      prefix: '€',
                      style: const TextStyle(
                        fontSize: 42,
                        fontWeight: FontWeight.w800,
                      color: Colors.white,
                      letterSpacing: -1.5,
                      height: 1,
                    ),
                  ),
                  ],
                ),
              ),
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: Colors.white.withOpacity(0.2),
                  borderRadius: BorderRadius.circular(16),
                ),
                child: const Icon(
                  Icons.account_balance_wallet_rounded,
                  color: Colors.white,
                  size: 32,
                ),
              ),
            ],
          ),
          
          const SizedBox(height: 24),
          
          Container(
            padding: const EdgeInsets.all(20),
            decoration: BoxDecoration(
              color: Colors.white.withOpacity(0.15),
              borderRadius: BorderRadius.circular(16),
              border: Border.all(
                color: Colors.white.withOpacity(0.3),
                width: 1,
              ),
            ),
            child: Column(
              children: [
                Row(
                  children: [
                    Expanded(
                      child: _BalanceInfo(
                        label: AppStrings.get('spent'),
                        value: '€${totalSpent.toStringAsFixed(2)}',
                        icon: Icons.arrow_upward_rounded,
                      ),
                    ),
                    Container(
                      width: 1,
                      height: 40,
                      color: Colors.white.withOpacity(0.3),
                    ),
                    Expanded(
                      child: _BalanceInfo(
                        label: AppStrings.get('budget'),
                        value: '€${budget.toStringAsFixed(2)}',
                        icon: Icons.flag_rounded,
                      ),
                    ),
                  ],
                ),
                
                const SizedBox(height: 20),
                
                Column(
                  children: [
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Flexible(
                          child: Text(
                            'Budget utilizzato',
                            style: const TextStyle(
                              fontSize: 13,
                              color: Colors.white70,
                              fontWeight: FontWeight.w500,
                            ),
                            overflow: TextOverflow.ellipsis,
                          ),
                        ),
                        Text(
                          '${percentUsed.toStringAsFixed(1)}%',
                          style: TextStyle(
                            fontSize: 15,
                            color: percentUsed > 90 ? AppColors.accentOrange : Colors.white,
                            fontWeight: FontWeight.w700,
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 10),
                    ClipRRect(
                      borderRadius: BorderRadius.circular(10),
                      child: LinearProgressIndicator(
                        value: percentUsed / 100,
                        minHeight: 10,
                        backgroundColor: Colors.white.withOpacity(0.2),
                        valueColor: AlwaysStoppedAnimation<Color>(
                          percentUsed > 90 
                              ? AppColors.accentOrange 
                              : AppColors.gradientGreenStart,
                        ),
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class _BalanceInfo extends StatelessWidget {
  final String label;
  final String value;
  final IconData icon;

  const _BalanceInfo({
    required this.label,
    required this.value,
    required this.icon,
  });

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Icon(icon, color: Colors.white70, size: 20),
        const SizedBox(height: 8),
        Text(
          label,
          style: const TextStyle(
            fontSize: 13,
            color: Colors.white60,
            fontWeight: FontWeight.w500,
          ),
        ),
        const SizedBox(height: 4),
        Text(
          value,
          style: const TextStyle(
            fontSize: 18,
            fontWeight: FontWeight.w700,
            color: Colors.white,
            letterSpacing: -0.3,
          ),
        ),
      ],
    );
  }
}

// ============================================================================
// Stats Row
// ============================================================================
class _StatsRow extends ConsumerWidget {
  const _StatsRow();

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final reportAsync = ref.watch(spendingReportProvider);
    
    return reportAsync.when(
      data: (reportData) {
        final report = reportData['data'] ?? {};
        final totalSpent = (report['total_spent'] as num?)?.toDouble() ?? 0.0;
        final totalIncome = (report['total_income'] as num?)?.toDouble() ?? 0.0;

        return Row(
          children: [
            Expanded(
              child: _StatCard(
                title: 'Entrate',
                amount: totalIncome,
                icon: Icons.arrow_downward_rounded,
                color: AppColors.success,
              ),
            ),
            const SizedBox(width: 16),
            Expanded(
              child: _StatCard(
                title: 'Uscite',
                amount: totalSpent,
                icon: Icons.arrow_upward_rounded,
                color: AppColors.error,
              ),
            ),
          ],
        );
      },
      loading: () => const SizedBox(height: 80, child: Center(child: CircularProgressIndicator())),
      error: (_, __) => const SizedBox(height: 80),
    );
  }
}

class _StatCard extends StatelessWidget {
  final String title;
  final double amount;
  final IconData icon;
  final Color color;

  const _StatCard({
    required this.title,
    required this.amount,
    required this.icon,
    required this.color,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Theme.of(context).cardColor,
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(
            color: AppColors.shadowLight,
            blurRadius: 10,
            offset: const Offset(0, 5),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(icon, color: color, size: 20),
              const SizedBox(width: 8),
              Text(
                title,
                style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                      color: Theme.of(context).colorScheme.onSurface.withOpacity(0.7),
                    ),
              ),
            ],
          ),
          const SizedBox(height: 8),
          AnimatedCounter(
            value: amount,
            prefix: '€',
            style: Theme.of(context).textTheme.titleLarge?.copyWith(
                  fontWeight: FontWeight.bold,
                  color: Theme.of(context).colorScheme.onSurface,
                ),
          ),
        ],
      ),
    );
  }
}

// ============================================================================
// Modern Quick Actions
// ============================================================================
class _ModernQuickActions extends StatelessWidget {
  final VoidCallback onRefresh;

  const _ModernQuickActions({required this.onRefresh});

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'Azioni Rapide',
          style: Theme.of(context).textTheme.titleLarge,
        ),
        const SizedBox(height: 16),
        Row(
          children: [
            Expanded(
              child: _ActionCard(
                icon: Icons.add_circle_outline_rounded,
                label: 'Nuova\nTransazione',
                gradient: const [AppColors.gradientBlueStart, AppColors.gradientBlueEnd],
                onTap: () async {
                  await context.push('/transactions');
                  onRefresh();
                },
              ),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: _ActionCard(
                icon: Icons.category_rounded,
                label: 'Gestisci\nCategorie',
                gradient: const [AppColors.accentPurple, AppColors.primaryAccent],
                onTap: () => context.push('/categories'),
              ),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: _ActionCard(
                icon: Icons.receipt_long_rounded,
                label: 'Bollette\nScadenza',
                gradient: const [AppColors.accentOrange, AppColors.warning],
                onTap: () async {
                  await context.push('/bills');
                  onRefresh();
                },
              ),
            ),
          ],
        ),
      ],
    );
  }
}

class _ActionCard extends StatelessWidget {
  final IconData icon;
  final String label;
  final List<Color> gradient;
  final VoidCallback onTap;

  const _ActionCard({
    required this.icon,
    required this.label,
    required this.gradient,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.symmetric(vertical: 20, horizontal: 12),
        decoration: BoxDecoration(
          gradient: LinearGradient(
            colors: gradient.map((c) => c.withOpacity(0.1)).toList(),
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
          ),
          borderRadius: BorderRadius.circular(16),
          border: Border.all(
            color: gradient.first.withOpacity(0.3),
            width: 1.5,
          ),
        ),
        child: Column(
          children: [
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                gradient: LinearGradient(colors: gradient),
                borderRadius: BorderRadius.circular(12),
              ),
              child: Icon(icon, color: Colors.white, size: 24),
            ),
            const SizedBox(height: 12),
            Text(
              label,
              textAlign: TextAlign.center,
              style: TextStyle(
                fontSize: 12,
                fontWeight: FontWeight.w600,
                color: Theme.of(context).colorScheme.onSurface,
                height: 1.3,
                letterSpacing: -0.1,
              ),
            ),
          ],
        ),
      ),
    );
  }
}

// ============================================================================
// Modern Spending Chart
// ============================================================================
class _ModernSpendingChart extends ConsumerWidget {
  const _ModernSpendingChart();

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final reportAsync = ref.watch(spendingReportProvider);
    
    return reportAsync.when(
      data: (reportData) {
        final report = reportData['data'] ?? {};
        final categories = (report['categories'] as List?)?.cast<Map<String, dynamic>>() ?? [];

        if (categories.isEmpty) {
          return _EmptyChartCard();
        }

        return Container(
          padding: const EdgeInsets.all(24),
          decoration: BoxDecoration(
            color: Theme.of(context).cardColor,
            borderRadius: BorderRadius.circular(24),
            boxShadow: [
              BoxShadow(
                color: AppColors.shadowLight,
                blurRadius: 20,
                offset: const Offset(0, 10),
              ),
            ],
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Flexible(
                    child: Text(
                      AppStrings.get('expensesByCategory'),
                      style: Theme.of(context).textTheme.titleLarge,
                      overflow: TextOverflow.ellipsis,
                    ),
                  ),
                  TextButton(
                    onPressed: () => context.push('/analytics/deep-dive'),
                    child: const Text('Dettagli'),
                  ),
                ],
              ),
              const SizedBox(height: 24),
              SizedBox(
                height: 200,
                child: PieChart(
                  PieChartData(
                    sections: categories.map((cat) {
                      final total = (cat['total_spent'] as num?)?.toDouble() ?? 0.0;
                      final percentage = (cat['percentage_of_total'] as num?)?.toDouble() ?? 0.0;
                      final colorHex = cat['color'] as String? ?? '#0A84FF';
                      final color = _hexToColor(colorHex);

                      return PieChartSectionData(
                        value: total,
                        title: '${percentage.toStringAsFixed(0)}%',
                        color: color,
                        radius: 70,
                        titleStyle: const TextStyle(
                          fontSize: 15,
                          fontWeight: FontWeight.w700,
                          color: Colors.white,
                          letterSpacing: -0.3,
                        ),
                      );
                    }).toList(),
                    sectionsSpace: 3,
                    centerSpaceRadius: 50,
                  ),
                ),
              ),
              const SizedBox(height: 24),
              ...categories.map((cat) {
                final name = cat['category_name'] as String;
                final total = (cat['total_spent'] as num?)?.toDouble() ?? 0.0;
                final colorHex = cat['color'] as String? ?? '#0A84FF';
                final color = _hexToColor(colorHex);

                return Padding(
                  padding: const EdgeInsets.only(bottom: 12),
                  child: Row(
                    children: [
                      Container(
                        width: 12,
                        height: 12,
                        decoration: BoxDecoration(
                          color: color,
                          borderRadius: BorderRadius.circular(3),
                        ),
                      ),
                      const SizedBox(width: 12),
                      Expanded(
                        child: Text(
                          name,
                          style: Theme.of(context).textTheme.bodyLarge,
                        ),
                      ),
                      Text(
                        '€${total.toStringAsFixed(2)}',
                        style: Theme.of(context).textTheme.titleSmall,
                      ),
                    ],
                  ),
                );
              }),
            ],
          ),
        );
      },
      loading: () => const SizedBox(height: 300, child: Center(child: CircularProgressIndicator())),
      error: (_, __) => const SizedBox(height: 300),
    );
  }

  Color _hexToColor(String hex) {
    if (hex.isEmpty) return Colors.blue;
    final hexCode = hex.replaceAll('#', '');
    if (hexCode.length == 6) {
      return Color(int.parse('FF$hexCode', radix: 16));
    }
    return Colors.blue;
  }
}

class _EmptyChartCard extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(48),
      decoration: BoxDecoration(
        color: Theme.of(context).cardColor,
        borderRadius: BorderRadius.circular(24),
      ),
      child: Column(
        children: [
          IconContainer(
            icon: Icons.pie_chart_outline_rounded,
            color: AppColors.textTertiary,
            size: 80,
            iconSize: 48,
          ),
          const SizedBox(height: 20),
          Text(
            'Nessuna spesa registrata',
            style: Theme.of(context).textTheme.titleMedium,
          ),
          const SizedBox(height: 8),
          Text(
            'Inizia ad aggiungere transazioni',
            style: Theme.of(context).textTheme.bodyMedium,
          ),
        ],
      ),
    );
  }
}

// ============================================================================
// Modern Bills List
// ============================================================================
class _ModernBillsList extends StatelessWidget {
  final List bills;
  final VoidCallback onRefresh;

  const _ModernBillsList({required this.bills, required this.onRefresh});

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Flexible(
              child: Text(
                'Bollette in Scadenza',
                style: Theme.of(context).textTheme.titleLarge,
                overflow: TextOverflow.ellipsis,
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
        const SizedBox(height: 16),
        ...bills.map((bill) {
          final name = bill['name'] as String;
          final amount = (bill['amount'] is num)
              ? (bill['amount'] as num).toDouble()
              : double.tryParse(bill['amount'].toString()) ?? 0.0;
          final dueDay = bill['due_day'] as int;

          return Container(
            margin: const EdgeInsets.only(bottom: 12),
            padding: const EdgeInsets.all(20),
            decoration: BoxDecoration(
              color: Theme.of(context).cardColor,
              borderRadius: BorderRadius.circular(16),
              border: Border.all(
                color: AppColors.warning.withOpacity(0.2),
                width: 1.5,
              ),
            ),
            child: Row(
              children: [
                IconContainer(
                  icon: Icons.receipt_rounded,
                  color: AppColors.warning,
                  size: 48,
                  iconSize: 24,
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        name,
                        style: Theme.of(context).textTheme.titleSmall,
                      ),
                      const SizedBox(height: 4),
                      Text(
                        'Scadenza: $dueDay del mese',
                        style: Theme.of(context).textTheme.bodySmall,
                      ),
                    ],
                  ),
                ),
                Text(
                  '€${amount.toStringAsFixed(2)}',
                  style: Theme.of(context).textTheme.titleMedium?.copyWith(
                    color: AppColors.warning,
                  ),
                ),
              ],
            ),
          );
        }),
      ],
    );
  }
}
