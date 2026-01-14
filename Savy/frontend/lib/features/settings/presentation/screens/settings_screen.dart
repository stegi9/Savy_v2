import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../../../core/theme/app_colors.dart';
import '../../../../core/providers/app_providers.dart';
import '../../../../core/providers/preferences_provider.dart';
import '../../../../core/l10n/app_strings.dart';

class SettingsScreen extends ConsumerStatefulWidget {
  const SettingsScreen({super.key});

  @override
  ConsumerState<SettingsScreen> createState() => _SettingsScreenState();
}

class _SettingsScreenState extends ConsumerState<SettingsScreen> {
  final _nameController = TextEditingController();
  final _balanceController = TextEditingController();
  final _budgetController = TextEditingController();
  bool _budgetNotifications = true;
  bool _aiTips = true;
  bool _optimizationAlerts = true;
  bool _isLoading = false;

  @override
  void dispose() {
    _nameController.dispose();
    _balanceController.dispose();
    _budgetController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final settingsAsync = ref.watch(userSettingsProvider);
    final prefsState = ref.watch(preferencesProvider);
    final prefsNotifier = ref.read(preferencesProvider.notifier);
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;

    return Scaffold(
      backgroundColor: theme.scaffoldBackgroundColor,
      appBar: AppBar(
        title: Text(AppStrings.get('settingsTitle')),
        backgroundColor: colorScheme.primary,
        foregroundColor: colorScheme.onPrimary,
      ),
      body: settingsAsync.when(
        data: (settings) {
          if (_nameController.text.isEmpty) {
            _nameController.text = settings['full_name'] ?? '';
            final balance = settings['current_balance'];
            _balanceController.text = (balance is num)
                ? balance.toString()
                : (balance as String?) ?? '0';
            final budget = settings['monthly_budget'];
            _budgetController.text = (budget is num)
                ? budget.toString()
                : (budget as String?) ?? '0';
            _budgetNotifications = settings['budget_notifications'] ?? true;
            _aiTips = settings['ai_tips_enabled'] ?? true;
            _optimizationAlerts = settings['optimization_alerts'] ?? true;
          }

          return SingleChildScrollView(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                _SettingsSection(
                  title: AppStrings.get('profileSection'),
                  icon: Icons.person_outline,
                  children: [
                    _SettingsTextField(
                      controller: _nameController,
                      label: AppStrings.get('nameLabel'),
                      icon: Icons.badge_outlined,
                    ),
                    const SizedBox(height: 16),
                    _SettingsTextField(
                      controller: _balanceController,
                      label: AppStrings.get('balanceLabel'),
                      icon: Icons.account_balance_wallet_outlined,
                      keyboardType: TextInputType.number,
                    ),
                  ],
                ),
                const SizedBox(height: 24),
                _SettingsSection(
                  title: AppStrings.get('banksSection'),
                  icon: Icons.account_balance,
                  children: [
                    ListTile(
                      contentPadding: EdgeInsets.zero,
                      title: Text(AppStrings.get('addBankTitle'), style: TextStyle(fontWeight: FontWeight.w600, color: colorScheme.onSurface)),
                      subtitle: Text(AppStrings.get('addBankSubtitle'), style: TextStyle(color: colorScheme.onSurface.withOpacity(0.7))),
                      leading: Container(
                        padding: const EdgeInsets.all(8),
                        decoration: BoxDecoration(
                          color: colorScheme.primary.withOpacity(0.1),
                          borderRadius: BorderRadius.circular(8),
                        ),
                        child: Icon(Icons.add_link, color: colorScheme.primary),
                      ),
                      trailing: Icon(Icons.chevron_right, color: colorScheme.onSurface),
                      onTap: () => context.push('/bank-connect'),
                    ),
                  ],
                ),
                const SizedBox(height: 24),
                _SettingsSection(
                  title: AppStrings.get('budgetSection'),
                  icon: Icons.savings_outlined,
                  children: [
                    _SettingsTextField(
                      controller: _budgetController,
                      label: AppStrings.get('budgetLabel'),
                      icon: Icons.euro,
                      keyboardType: TextInputType.number,
                    ),
                  ],
                ),
                const SizedBox(height: 24),
                _SettingsSection(
                  title: AppStrings.get('notificationsSection'),
                  icon: Icons.notifications_outlined,
                  children: [
                    _SettingsSwitch(
                      title: AppStrings.get('budgetAlertTitle'),
                      subtitle: AppStrings.get('budgetAlertSubtitle'),
                      value: _budgetNotifications,
                      onChanged: (value) => setState(() => _budgetNotifications = value),
                    ),
                    _SettingsSwitch(
                      title: AppStrings.get('aiTipsTitle'),
                      subtitle: AppStrings.get('aiTipsSubtitle'),
                      value: _aiTips,
                      onChanged: (value) => setState(() => _aiTips = value),
                    ),
                    _SettingsSwitch(
                      title: AppStrings.get('optAlertTitle'),
                      subtitle: AppStrings.get('optAlertSubtitle'),
                      value: _optimizationAlerts,
                      onChanged: (value) => setState(() => _optimizationAlerts = value),
                    ),
                  ],
                ),
                const SizedBox(height: 24),
                _SettingsSection(
                  title: AppStrings.get('appearanceSection'),
                  icon: Icons.palette_outlined,
                  children: [
                    _SettingsSwitch(
                      title: AppStrings.get('darkModeTitle'),
                      subtitle: AppStrings.get('darkModeSubtitle'),
                      value: prefsNotifier.isDarkMode,
                      onChanged: (value) => prefsNotifier.toggleTheme(value),
                    ),
                    Padding(
                      padding: const EdgeInsets.only(top: 8.0, left: 4),
                      child: Row(
                        children: [
                          Icon(Icons.info_outline, size: 16, color: theme.colorScheme.primary),
                          const SizedBox(width: 8),
                          Text(
                            AppStrings.get('settingsApplyImmediately'),
                            style: TextStyle(
                              fontSize: 12,
                              color: theme.colorScheme.primary,
                              fontStyle: FontStyle.italic,
                            ),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 24),
                _SettingsSection(
                  title: AppStrings.get('languageSection'),
                  icon: Icons.language,
                  children: [
                    _SettingsSwitch(
                      title: AppStrings.get('languageTitle'),
                      subtitle: AppStrings.get('languageSubtitle'),
                      value: !prefsNotifier.isItalian,
                      onChanged: (value) => prefsNotifier.setLocale(value ? 'en' : 'it'),
                    ),
                  ],
                ),
                const SizedBox(height: 32),
                _SaveButton(
                  isLoading: _isLoading,
                  onPressed: _saveSettings,
                ),
              ],
            ),
          );
        },
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (e, s) => Center(child: Text('Errore: $e')),
      ),
    );
  }

  Future<void> _saveSettings() async {
    setState(() => _isLoading = true);

    try {
      final apiClient = ref.read(apiClientProvider);
      await apiClient.updateUserSettings({
        'full_name': _nameController.text,
        'current_balance': double.tryParse(_balanceController.text) ?? 0.0,
        'monthly_budget': double.tryParse(_budgetController.text) ?? 0.0,
        'budget_notifications': _budgetNotifications,
        'ai_tips_enabled': _aiTips,
        'optimization_alerts': _optimizationAlerts,
      });

      ref.invalidate(userSettingsProvider);
      ref.invalidate(dashboardDataProvider);

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: const Row(
              children: [
                Icon(Icons.check_circle, color: Colors.white),
                SizedBox(width: 12),
                Text('Impostazioni salvate con successo'),
              ],
            ),
            backgroundColor: AppColors.success,
            behavior: SnackBarBehavior.floating,
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
            margin: const EdgeInsets.all(16),
          ),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Errore: $e'),
            backgroundColor: AppColors.error,
          ),
        );
      }
    } finally {
      if (mounted) setState(() => _isLoading = false);
    }
  }
}

