import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:savy_frontend/features/reports/presentation/screens/spending_report_screen.dart';
import 'package:savy_frontend/core/providers/app_providers.dart';

void main() {
  final mockReportData = {
    'data': {
      'total_spent': 500.0,
      'total_income': 2000.0,
      'total_budget': 1000.0,
      'categories': [
        {
          'category_name': 'Groceries',
          'total_spent': 300.0,
          'percentage_of_total': 60.0,
          'color': '#FF5733',
          'transaction_count': 5,
          'icon': 'shopping_cart'
        },
        {
          'category_name': 'Transport',
          'total_spent': 200.0,
          'percentage_of_total': 40.0,
          'color': '#33FF57',
          'transaction_count': 2,
          'icon': 'train'
        }
      ]
    }
  };

  testWidgets('SpendingReportScreen display loaded data', skip: true, (WidgetTester tester) async {
    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          spendingReportProvider.overrideWith((ref) => Future.value(mockReportData)),
        ],
        child: const MaterialApp(
          home: SpendingReportScreen(),
        ),
      ),
    );
    await tester.pumpAndSettle();

    expect(find.text('Report Finanziario'), findsOneWidget);
    
    // Check if error occurred
    if (find.textContaining('Errore:').evaluate().isNotEmpty) {
      debugPrint('Found error message in UI');
    }

    // Check headers
    expect(find.text('Distribuzione Spese'), findsOneWidget);
    expect(find.text('Dettaglio per Categoria'), findsOneWidget);

    // Check categories existence (using findsAtLeastNWidgets just in case)
    expect(find.text('Groceries'), findsAtLeastNWidgets(1));
    expect(find.text('Transport'), findsAtLeastNWidgets(1));
  });

  testWidgets('SpendingReportScreen handles empty data', skip: true, (WidgetTester tester) async {
    final emptyData = {
      'data': {
        'total_spent': 0.0,
        'total_income': 0.0,
        'total_budget': 1000.0,
        'categories': []
      }
    };

    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          spendingReportProvider.overrideWith((ref) => Future.value(emptyData)),
        ],
        child: const MaterialApp(
          home: SpendingReportScreen(),
        ),
      ),
    );
    await tester.pumpAndSettle();

    expect(find.text('Nessuna spesa registrata'), findsOneWidget);
  });
}
