import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:savy_frontend/features/transactions/presentation/screens/transactions_screen.dart';
import 'package:savy_frontend/core/providers/app_providers.dart';

void main() {
  final mockTransactions = [
    {
      'id': 'tx-123',
      'user_id': 'user-123',
      'amount': 50.0,
      'description': 'Supermarket',
      'category_id': 'cat-1',
      'category_name': 'Groceries',
      'transaction_type': 'expense',
      'date': '2024-01-01T10:00:00',
      'created_at': '2024-01-01T10:00:00',
      'needs_review': false,
    },
    {
      'id': 'tx-456',
      'user_id': 'user-123',
      'amount': 1200.0,
      'description': 'Monthly Salary',
      'category_id': 'cat-2',
      'category_name': 'Salary',
      'transaction_type': 'income',
      'date': '2024-01-02T10:00:00',
      'created_at': '2024-01-02T10:00:00',
      'needs_review': false,
    }
  ];

  testWidgets('TransactionsScreen displays list of transactions', skip: true, (WidgetTester tester) async {
    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          transactionsProvider.overrideWith((ref) => Future.value(mockTransactions)),
        ],
        child: const MaterialApp(
          home: TransactionsScreen(),
        ),
      ),
    );
    await tester.pumpAndSettle();

    expect(find.text('Transazioni'), findsOneWidget);
    expect(find.text('Supermarket'), findsOneWidget);
    expect(find.text('Salary'), findsOneWidget);
    expect(find.text('-€50.00'), findsOneWidget);
    expect(find.text('+€1200.00'), findsOneWidget);
  });

  testWidgets('TransactionsScreen shows empty state', skip: true, (WidgetTester tester) async {
    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          transactionsProvider.overrideWith((ref) => Future.value([])),
        ],
        child: const MaterialApp(
          home: TransactionsScreen(),
        ),
      ),
    );
    await tester.pumpAndSettle();

    expect(find.text('Nessuna transazione'), findsOneWidget);
    expect(find.text('Inizia ad aggiungere le tue transazioni'), findsOneWidget);
  });

  testWidgets('TransactionsScreen floating action button exists', skip: true, (WidgetTester tester) async {
    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          transactionsProvider.overrideWith((ref) => Future.value(mockTransactions)),
        ],
        child: const MaterialApp(
          home: TransactionsScreen(),
        ),
      ),
    );
    await tester.pumpAndSettle();

    expect(find.byType(FloatingActionButton), findsOneWidget);
    expect(find.text('Nuova'), findsOneWidget);
  });
}
