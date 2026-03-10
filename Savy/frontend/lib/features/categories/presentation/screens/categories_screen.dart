import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../../core/theme/app_colors.dart';
import '../../../../core/providers/app_providers.dart';
import '../../../../core/l10n/app_strings.dart';
import 'package:dio/dio.dart';

class CategoriesScreen extends ConsumerWidget {
  const CategoriesScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final categoriesAsync = ref.watch(categoriesProvider);
    final theme = Theme.of(context);

    return Scaffold(
      backgroundColor: theme.scaffoldBackgroundColor,
      appBar: AppBar(
        title: Text(AppStrings.get('actionCategories')),
        backgroundColor: theme.colorScheme.primary,
        foregroundColor: theme.colorScheme.onPrimary,
      ),
      body: categoriesAsync.when(
        data: (categories) {
          if (categories.isEmpty) {
            return _buildEmptyState(context, ref, theme);
          }

          // Extract used colors (handle null values)
          final usedColors = categories
              .map((c) => c['color'] as String?)
              .where((c) => c != null)
              .cast<String>()
              .map((c) => c.toUpperCase())
              .toSet();

          return ListView.builder(
            padding: const EdgeInsets.only(left: 16, right: 16, top: 16, bottom: 88),
            itemCount: categories.length,
            itemBuilder: (context, index) {
              final cat = categories[index];
              return _CategoryCard(
                category: cat,
                onDelete: () => _deleteCategory(context, ref, cat['id']),
              );
            },
          );
        },
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (e, s) => Center(child: Text('${AppStrings.get('error')}: $e', style: TextStyle(color: theme.colorScheme.error))),
      ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: () => _showAddCategoryDialog(context, ref),
        backgroundColor: theme.colorScheme.primary,
        icon: Icon(Icons.add, color: theme.colorScheme.onPrimary),
        label: Text(AppStrings.get('newCategory'), style: TextStyle(color: theme.colorScheme.onPrimary)),
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
              color: theme.colorScheme.primary.withOpacity(0.1),
              shape: BoxShape.circle,
            ),
            child: Icon(
              Icons.category_outlined,
              size: 64,
              color: theme.colorScheme.primary,
            ),
          ),
          const SizedBox(height: 24),
          Text(
            AppStrings.get('noCategories'),
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
              AppStrings.get('addCategoryPrompt'),
              textAlign: TextAlign.center,
              style: const TextStyle(
                fontSize: 14,
                color: AppColors.textSecondary,
              ),
            ),
          ),
          const SizedBox(height: 32),
          ElevatedButton.icon(
            onPressed: () => _showAddCategoryDialog(context, ref),
            icon: const Icon(Icons.add),
            label: Text(AppStrings.get('newCategory')), // Assuming newCategory fits here too or use a generic 'Add'
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

  Future<void> _showAddCategoryDialog(BuildContext context, WidgetRef ref) async {
    final categoriesAsync = ref.read(categoriesProvider);
    final existingCategories = categoriesAsync.whenOrNull(data: (data) => data) ?? [];
    final theme = Theme.of(context);
    
    final usedColors = existingCategories
        .map((c) => c['color'] as String?)
        .where((c) => c != null)
        .cast<String>()
        .map((c) => c.toUpperCase())
        .toSet();

    final nameController = TextEditingController();
    final budgetController = TextEditingController();
    String selectedIcon = 'shopping_cart';
    String? selectedColor;
    String categoryType = 'expense'; // Default expense

    // Find first available color
    for (final color in AppColors.categoryColors) {
      final hexColor = '#${color.value.toRadixString(16).substring(2).toUpperCase()}';
      if (!usedColors.contains(hexColor)) {
        selectedColor = hexColor;
        break;
      }
    }

    await showDialog(
      context: context,
      builder: (dialogContext) => StatefulBuilder(
        builder: (context, setState) => AlertDialog(
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
              Text(AppStrings.get('newCategory'), style: TextStyle(color: theme.colorScheme.onSurface)),
            ],
          ),
          content: SingleChildScrollView(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Category Type Selection
                Text(
                  AppStrings.get('type'),
                  style: const TextStyle(
                    fontSize: 14,
                    fontWeight: FontWeight.w600,
                    color: AppColors.textSecondary,
                  ),
                ),
                const SizedBox(height: 12),
                SegmentedButton<String>(
                  style: ButtonStyle(
                    backgroundColor: WidgetStateProperty.resolveWith<Color>(
                      (Set<WidgetState> states) {
                        if (states.contains(WidgetState.selected)) {
                          return categoryType == 'income'
                              ? AppColors.success.withOpacity(0.2)
                              : theme.colorScheme.error.withOpacity(0.2);
                        }
                        return Colors.transparent;
                      },
                    ),
                    foregroundColor: WidgetStateProperty.resolveWith<Color>(
                      (Set<WidgetState> states) {
                        if (states.contains(WidgetState.selected)) {
                          return categoryType == 'income'
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
                  selected: {categoryType},
                  onSelectionChanged: (Set<String> newSelection) {
                    setState(() => categoryType = newSelection.first);
                  },
                ),
                const SizedBox(height: 20),
                TextField(
                  controller: nameController,
                  decoration: InputDecoration(
                    labelText: AppStrings.get('nameLabel'),
                    prefixIcon: Icon(Icons.label_outline, color: theme.colorScheme.primary),
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
                  controller: budgetController,
                  decoration: InputDecoration(
                    labelText: AppStrings.get('budgetLabel'),
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
                  style: TextStyle(color: theme.colorScheme.onSurface),
                  keyboardType: TextInputType.number,
                ),
                const SizedBox(height: 20),
                const SizedBox(height: 20),
                Text(
                  AppStrings.get('selectIcon'),
                  style: const TextStyle(
                    fontSize: 14,
                    fontWeight: FontWeight.w600,
                    color: AppColors.textSecondary,
                  ),
                ),
                const SizedBox(height: 12),
                Wrap(
                  spacing: 16,
                  runSpacing: 16,
                  children: [
                    'shopping_cart',
                    'restaurant',
                    'local_gas_station',
                    'home',
                    'shopping_bag',
                    'fitness_center',
                    'flight',
                    'hotel',
                    'local_cafe',
                    'movie'
                  ].map((iconName) {
                    final isSelected = selectedIcon == iconName;
                    return InkWell(
                      onTap: () => setState(() => selectedIcon = iconName),
                      borderRadius: BorderRadius.circular(12),
                      child: Container(
                        padding: const EdgeInsets.all(10),
                        decoration: BoxDecoration(
                          color: isSelected ? theme.colorScheme.primary : theme.cardColor,
                          borderRadius: BorderRadius.circular(12),
                          border: Border.all(
                            color: isSelected ? theme.colorScheme.primary : theme.colorScheme.outline,
                          ),
                        ),
                        child: Icon(
                          _getIconData(iconName),
                          color: isSelected ? theme.colorScheme.onPrimary : theme.colorScheme.onSurface,
                          size: 24,
                        ),
                      ),
                    );
                  }).toList(),
                ),
                const SizedBox(height: 24),
                Text(
                  AppStrings.get('selectColor'),
                  style: const TextStyle(
                    fontSize: 14,
                    fontWeight: FontWeight.w600,
                    color: AppColors.textSecondary,
                  ),
                ),
                const SizedBox(height: 12),
                Wrap(
                  spacing: 12,
                  runSpacing: 12,
                  children: AppColors.categoryColors.map((color) {
                    final colorHex = '#${color.value.toRadixString(16).substring(2).toUpperCase()}';
                    final isUsed = usedColors.contains(colorHex);
                    final isSelected = selectedColor == colorHex;

                    return InkWell(
                      onTap: isUsed ? null : () => setState(() => selectedColor = colorHex),
                      borderRadius: BorderRadius.circular(20),
                      child: Opacity(
                        opacity: isUsed ? 0.3 : 1.0,
                        child: Container(
                          width: 40,
                          height: 40,
                          decoration: BoxDecoration(
                            color: color,
                            shape: BoxShape.circle,
                            border: Border.all(
                              color: isSelected ? theme.colorScheme.onSurface : Colors.transparent,
                              width: isSelected ? 2 : 0,
                            ),
                            boxShadow: [
                              if (isSelected)
                                BoxShadow(
                                  color: color.withOpacity(0.4),
                                  blurRadius: 8,
                                  spreadRadius: 2,
                                )
                            ],
                          ),
                          child: isSelected
                              ? const Icon(Icons.check, color: Colors.white, size: 20)
                              : (isUsed 
                                  ? const Icon(Icons.lock, color: Colors.white, size: 20) 
                                  : null),
                        ),
                      ),
                    );
                  }).toList()
                    ..add(
                      InkWell(
                        onTap: () async {
                          final customHex = await _showCustomColorPicker(context, theme, usedColors);
                          if (customHex != null) {
                            setState(() => selectedColor = customHex);
                          }
                        },
                        borderRadius: BorderRadius.circular(20),
                        child: Container(
                          width: 40,
                          height: 40,
                          decoration: BoxDecoration(
                            color: theme.cardColor,
                            shape: BoxShape.circle,
                            border: Border.all(color: theme.colorScheme.outline),
                          ),
                          child: Icon(Icons.palette_outlined, color: theme.colorScheme.onSurface, size: 20),
                        ),
                      ),
                    ),
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
              onPressed: selectedColor == null
                  ? null
                  : () async {
                      if (nameController.text.isEmpty) {
                        ScaffoldMessenger.of(context).showSnackBar(
                          SnackBar(content: Text(AppStrings.get('fillAllFields'))),
                        );
                        return;
                      }
                      final budget = double.tryParse(budgetController.text) ?? 0.0;

                      Navigator.pop(context);
                      await _createCategory(
                        context,
                        ref,
                        nameController.text,
                        selectedIcon,
                        budget,
                        selectedColor!,
                        categoryType,
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

  Future<void> _createCategory(BuildContext context, WidgetRef ref,
      String name, String icon, double budget, String color, String categoryType) async {
    try {
      final apiClient = ref.read(apiClientProvider);
      await apiClient.createCategory(
        name: name,
        icon: icon,
        budgetMonthly: budget,
        color: color,
        categoryType: categoryType,
      );
      ref.invalidate(categoriesProvider);
      if (context.mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Categoria "$name" creata'),
            backgroundColor: AppColors.success,
            behavior: SnackBarBehavior.floating,
          ),
        );
      }
    } catch (e) {
      if (context.mounted) {
        final theme = Theme.of(context);
        String errorMsg = e.toString();
        
        if (e is DioException && e.response?.data != null) {
          final data = e.response!.data;
          if (data is Map && data['detail'] != null) {
            errorMsg = data['detail'];
          }
        }
        
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Errore: $errorMsg'),
            backgroundColor: theme.colorScheme.error,
          ),
        );
      }
    }
  }

  Future<String?> _showCustomColorPicker(BuildContext context, ThemeData theme, Set<String> usedColors) async {
    final hexController = TextEditingController(text: '#');
    String? errorMessage;
    
    return showDialog<String>(
      context: context,
      builder: (context) => StatefulBuilder(
        builder: (context, setState) => AlertDialog(
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
          backgroundColor: theme.cardColor,
          title: Text('Colore Personalizzato', style: TextStyle(color: theme.colorScheme.onSurface)),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              TextField(
                controller: hexController,
                style: TextStyle(color: theme.colorScheme.onSurface),
                decoration: InputDecoration(
                  labelText: 'Codice HEX (es. #FF0000)',
                  errorText: errorMessage,
                  border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
                ),
                onChanged: (val) {
                  if (errorMessage != null) {
                    setState(() => errorMessage = null);
                  }
                },
              ),
            ],
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(context),
              child: const Text('Annulla'),
            ),
            ElevatedButton(
              onPressed: () {
                String hex = hexController.text.trim().toUpperCase();
                if (!hex.startsWith('#')) hex = '#$hex';
                if (!RegExp(r'^#[0-9A-F]{6}$').hasMatch(hex)) {
                  setState(() => errorMessage = 'Formato non valido');
                  return;
                }
                if (usedColors.contains(hex)) {
                  setState(() => errorMessage = 'Colore già in uso');
                  return;
                }
                Navigator.pop(context, hex);
              },
              child: const Text('Conferma'),
            ),
          ],
        ),
      ),
    );
  }

  Future<void> _deleteCategory(
      BuildContext context, WidgetRef ref, String id) async {
    final theme = Theme.of(context);
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
        backgroundColor: theme.cardColor,
        title: Row(
          children: [
            const Icon(Icons.warning_amber_rounded, color: AppColors.warning),
            const SizedBox(width: 12),
            Text('Elimina categoria', style: TextStyle(color: theme.colorScheme.onSurface)),
          ],
        ),
        content: Text(
          'Sei sicuro di voler eliminare questa categoria? Le transazioni associate non saranno eliminate.',
          style: TextStyle(color: theme.colorScheme.onSurface),
        ),
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
      await apiClient.deleteCategory(id);
      ref.invalidate(categoriesProvider);
      if (context.mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Categoria eliminata'),
            backgroundColor: Colors.orange,
          ),
        );
      }
    } catch (e) {
      if (context.mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Errore: $e')),
        );
      }
    }
  }
}

class _CategoryCard extends StatelessWidget {
  final Map<String, dynamic> category;
  final VoidCallback onDelete;

  const _CategoryCard({
    required this.category,
    required this.onDelete,
  });

  @override
  Widget build(BuildContext context) {
    final colorHex = category['color']?.toString() ?? '#3B82F6';
    final color = _hexToColor(colorHex);
    final theme = Theme.of(context);
    final name = category['name']?.toString() ?? 'Categoria';
    final icon = category['icon']?.toString() ?? 'category';
    final isIncome = (category['category_type']?.toString() ?? 'expense') == 'income';
    final budget = category['budget_monthly'] ?? 0;
    
    return Container(
      margin: const EdgeInsets.only(bottom: 12),
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
      child: ListTile(
        contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
        leading: Container(
          padding: const EdgeInsets.all(12),
          decoration: BoxDecoration(
            color: color.withOpacity(0.1),
            borderRadius: BorderRadius.circular(12),
            border: Border.all(color: color.withOpacity(0.2)),
          ),
          child: Icon(_getIconData(icon), color: color, size: 24),
        ),
        title: Row(
          children: [
            Expanded(
              child: Text(
                name,
                style: TextStyle(
                  fontWeight: FontWeight.w600,
                  fontSize: 16,
                  color: theme.colorScheme.onSurface,
                ),
              ),
            ),
            if (isIncome)
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                decoration: BoxDecoration(
                  color: AppColors.success.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(4),
                ),
                child: const Text('Entrata', style: TextStyle(fontSize: 10, color: AppColors.success)),
              )
            else
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                decoration: BoxDecoration(
                  color: theme.colorScheme.error.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(4),
                ),
                child: Text('Spesa', style: TextStyle(fontSize: 10, color: theme.colorScheme.error)),
              ),
          ],
        ),
        subtitle: Text(
          isIncome ? 'Entrata stimata: €$budget' : 'Budget: €$budget',
          style: const TextStyle(
            fontSize: 14,
            color: AppColors.textSecondary,
          ),
        ),
        trailing: IconButton(
          icon: Icon(Icons.delete_outline, color: theme.colorScheme.error),
          onPressed: onDelete,
        ),
      ),
    );
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