class _SettingsSection extends StatelessWidget {
  final String title;
  final IconData icon;
  final List<Widget> children;

  const _SettingsSection({
    required this.title,
    required this.icon,
    required this.children,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: theme.cardColor,
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.05),
            blurRadius: 10,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Container(
                padding: const EdgeInsets.all(8),
                decoration: BoxDecoration(
                  color: theme.colorScheme.primary.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Icon(icon, color: theme.colorScheme.primary, size: 20),
              ),
              const SizedBox(width: 12),
              Text(
                title,
                style: TextStyle(
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                  color: theme.colorScheme.onSurface,
                ),
              ),
            ],
          ),
          const SizedBox(height: 20),
          ...children,
        ],
      ),
    );
  }
}

class _SettingsTextField extends StatelessWidget {
  final TextEditingController controller;
  final String label;
  final IconData icon;
  final TextInputType? keyboardType;

  const _SettingsTextField({
    required this.controller,
    required this.label,
    required this.icon,
    this.keyboardType,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final isDark = theme.brightness == Brightness.dark;
    
    return TextField(
      controller: controller,
      style: TextStyle(color: theme.colorScheme.onSurface),
      decoration: InputDecoration(
        labelText: label,
        labelStyle: TextStyle(color: theme.colorScheme.onSurface.withOpacity(0.7)),
        prefixIcon: Icon(icon, color: theme.colorScheme.primary),
        filled: true,
        fillColor: isDark ? theme.scaffoldBackgroundColor : AppColors.background,
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: BorderSide.none,
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: BorderSide(color: theme.colorScheme.primary, width: 2),
        ),
      ),
      keyboardType: keyboardType,
    );
  }
}

