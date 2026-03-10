import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:intl/intl.dart';
import '../../../../core/theme/app_colors.dart';
import '../../../../core/providers/app_providers.dart';
import '../../../../core/l10n/app_strings.dart';
import '../../data/models/transaction_model.dart';
import '../../../../features/accounts/data/providers/account_provider.dart';

class TransactionsScreen extends ConsumerStatefulWidget {
  const TransactionsScreen({super.key});

  @override
  ConsumerState<TransactionsScreen> createState() => _TransactionsScreenState();
}

class _TransactionsScreenState extends ConsumerState<TransactionsScreen> {
  String _filter = 'all';

  @override
  Widget build(BuildContext context) {
    final transactionsAsync = ref.watch(transactionsProvider);
    final theme = Theme.of(context);

    return Scaffold(
      backgroundColor: theme.scaffoldBackgroundColor,
      appBar: AppBar(
        title: Text(AppStrings.get('actionTransaction')),
        backgroundColor: theme.colorScheme.primary,
        foregroundColor: theme.colorScheme.onPrimary,
        actions: [
          PopupMenuButton<String>(
            initialValue: _filter,
            icon: Icon(Icons.filter_list, color: theme.colorScheme.onPrimary),
            onSelected: (value) => setState(() => _filter = value),
            itemBuilder: (context) => [
              PopupMenuItem(value: 'all', child: Text(AppStrings.get('filterAll'))),
              PopupMenuItem(value: 'review', child: Text(AppStrings.get('filterReview'))),
              PopupMenuItem(value: 'income', child: Text(AppStrings.get('filterIncome'))),
              PopupMenuItem(value: 'expense', child: Text(AppStrings.get('filterExpense'))),
            ],
            color: theme.cardColor,
          ),
        ],
      ),
      body: Column(
        children: [
          _buildAccountFilter(context),
          Expanded(
            child: transactionsAsync.when(
              data: (transactions) {
                final List<TransactionModel> transactionModels =
                    transactions.map((t) => TransactionModel.fromJson(t)).toList();

                final filtered = transactionModels.where((t) {
                  if (_filter == 'review') return t.needsReview || t.categoryId == null;
                  if (_filter == 'income') return t.transactionType == 'income';
                  if (_filter == 'expense') return t.transactionType == 'expense';
                  return true;
                }).toList();

                if (filtered.isEmpty) {
                  return _buildEmptyState(theme);
                }

                return RefreshIndicator(
                  onRefresh: () async {
                    ref.invalidate(transactionsProvider);
                  },
                  child: ListView.builder(
                    padding: const EdgeInsets.all(16),
                    itemCount: filtered.length,
                    itemBuilder: (context, index) {
                      final transaction = filtered[index];
                      return _TransactionCard(
                        key: ValueKey('card_${transaction.id}'),
                        transaction: transaction,
                        onDelete: () async {
                          return await _deleteTransaction(transaction.id);
                        },
                        onEdit: () async {
                          await _showCategoryPicker(transaction);
                        },
                      );
                    },
                  ),
                );
              },
              loading: () => const Center(child: CircularProgressIndicator()),
              error: (e, s) => Center(child: Text('Errore: $e', style: TextStyle(color: theme.colorScheme.error))),
            ),
          ),
        ],
      ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: _showAddTransactionDialog,
        backgroundColor: theme.colorScheme.primary,
        icon: Icon(Icons.add, color: theme.colorScheme.onPrimary),
        label: Text(AppStrings.get('newButton'), style: TextStyle(color: theme.colorScheme.onPrimary)),
      ),
    );
  }

