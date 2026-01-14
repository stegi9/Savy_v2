import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:savy_frontend/features/bills/presentation/screens/bills_screen.dart';
import 'package:savy_frontend/core/providers/app_providers.dart';

void main() {
  final mockBills = [
    {
      'id': 'bill-1',
      'user_id': 'user-1',
      'name': 'Netflix',
      'amount': 15.99,
      'due_day': 15,
      'category': 'Entertainment',
      'provider': 'Netflix',
      'is_active': true,
      'created_at': '2024-01-01T00:00:00',
    },
    {
      'id': 'bill-2',
      'user_id': 'user-1',
      'name': 'Rent',
      'amount': 800.0,
      'due_day': 1,
      'category': 'Rent',
      'is_active': true,
      'created_at': '2024-01-01T00:00:00',
    }
  ];

  testWidgets('BillsScreen displays list of bills', skip: true, (WidgetTester tester) async {
    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          billsProvider.overrideWith((ref) => Future.value(mockBills)),
        ],
        child: const MaterialApp(
          home: BillsScreen(),
        ),
      ),
    );
    await tester.pumpAndSettle();

    expect(find.text('Bollette'), findsOneWidget);
    expect(find.text('Netflix'), findsOneWidget);
    expect(find.text('Rent'), findsOneWidget);
    expect(find.text('€15.99'), findsOneWidget);
    expect(find.text('€800.00'), findsOneWidget);
  });

  testWidgets('BillsScreen shows empty state', skip: true, (WidgetTester tester) async {
    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          billsProvider.overrideWith((ref) => Future.value([])),
        ],
        child: const MaterialApp(
          home: BillsScreen(),
        ),
      ),
    );
    await tester.pumpAndSettle();

    expect(find.text('Nessuna bolletta attiva'), findsOneWidget);
    expect(find.text('Aggiungi le tue spese ricorrenti'), findsOneWidget);
  });
}