class _SettingsSwitch extends StatelessWidget {
  final String title;
  final String subtitle;
  final bool value;
  final ValueChanged<bool> onChanged;

  const _SettingsSwitch({
    required this.title,
    required this.subtitle,
    required this.value,
    required this.onChanged,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final isDark = theme.brightness == Brightness.dark;

    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: isDark ? theme.scaffoldBackgroundColor : AppColors.background,
        borderRadius: BorderRadius.circular(12),
      ),
      child: Row(
        children: [
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  title,
                  style: TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.w600,
                    color: theme.colorScheme.onSurface,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  subtitle,
                  style: TextStyle(
                    fontSize: 13,
                    color: theme.colorScheme.onSurface.withOpacity(0.7),
                  ),
                ),
              ],
            ),
          ),
          Switch(
            value: value,
            onChanged: onChanged,
            activeThumbColor: theme.colorScheme.primary,
          ),
        ],
      ),
    );
  }
}

class _SaveButton extends StatelessWidget {
  final bool isLoading;
  final VoidCallback onPressed;

  const _SaveButton({
    required this.isLoading,
    required this.onPressed,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    
    return Container(
      width: double.infinity,
      height: 56,
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: [theme.colorScheme.primary, AppColors.primaryDark],
        ),
        borderRadius: BorderRadius.circular(12),
        boxShadow: [
          BoxShadow(
            color: theme.colorScheme.primary.withOpacity(0.4),
            blurRadius: 12,
            offset: const Offset(0, 6),
          ),
        ],
      ),
      child: ElevatedButton(
        onPressed: isLoading ? null : onPressed,
        style: ElevatedButton.styleFrom(
          backgroundColor: Colors.transparent,
          shadowColor: Colors.transparent,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(12),
          ),
        ),
        child: isLoading
            ? const SizedBox(
                height: 24,
                width: 24,
                child: CircularProgressIndicator(
                  strokeWidth: 2,
                  color: Colors.white,
                ),
              )
            : Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  const Icon(Icons.save_outlined, color: Colors.white),
                  const SizedBox(width: 12),
                  Text(
                    AppStrings.get('save'),
                  ),
                ],
              ),
      ),
    );
  }
}