  Widget _buildAccountFilter(BuildContext context) {
    final theme = Theme.of(context);
    final accountsAsync = ref.watch(accountsProvider);
    final selectedAccountId = ref.watch(selectedAccountIdProvider);

    return accountsAsync.when(
      data: (accounts) {
        if (accounts.isEmpty) return const SizedBox.shrink();
        
        return Container(
          height: 56,
          decoration: BoxDecoration(
            color: theme.cardColor,
            border: Border(bottom: BorderSide(color: theme.dividerColor.withOpacity(0.1))),
          ),
          child: ListView(
            scrollDirection: Axis.horizontal,
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
            children: [
              Padding(
                padding: const EdgeInsets.only(right: 8),
                child: ChoiceChip(
                  label: const Text('Tutti i conti'),
                  selected: selectedAccountId == null,
                  onSelected: (selected) {
                    if (selected) {
                      ref.read(selectedAccountIdProvider.notifier).state = null;
                    }
                  },
                  selectedColor: theme.colorScheme.primaryContainer,
                  labelStyle: TextStyle(
                    color: selectedAccountId == null 
                        ? theme.colorScheme.onPrimaryContainer
                        : theme.colorScheme.onSurface,
                  ),
                ),
              ),
              ...accounts.map((account) {
                final isSelected = selectedAccountId == account.id;
                return Padding(
                  padding: const EdgeInsets.only(right: 8),
                  child: ChoiceChip(
                    label: Text(account.name ?? 'Conto'),
                    selected: isSelected,
                    onSelected: (selected) {
                      ref.read(selectedAccountIdProvider.notifier).state = 
                          selected ? account.id : null;
                    },
                    selectedColor: theme.colorScheme.primaryContainer,
                    labelStyle: TextStyle(
                      color: isSelected 
                          ? theme.colorScheme.onPrimaryContainer
                          : theme.colorScheme.onSurface,
                    ),
                  ),
                );
              }).toList(),
            ],
          ),
        );
      },
      loading: () => const SizedBox(height: 56, child: Center(child: CircularProgressIndicator())),
      error: (_, __) => const SizedBox.shrink(),
    );
  }

