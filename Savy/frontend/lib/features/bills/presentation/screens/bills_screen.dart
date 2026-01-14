import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../../core/theme/app_colors.dart';
import '../../../../core/providers/app_providers.dart';
import '../../../../core/l10n/app_strings.dart';

class BillsScreen extends ConsumerWidget {
  const BillsScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final billsAsync = ref.watch(billsProvider);
    final theme = Theme.of(context);

    return Scaffold(
      backgroundColor: theme.scaffoldBackgroundColor,
      appBar: AppBar(
        title: Text(AppStrings.get('billsTitle')),
        backgroundColor: theme.colorScheme.primary,
        foregroundColor: theme.colorScheme.onPrimary,
      ),
      body: billsAsync.when(
        data: (bills) {
          if (bills.isEmpty) {
            return _buildEmptyState(context, ref, theme);
          }

          return RefreshIndicator(
            onRefresh: () async {
              ref.invalidate(billsProvider);
            },
            child: ListView.builder(
              padding: const EdgeInsets.all(16),
              itemCount: bills.length,
              itemBuilder: (context, index) {
                final bill = bills[index];
                return _BillCard(
                  bill: bill,
                  onEdit: () => _showEditBillDialog(context, ref, bill),
                  onDelete: () => _deleteBill(context, ref, bill['id']),
                  onPayment: () => _registerPayment(context, ref, bill),
                );
              },
            ),
          );
        },
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (e, s) => Center(child: Text('${AppStrings.get('error')}: $e', style: TextStyle(color: theme.colorScheme.error))),
      ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: () => _showAddBillDialog(context, ref),
        backgroundColor: theme.colorScheme.primary,
        icon: Icon(Icons.add, color: theme.colorScheme.onPrimary),
        label: Text(AppStrings.get('newBill'), style: TextStyle(color: theme.colorScheme.onPrimary)),
      ),
    );
  }

  Widget _buildEmptyState(BuildContext context, WidgetRef ref, ThemeData theme) {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Container(
            padding: const EdgeInsets.all(32),
            decoration: BoxDecoration(
              color: AppColors.warning.withOpacity(0.1),
              shape: BoxShape.circle,
            ),
            child: const Icon(
              Icons.receipt_long,
              size: 64,
              color: AppColors.warning,
            ),
          ),
          const SizedBox(height: 24),
          Text(
            AppStrings.get('noBills'),
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
              AppStrings.get('addBillPrompt'),
              textAlign: TextAlign.center,
              style: const TextStyle(
                fontSize: 14,
                color: AppColors.textSecondary,
              ),
            ),
          ),
          const SizedBox(height: 32),
          ElevatedButton.icon(
            onPressed: () => _showAddBillDialog(context, ref),
            icon: const Icon(Icons.add),
            label: Text(AppStrings.get('newBill')),
            style: ElevatedButton.styleFrom(
              padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 16),
              backgroundColor: theme.colorScheme.primary,
              foregroundColor: theme.colorScheme.onPrimary,
            ),
          ),
        ],
      ),
    );
  }

  Future<void> _showAddBillDialog(BuildContext context, WidgetRef ref) async {
    final nameController = TextEditingController();
    final amountController = TextEditingController();
    final dueDayController = TextEditingController();
    final providerController = TextEditingController();
    String category = 'energy';
    final theme = Theme.of(context);

    await showDialog(
      context: context,
      builder: (context) => StatefulBuilder(
        builder: (context, setState) => AlertDialog(
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
          backgroundColor: theme.cardColor,
          title: Row(
            children: [
              Container(
                padding: const EdgeInsets.all(8),
                decoration: BoxDecoration(
                  color: AppColors.warning.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: const Icon(Icons.receipt, color: AppColors.warning),
              ),
              const SizedBox(width: 12),
              Text(AppStrings.get('newBill'), style: TextStyle(color: theme.colorScheme.onSurface)),
            ],
          ),
          content: SingleChildScrollView(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                TextField(
                  controller: nameController,
                  decoration: InputDecoration(
                    labelText: AppStrings.get('nameLabel'),
                    prefixIcon: Icon(Icons.label_outline, color: theme.colorScheme.secondary),
                    labelStyle: TextStyle(color: theme.colorScheme.onSurface.withOpacity(0.7)),
                    border: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(12),
                    ),
                    enabledBorder: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(12),
                      borderSide: BorderSide(color: theme.colorScheme.outline),
                    ),
                  ),
                  style: TextStyle(color: theme.colorScheme.onSurface),
                  textCapitalization: TextCapitalization.words,
                ),
                const SizedBox(height: 16),
                TextField(
                  controller: amountController,
                  decoration: InputDecoration(
                    labelText: '${AppStrings.get('amount')} (€)',
                    prefixIcon: Icon(Icons.euro, color: theme.colorScheme.secondary),
                    labelStyle: TextStyle(color: theme.colorScheme.onSurface.withOpacity(0.7)),
                    border: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(12),
                    ),
                    enabledBorder: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(12),
                      borderSide: BorderSide(color: theme.colorScheme.outline),
                    ),
                    helperText: 'Può essere un importo stimato', // Add key if needed or leave as is if minor
                    helperStyle: const TextStyle(color: AppColors.textSecondary),
                  ),
                  style: TextStyle(color: theme.colorScheme.onSurface),
                  keyboardType: TextInputType.number,
                ),
                const SizedBox(height: 16),
                TextField(
                  controller: dueDayController,
                  decoration: InputDecoration(
                    labelText: 'Giorno scadenza (1-31)', // Add key
                    prefixIcon: Icon(Icons.calendar_today, color: theme.colorScheme.secondary),
                    labelStyle: TextStyle(color: theme.colorScheme.onSurface.withOpacity(0.7)),
                    border: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(12),
                    ),
                    enabledBorder: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(12),
                      borderSide: BorderSide(color: theme.colorScheme.outline),
                    ),
                  ),
                  style: TextStyle(color: theme.colorScheme.onSurface),
                  keyboardType: TextInputType.number,
                ),
                const SizedBox(height: 16),
                TextField(
                  controller: providerController,
                  decoration: InputDecoration(
                    labelText: 'Fornitore (opzionale)', // Add key
                    prefixIcon: Icon(Icons.business, color: theme.colorScheme.secondary),
                    labelStyle: TextStyle(color: theme.colorScheme.onSurface.withOpacity(0.7)),
                    border: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(12),
                    ),
                    enabledBorder: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(12),
                      borderSide: BorderSide(color: theme.colorScheme.outline),
                    ),
                  ),
                  style: TextStyle(color: theme.colorScheme.onSurface),
                ),
                const SizedBox(height: 16),
                DropdownButtonFormField<String>(
                  initialValue: category,
                  decoration: InputDecoration(
                    labelText: 'Categoria',
                    prefixIcon: Icon(Icons.category, color: theme.colorScheme.secondary),
                    labelStyle: TextStyle(color: theme.colorScheme.onSurface.withOpacity(0.7)),
                    border: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(12),
                    ),
                    enabledBorder: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(12),
                      borderSide: BorderSide(color: theme.colorScheme.outline),
                    ),
                  ),
                  dropdownColor: theme.cardColor,
                  style: TextStyle(color: theme.colorScheme.onSurface),
                  items: [
                    DropdownMenuItem(value: 'energy', child: Text('⚡ Energia', style: TextStyle(color: theme.colorScheme.onSurface))),
                    DropdownMenuItem(value: 'telco', child: Text('📱 Telefonia', style: TextStyle(color: theme.colorScheme.onSurface))),
                    DropdownMenuItem(value: 'subscription', child: Text('🎬 Abbonamenti', style: TextStyle(color: theme.colorScheme.onSurface))),
                    DropdownMenuItem(value: 'other', child: Text('📋 Altro', style: TextStyle(color: theme.colorScheme.onSurface))),
                  ],
                  onChanged: (value) {
                    if (value != null) setState(() => category = value);
                  },
                ),
              ],
            ),
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(context),
              child: Text(AppStrings.get('cancel')),
            ),
            ElevatedButton(
              onPressed: () async {
                final amount = double.tryParse(amountController.text);
                final dueDay = int.tryParse(dueDayController.text);
                if (amount == null || dueDay == null || nameController.text.isEmpty) {
                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(content: Text(AppStrings.get('fillAllFields'))),
                  );
                  return;
                }

                Navigator.pop(context);
                await _createBill(
                  context,
                  ref,
                  nameController.text,
                  amount,
                  dueDay,
                  category,
                  providerController.text.isEmpty ? null : providerController.text,
                );
              },
              style: ElevatedButton.styleFrom(
                backgroundColor: theme.colorScheme.primary,
                foregroundColor: theme.colorScheme.onPrimary,
              ),
              child: Text(AppStrings.get('add')),
            ),
          ],
        ),
      ),
    );
  }

  Future<void> _showEditBillDialog(
      BuildContext context, WidgetRef ref, Map<String, dynamic> bill) async {
    final nameController = TextEditingController(text: bill['name']);
    final amountController = TextEditingController(
      text: bill['amount'].toString(),
    );
    final dueDayController = TextEditingController(
      text: bill['due_day'].toString(),
    );
    final providerController = TextEditingController(text: bill['provider'] ?? '');
    String category = bill['category'];
    final theme = Theme.of(context);

    await showDialog(
      context: context,
      builder: (context) => StatefulBuilder(
        builder: (context, setState) => AlertDialog(
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
          backgroundColor: theme.cardColor,
          title: Row(
            children: [
              Container(
                padding: const EdgeInsets.all(8),
                decoration: BoxDecoration(
                  color: AppColors.primary.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: const Icon(Icons.edit, color: AppColors.primary),
              ),
              const SizedBox(width: 12),
              Text(AppStrings.get('editBill'), style: TextStyle(color: theme.colorScheme.onSurface)),
            ],
          ),
          content: SingleChildScrollView(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                TextField(
                  controller: nameController,
                  decoration: InputDecoration(
                    labelText: 'Nome',
                    prefixIcon: Icon(Icons.label_outline, color: theme.colorScheme.secondary),
                    labelStyle: TextStyle(color: theme.colorScheme.onSurface.withOpacity(0.7)),
                    border: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(12),
                    ),
                    enabledBorder: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(12),
                      borderSide: BorderSide(color: theme.colorScheme.outline),
                    ),
                  ),
                  style: TextStyle(color: theme.colorScheme.onSurface),
                ),
                const SizedBox(height: 16),
                TextField(
                  controller: amountController,
                  decoration: InputDecoration(
                    labelText: 'Importo (€)',
                    prefixIcon: Icon(Icons.euro, color: theme.colorScheme.secondary),
                    labelStyle: TextStyle(color: theme.colorScheme.onSurface.withOpacity(0.7)),
                    border: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(12),
                    ),
                    enabledBorder: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(12),
                      borderSide: BorderSide(color: theme.colorScheme.outline),
                    ),
                  ),
                  style: TextStyle(color: theme.colorScheme.onSurface),
                  keyboardType: TextInputType.number,
                ),
                const SizedBox(height: 16),
                TextField(
                  controller: dueDayController,
                  decoration: InputDecoration(
                    labelText: 'Giorno scadenza',
                    prefixIcon: Icon(Icons.calendar_today, color: theme.colorScheme.secondary),
                    labelStyle: TextStyle(color: theme.colorScheme.onSurface.withOpacity(0.7)),
                    border: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(12),
                    ),
                    enabledBorder: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(12),
                      borderSide: BorderSide(color: theme.colorScheme.outline),
                    ),
                  ),
                  style: TextStyle(color: theme.colorScheme.onSurface),
                  keyboardType: TextInputType.number,
                ),
                const SizedBox(height: 16),
                TextField(
                  controller: providerController,
                  decoration: InputDecoration(
                    labelText: 'Fornitore',
                    prefixIcon: Icon(Icons.business, color: theme.colorScheme.secondary),
                    labelStyle: TextStyle(color: theme.colorScheme.onSurface.withOpacity(0.7)),
                    border: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(12),
                    ),
                    enabledBorder: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(12),
                      borderSide: BorderSide(color: theme.colorScheme.outline),
                    ),
                  ),
                  style: TextStyle(color: theme.colorScheme.onSurface),
                ),
                const SizedBox(height: 16),
                DropdownButtonFormField<String>(
                  initialValue: category,
                  decoration: InputDecoration(
                    labelText: 'Categoria',
                    prefixIcon: Icon(Icons.category, color: theme.colorScheme.secondary),
                    labelStyle: TextStyle(color: theme.colorScheme.onSurface.withOpacity(0.7)),
                    border: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(12),
                    ),
                    enabledBorder: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(12),
                      borderSide: BorderSide(color: theme.colorScheme.outline),
                    ),
                  ),
                  dropdownColor: theme.cardColor,
                  style: TextStyle(color: theme.colorScheme.onSurface),
                  items: [
                    DropdownMenuItem(value: 'energy', child: Text('⚡ Energia', style: TextStyle(color: theme.colorScheme.onSurface))),
                    DropdownMenuItem(value: 'telco', child: Text('📱 Telefonia', style: TextStyle(color: theme.colorScheme.onSurface))),
                    DropdownMenuItem(value: 'subscription', child: Text('🎬 Abbonamenti', style: TextStyle(color: theme.colorScheme.onSurface))),
                    DropdownMenuItem(value: 'other', child: Text('📋 Altro', style: TextStyle(color: theme.colorScheme.onSurface))),
                  ],
                  onChanged: (value) {
                    if (value != null) setState(() => category = value);
                  },
                ),
              ],
            ),
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(context),
              child: const Text('Annulla'),
            ),
            ElevatedButton(
              onPressed: () async {
                final amount = double.tryParse(amountController.text);
                final dueDay = int.tryParse(dueDayController.text);
                if (amount == null || dueDay == null) return;

                Navigator.pop(context);
                await _updateBill(
                  context,
                  ref,
                  bill['id'],
                  nameController.text,
                  amount,
                  dueDay,
                  category,
                  providerController.text.isEmpty ? null : providerController.text,
                );
              },
              style: ElevatedButton.styleFrom(
                backgroundColor: theme.colorScheme.primary,
                foregroundColor: theme.colorScheme.onPrimary,
              ),
              child: const Text('Salva'),
            ),
          ],
        ),
      ),
    );
  }

  Future<void> _createBill(BuildContext context, WidgetRef ref, String name,
      double amount, int dueDay, String category, String? provider) async {
    try {
      final apiClient = ref.read(apiClientProvider);
      await apiClient.createBill(
        name: name,
        amount: amount,
        dueDay: dueDay,
        category: category,
        provider: provider,
      );
      ref.invalidate(billsProvider);
      ref.invalidate(dashboardDataProvider);
      if (context.mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Row(
              children: [
                const Icon(Icons.check_circle, color: Colors.white),
                const SizedBox(width: 12),
                Text('Bolletta "$name" aggiunta'),
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
      if (context.mounted) {
        final theme = Theme.of(context);
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Errore: $e'),
            backgroundColor: theme.colorScheme.error,
          ),
        );
      }
    }
  }

  Future<void> _updateBill(BuildContext context, WidgetRef ref, String billId,
      String name, double amount, int dueDay, String category, String? provider) async {
    try {
      final apiClient = ref.read(apiClientProvider);
      await apiClient.updateBill(billId, {
        'name': name,
        'amount': amount,
        'due_day': dueDay,
        'category': category,
        'provider': provider,
      });
      ref.invalidate(billsProvider);
      ref.invalidate(dashboardDataProvider);
      if (context.mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: const Row(
              children: [
                Icon(Icons.check_circle, color: Colors.white),
                SizedBox(width: 12),
                Text('Bolletta aggiornata'),
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
      if (context.mounted) {
        final theme = Theme.of(context);
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Errore: $e'), backgroundColor: theme.colorScheme.error),
        );
      }
    }
  }

  Future<void> _deleteBill(BuildContext context, WidgetRef ref, String id) async {
    final theme = Theme.of(context);
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
        backgroundColor: theme.cardColor,
        title: Row(
          children: [
            Icon(Icons.delete_outline, color: theme.colorScheme.error),
            const SizedBox(width: 12),
            Text('Elimina bolletta', style: TextStyle(color: theme.colorScheme.onSurface)),
          ],
        ),
        content: Text('Sei sicuro di voler eliminare questa bolletta?', style: TextStyle(color: theme.colorScheme.onSurface)),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context, false),
            child: const Text('Annulla'),
          ),
          ElevatedButton(
            onPressed: () => Navigator.pop(context, true),
            style: ElevatedButton.styleFrom(
              backgroundColor: theme.colorScheme.error,
              foregroundColor: theme.colorScheme.onError,
            ),
            child: const Text('Elimina'),
          ),
        ],
      ),
    );

    if (confirmed != true) return;

    try {
      final apiClient = ref.read(apiClientProvider);
      await apiClient.deleteBill(id);
      ref.invalidate(billsProvider);
      ref.invalidate(dashboardDataProvider);
      if (context.mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Bolletta eliminata'),
            backgroundColor: Colors.orange,
          ),
        );
      }
    } catch (e) {
      if (context.mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Errore: $e'), backgroundColor: theme.colorScheme.error),
        );
      }
    }
  }

  Future<void> _registerPayment(
      BuildContext context, WidgetRef ref, Map<String, dynamic> bill) async {
    final amount = (bill['amount'] is num)
        ? (bill['amount'] as num).toDouble()
        : double.tryParse(bill['amount'].toString()) ?? 0.0;

    try {
      final apiClient = ref.read(apiClientProvider);
      await apiClient.createTransaction(
        amount: amount,
        description: 'Pagamento ${bill['name']}',
        transactionType: 'expense',
      );
      ref.invalidate(billsProvider);
      ref.invalidate(dashboardDataProvider);
      ref.invalidate(transactionsProvider);
      if (context.mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Row(
              children: [
                const Icon(Icons.check_circle, color: Colors.white),
                const SizedBox(width: 12),
                Text('Pagamento di €${amount.toStringAsFixed(2)} registrato'),
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
      if (context.mounted) {
        final theme = Theme.of(context);
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Errore: $e'), backgroundColor: theme.colorScheme.error),
        );
      }
    }
  }
}

class _BillCard extends StatelessWidget {
  final Map<String, dynamic> bill;
  final VoidCallback onEdit;
  final VoidCallback onDelete;
  final VoidCallback onPayment;

  const _BillCard({
    required this.bill,
    required this.onEdit,
    required this.onDelete,
    required this.onPayment,
  });

  @override
  Widget build(BuildContext context) {
    final amount = (bill['amount'] is num)
        ? (bill['amount'] as num).toDouble()
        : double.tryParse(bill['amount'].toString()) ?? 0.0;

    final category = bill['category'] as String;
    final categoryIcon = _getCategoryIcon(category);
    final categoryColor = _getCategoryColor(category);
    final theme = Theme.of(context);

    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      decoration: BoxDecoration(
        color: theme.cardColor,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: categoryColor.withOpacity(0.2)),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.05),
            blurRadius: 10,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Column(
        children: [
          ListTile(
            contentPadding: const EdgeInsets.all(16),
            leading: Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: categoryColor.withOpacity(0.1),
                borderRadius: BorderRadius.circular(12),
              ),
              child: Icon(categoryIcon, color: categoryColor, size: 24),
            ),
            title: Text(
              bill['name'],
              style: TextStyle(
                fontWeight: FontWeight.w600,
                fontSize: 16,
                color: theme.colorScheme.onSurface,
              ),
            ),
            subtitle: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const SizedBox(height: 4),
                Text(
                  'Scadenza: ${bill['due_day']} del mese',
                  style: const TextStyle(fontSize: 13, color: AppColors.textSecondary),
                ),
                if (bill['provider'] != null)
                  Text(
                    bill['provider'],
                    style: const TextStyle(
                      fontSize: 12,
                      color: AppColors.textSecondary,
                      fontStyle: FontStyle.italic,
                    ),
                  ),
              ],
            ),
            trailing: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              crossAxisAlignment: CrossAxisAlignment.end,
              children: [
                Text(
                  '€${amount.toStringAsFixed(2)}',
                  style: TextStyle(
                    fontWeight: FontWeight.bold,
                    fontSize: 18,
                    color: categoryColor,
                  ),
                ),
                const Text(
                  '/mese',
                  style: TextStyle(
                    fontSize: 11,
                    color: AppColors.textSecondary,
                  ),
                ),
              ],
            ),
          ),
          Divider(height: 1, color: theme.colorScheme.outlineVariant),
          Padding(
            padding: const EdgeInsets.all(8),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceEvenly,
              children: [
                Expanded(
                  child: TextButton.icon(
                    onPressed: onPayment,
                    icon: const Icon(Icons.payment, size: 18),
                    label: const Text('Registra'),
                    style: TextButton.styleFrom(
                      foregroundColor: AppColors.success,
                    ),
                  ),
                ),
                Expanded(
                  child: TextButton.icon(
                    onPressed: onEdit,
                    icon: const Icon(Icons.edit_outlined, size: 18),
                    label: const Text('Modifica'),
                    style: TextButton.styleFrom(
                      foregroundColor: theme.colorScheme.primary,
                    ),
                  ),
                ),
                Expanded(
                  child: TextButton.icon(
                    onPressed: onDelete,
                    icon: const Icon(Icons.delete_outline, size: 18),
                    label: const Text('Elimina'),
                    style: TextButton.styleFrom(
                      foregroundColor: theme.colorScheme.error,
                    ),
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  IconData _getCategoryIcon(String category) {
    switch (category) {
      case 'energy':
        return Icons.bolt;
      case 'telco':
        return Icons.phone_android;
      case 'subscription':
        return Icons.subscriptions;
      default:
        return Icons.receipt;
    }
  }

  Color _getCategoryColor(String category) {
    switch (category) {
      case 'energy':
        return Colors.orange;
      case 'telco':
        return Colors.blue;
      case 'subscription':
        return Colors.purple;
      default:
        return AppColors.warning;
    }
  }
}