  Widget _buildEmptyState(ThemeData theme) {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Container(
            padding: const EdgeInsets.all(32),
            decoration: BoxDecoration(
              color: theme.colorScheme.primary.withOpacity(0.1),
              shape: BoxShape.circle,
            ),
            child: Icon(
              Icons.receipt_long_outlined,
              size: 64,
              color: theme.colorScheme.primary,
            ),
          ),
          const SizedBox(height: 24),
          Text(
            _filter == 'review' ? 'Tutto OK!' : AppStrings.get('noTransactions'),
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
              _filter == 'review'
                  ? 'Tutte le transazioni sono categorizzate correttamente'
                  : AppStrings.get('startAddingTransactions'),
              textAlign: TextAlign.center,
              style: const TextStyle(
                fontSize: 14,
                color: AppColors.textSecondary,
              ),
            ),
          ),
        ],
      ),
    );
  }

  Future<void> _showCategoryPicker(TransactionModel transaction) async {
    // Force refresh categories
    ref.invalidate(categoriesProvider);
    final categoriesAsync = await ref.read(categoriesProvider.future);
    final theme = Theme.of(context);

    // Filter categories by transaction type
    final filteredCategories = categoriesAsync.where((cat) {
      final catType = cat['category_type'] as String? ?? 'expense';
      return catType == transaction.transactionType;
    }).toList();

    if (filteredCategories.isEmpty) {
      if (!mounted) return;
      showDialog(
        context: context,
        builder: (context) => AlertDialog(
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
          backgroundColor: theme.cardColor,
          title: Row(
            children: [
              const Icon(Icons.warning_amber_rounded, color: AppColors.warning),
              const SizedBox(width: 12),
              Text('Nessuna categoria ${transaction.transactionType == "income" ? "entrata" : "uscita"}', 
                   style: TextStyle(color: theme.colorScheme.onSurface)),
            ],
          ),
          content: Text(
            'Crea prima delle categorie di tipo ${transaction.transactionType == "income" ? "entrata" : "uscita"} per poter categorizzare questa transazione.',
            style: TextStyle(color: theme.colorScheme.onSurface),
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(context),
              child: const Text('Annulla'),
            ),
            ElevatedButton(
              onPressed: () {
                Navigator.pop(context);
                context.push('/categories');
              },
              child: const Text('Crea categorie'),
            ),
          ],
        ),
      );
      return;
    }

    if (!mounted) return;
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
        backgroundColor: theme.cardColor,
        title: Row(
          children: [
            Container(
              padding: const EdgeInsets.all(8),
              decoration: BoxDecoration(
                color: theme.colorScheme.primary.withOpacity(0.1),
                borderRadius: BorderRadius.circular(8),
              ),
              child: Icon(Icons.category, color: theme.colorScheme.primary),
            ),
            const SizedBox(width: 12),
            Expanded(child: Text('Seleziona categoria ${transaction.transactionType == "income" ? "entrata" : "uscita"}',
               style: TextStyle(color: theme.colorScheme.onSurface))),
          ],
        ),
        content: SizedBox(
          width: double.maxFinite,
          child: ListView.builder(
            shrinkWrap: true,
            itemCount: filteredCategories.length,
            itemBuilder: (context, index) {
              final cat = filteredCategories[index];
              final color = _hexToColor(cat['color'] as String? ?? '#3B82F6');
              
              return Container(
                margin: const EdgeInsets.only(bottom: 8),
                decoration: BoxDecoration(
                  color: theme.scaffoldBackgroundColor,
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(color: color.withOpacity(0.2)),
                ),
                child: ListTile(
                  leading: Container(
                    padding: const EdgeInsets.all(8),
                    decoration: BoxDecoration(
                      color: color.withOpacity(0.1),
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: Icon(_getIconData(cat['icon']), color: color, size: 20),
                  ),
                  title: Text(
                    cat['name'],
                    style: TextStyle(fontWeight: FontWeight.w600, color: theme.colorScheme.onSurface),
                  ),
                  trailing: const Icon(Icons.chevron_right, color: AppColors.textSecondary),
                  onTap: () async {
                    Navigator.pop(context);
                    await _updateCategory(transaction.id, cat['id']);
                  },
                ),
              );
            },
          ),
        ),
      ),
    );
  }

  Future<void> _updateCategory(String transactionId, String categoryId) async {
    try {
      final apiClient = ref.read(apiClientProvider);
      await apiClient.updateTransactionCategory(transactionId, categoryId);
      ref.invalidate(transactionsProvider);
      ref.invalidate(dashboardDataProvider);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: const Row(
              children: [
                Icon(Icons.check_circle, color: Colors.white),
                SizedBox(width: 12),
                Text('Categoria aggiornata'),
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

  Future<bool> _deleteTransaction(String id) async {
    try {
      final apiClient = ref.read(apiClientProvider);
      await apiClient.deleteTransaction(id);
      ref.invalidate(transactionsProvider);
      ref.invalidate(dashboardDataProvider);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(AppStrings.get('transactionDeleted') != 'transactionDeleted' ? AppStrings.get('transactionDeleted') : 'Transazione eliminata'),
            backgroundColor: AppColors.success,
          ),
        );
      }
      return true;
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('${AppStrings.get('error')}: $e'), 
            backgroundColor: Theme.of(context).colorScheme.error
          ),
        );
      }
      return false;
    }
  }

  Future<void> _showAddTransactionDialog() async {
    final amountController = TextEditingController();
    final descController = TextEditingController();
    String transactionType = 'expense';
    String? selectedAccountId;
    final theme = Theme.of(context);
    final accountsState = ref.read(accountsProvider);
    
    // Default select the first account if available
    if (selectedAccountId == null && accountsState is AsyncData && accountsState.value!.isNotEmpty) {
      selectedAccountId = accountsState.value!.first.id;
    }

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
                  gradient: LinearGradient(
                    colors: [theme.colorScheme.primary, AppColors.primaryDark],
                  ),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Icon(Icons.add, color: theme.colorScheme.onPrimary),
              ),
              const SizedBox(width: 12),
              Text(AppStrings.get('newTransaction'), style: TextStyle(color: theme.colorScheme.onSurface)),
            ],
          ),
          content: SingleChildScrollView(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                SegmentedButton<String>(
                  style: ButtonStyle(
                    backgroundColor: WidgetStateProperty.resolveWith<Color>(
                      (Set<WidgetState> states) {
                        if (states.contains(WidgetState.selected)) {
                          return transactionType == 'income'
                              ? AppColors.success.withOpacity(0.2)
                              : theme.colorScheme.error.withOpacity(0.2);
                        }
                        return Colors.transparent;
                      },
                    ),
                    foregroundColor: WidgetStateProperty.resolveWith<Color>(
                      (Set<WidgetState> states) {
                        if (states.contains(WidgetState.selected)) {
                          return transactionType == 'income'
                              ? AppColors.success
                              : theme.colorScheme.error;
                        }
                        return theme.colorScheme.onSurface;
                      },
                    ),
                  ),
                  segments: [
                    ButtonSegment(
                      value: 'expense',
                      label: Text(AppStrings.get('expense')),
                      icon: const Icon(Icons.arrow_upward),
                    ),
                    ButtonSegment(
                      value: 'income',
                      label: Text(AppStrings.get('income')),
                      icon: const Icon(Icons.arrow_downward),
                    ),
                  ],
                  selected: {transactionType},
                  onSelectionChanged: (Set<String> newSelection) {
                    setState(() => transactionType = newSelection.first);
                  },
                ),
                const SizedBox(height: 16),
                if (accountsState is AsyncData && accountsState.value!.isNotEmpty)
                  DropdownButtonFormField<String>(
                    value: selectedAccountId,
                    decoration: InputDecoration(
                      labelText: 'Seleziona Conto',
                      prefixIcon: Icon(Icons.account_balance_wallet, color: theme.colorScheme.primary),
                      border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
                    ),
                    items: accountsState.value!.map((acc) => DropdownMenuItem(
                      value: acc.id,
                      child: Text(acc.name ?? 'Conto Sconosciuto'),
                    )).toList(),
                    onChanged: (v) => setState(() => selectedAccountId = v),
                  ),
                const SizedBox(height: 20),
                TextField(
                  controller: amountController,
                  decoration: InputDecoration(
                    labelText: '${AppStrings.get('amount')} (€)',
                    prefixIcon: Icon(Icons.euro, color: theme.colorScheme.primary),
                    labelStyle: TextStyle(color: theme.colorScheme.onSurface.withOpacity(0.7)),
                    border: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(12),
                    ),
                    enabledBorder: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(12),
                      borderSide: BorderSide(color: theme.colorScheme.outline),
                    ),
                  ),
                  keyboardType: TextInputType.number,
                  autofocus: true,
                  style: TextStyle(color: theme.colorScheme.onSurface),
                ),
                const SizedBox(height: 16),
                TextField(
                  controller: descController,
                  decoration: InputDecoration(
                    labelText: AppStrings.get('description'),
                    prefixIcon: Icon(Icons.description_outlined, color: theme.colorScheme.primary),
                    labelStyle: TextStyle(color: theme.colorScheme.onSurface.withOpacity(0.7)),
                    border: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(12),
                    ),
                    enabledBorder: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(12),
                      borderSide: BorderSide(color: theme.colorScheme.outline),
                    ),
                  ),
                  textCapitalization: TextCapitalization.sentences,
                  style: TextStyle(color: theme.colorScheme.onSurface),
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
                if (amount == null || descController.text.isEmpty) {
                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(content: Text(AppStrings.get('fillAllFields'))),
                  );
                  return;
                }

                Navigator.pop(context);
                await _createTransaction(
                  amount,
                  descController.text,
                  transactionType,
                  selectedAccountId,
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

  Future<void> _createTransaction(
      double amount, String description, String type, String? bankAccountId) async {
    // Force refresh and wait for categories
    ref.invalidate(categoriesProvider);
    final categories = await ref.read(categoriesProvider.future);
    final theme = Theme.of(context);
    
    final hasMatchingCategories = categories.any((cat) => 
      (cat['category_type'] as String? ?? 'expense') == type
    );
    
    if (!hasMatchingCategories) {
      // Show warning but still allow creation
      if (mounted) {
        final proceed = await showDialog<bool>(
          context: context,
          builder: (context) => AlertDialog(
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
            backgroundColor: theme.cardColor,
            title: Row(
              children: [
                const Icon(Icons.warning_amber_rounded, color: AppColors.warning),
                const SizedBox(width: 12),
                Expanded(
                  child: Text(
                    'Nessuna categoria ${type == "income" ? "entrata" : "uscita"}',
                    style: TextStyle(fontSize: 18, color: theme.colorScheme.onSurface),
                  ),
                ),
              ],
            ),
            content: Text(
              'Non hai categorie di tipo "${type == "income" ? "entrata" : "uscita"}". '
              'La transazione verrà salvata come "da categorizzare".\n\n'
              'Vuoi creare prima una categoria?',
              style: TextStyle(color: theme.colorScheme.onSurface),
            ),
            actions: [
              TextButton(
                onPressed: () => Navigator.pop(context, false),
                child: const Text('Annulla'),
              ),
              OutlinedButton(
                onPressed: () {
                  Navigator.pop(context, null); // null = go to categories
                },
                child: const Text('Crea categoria'),
              ),
              ElevatedButton(
                onPressed: () => Navigator.pop(context, true),
                style: ElevatedButton.styleFrom(
                  backgroundColor: theme.colorScheme.primary,
                  foregroundColor: theme.colorScheme.onPrimary,
                ),
                child: const Text('Continua'),
              ),
            ],
          ),
        );
        
        if (proceed == null) {
          // User wants to create category first
          context.push('/categories');
          return;
        }
        if (proceed != true) {
          return; // User cancelled
        }
      }
    }
    
    try {
      final apiClient = ref.read(apiClientProvider);
      await apiClient.createTransaction(
        amount: amount,
        description: description,
        transactionType: type,
        bankAccountId: bankAccountId,
      );
      ref.invalidate(transactionsProvider);
      ref.invalidate(dashboardDataProvider);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Row(
              children: [
                const Icon(Icons.check_circle, color: Colors.white),
                const SizedBox(width: 12),
                Text('${type == 'income' ? 'Entrata' : 'Spesa'} aggiunta'),
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
            backgroundColor: theme.colorScheme.error,
          ),
        );
      }
    }
  }

}

Color _hexToColor(String hex) {
  final hexCode = hex.replaceAll('#', '');
  try {
    return Color(int.parse('FF$hexCode', radix: 16));
  } catch (e) {
    return Colors.grey;
  }
}

IconData _getIconData(String? iconName) {
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

class _TransactionCard extends StatelessWidget {
  final TransactionModel transaction;
  final Future<bool> Function() onDelete;
  final VoidCallback onEdit;

  const _TransactionCard({
    super.key,
    required this.transaction,
    required this.onDelete,
    required this.onEdit,
  });

  @override
  Widget build(BuildContext context) {
    final isIncome = transaction.transactionType == 'income';
    final needsReview = transaction.needsReview || transaction.categoryId == null;
    final theme = Theme.of(context);

    return Dismissible(
      key: ValueKey('tx_${transaction.id}'),
      direction: DismissDirection.endToStart,
      background: Container(
        alignment: Alignment.centerRight,
        padding: const EdgeInsets.only(right: 20),
        decoration: BoxDecoration(
          color: theme.colorScheme.error,
          borderRadius: BorderRadius.circular(16),
        ),
        child: Icon(Icons.delete_outline, color: theme.colorScheme.onError, size: 28),
      ),
      confirmDismiss: (direction) async {
        final confirmed = await showDialog<bool>(
          context: context,
          builder: (context) => AlertDialog(
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
            backgroundColor: theme.cardColor,
            title: Row(
              children: [
                Icon(Icons.delete_outline, color: theme.colorScheme.error),
                const SizedBox(width: 12),
                Expanded(child: Text(AppStrings.get('deleteTransactionTitle'), style: TextStyle(color: theme.colorScheme.onSurface))),
              ],
            ),
            content: Text(AppStrings.get('deleteTransactionConfirm'), 
                          style: TextStyle(color: theme.colorScheme.onSurface)),
            actions: [
              TextButton(
                onPressed: () => Navigator.pop(context, false),
                child: Text(AppStrings.get('cancel')),
              ),
              ElevatedButton(
                onPressed: () => Navigator.pop(context, true),
                style: ElevatedButton.styleFrom(
                  backgroundColor: theme.colorScheme.error,
                  foregroundColor: theme.colorScheme.onError,
                ),
                child: Text(AppStrings.get('delete')),
              ),
            ],
          ),
        );

        if (confirmed == true) {
          // Perform delete operation while item is still there
          // If successful, return true to animate away
          return await onDelete(); 
        }
        return false;
      },
      onDismissed: (_) {
         // Logic is handled in confirmDismiss, but we need this callback for Dismissible
      },
      child: Container(
        margin: const EdgeInsets.only(bottom: 12),
        decoration: BoxDecoration(
          color: theme.cardColor,
          borderRadius: BorderRadius.circular(16),
          border: needsReview
              ? Border.all(color: AppColors.warning.withOpacity(0.5), width: 2)
              : null,
          boxShadow: [
            BoxShadow(
              color: Colors.black.withOpacity(0.05),
              blurRadius: 10,
              offset: const Offset(0, 2),
            ),
          ],
        ),
        child: ListTile(
          contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
          leading: Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: transaction.categoryColor != null
                  ? _hexToColor(transaction.categoryColor!).withOpacity(0.1)
                  : (isIncome
                      ? AppColors.success.withOpacity(0.1)
                      : theme.colorScheme.error.withOpacity(0.1)),
              borderRadius: BorderRadius.circular(12),
            ),
            child: Icon(
              transaction.categoryIcon != null
                  ? _getIconData(transaction.categoryIcon)
                  : (isIncome ? Icons.arrow_downward : Icons.arrow_upward),
              color: transaction.categoryColor != null
                  ? _hexToColor(transaction.categoryColor!)
                  : (isIncome ? AppColors.success : theme.colorScheme.error),
              size: 24,
            ),
          ),
          title: Text(
            transaction.description,
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
                DateFormat('dd/MM/yyyy').format(transaction.transactionDate),
                style: const TextStyle(fontSize: 12, color: AppColors.textSecondary),
              ),
              if (needsReview)
                Container(
                  margin: const EdgeInsets.only(top: 6),
                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                  decoration: BoxDecoration(
                    color: AppColors.warning.withOpacity(0.1),
                    borderRadius: BorderRadius.circular(6),
                  ),
                  child: const Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Icon(Icons.warning_amber_rounded, size: 14, color: AppColors.warning),
                      SizedBox(width: 4),
                      Text(
                        'Da categorizzare',
                        style: TextStyle(
                          fontSize: 11,
                          color: AppColors.warning,
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                    ],
                  ),
                )
              else if (transaction.categoryName != null)
                Container(
                  margin: const EdgeInsets.only(top: 6),
                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                  decoration: BoxDecoration(
                    color: isIncome ? AppColors.success.withOpacity(0.1) : theme.colorScheme.primary.withOpacity(0.1),
                    borderRadius: BorderRadius.circular(6),
                  ),
                  child: Text(
                    transaction.categoryName!,
                    style: TextStyle(
                      fontSize: 11,
                      color: isIncome ? AppColors.success : theme.colorScheme.primary,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                ),
            ],
          ),
          trailing: Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              Text(
                '${isIncome ? '+' : '-'}€${transaction.amount.toStringAsFixed(2)}',
                style: TextStyle(
                  fontWeight: FontWeight.bold,
                  fontSize: 18,
                  color: isIncome ? AppColors.success : theme.colorScheme.error,
                ),
              ),
              if (needsReview) ...[
                const SizedBox(width: 8),
                IconButton(
                  icon: const Icon(Icons.edit_outlined, size: 20, color: AppColors.warning),
                  onPressed: onEdit,
                  style: IconButton.styleFrom(
                    backgroundColor: AppColors.warning.withOpacity(0.1),
                    padding: const EdgeInsets.all(8),
                  ),
                ),
              ],
            ],
          ),
        ),
      ),
    );
  }
}
