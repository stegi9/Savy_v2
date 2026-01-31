import 'package:flutter_test/flutter_test.dart';
import 'package:integration_test/integration_test.dart';
import 'package:savy_frontend/main.dart' as app;

/// End-to-End integration tests for critical user flows.
/// Run with: flutter test integration_test/app_test.dart
void main() {
  IntegrationTestWidgetsFlutterBinding.ensureInitialized();

  group('E2E: Complete User Journey', () {
    testWidgets('1. Onboarding → Login → Dashboard flow', (tester) async {
      // Start app
      app.main();
      await tester.pumpAndSettle(const Duration(seconds: 2));

      // Should show onboarding if first launch
      // Skip onboarding
      if (find.text('Salta').evaluate().isNotEmpty) {
        await tester.tap(find.text('Salta'));
        await tester.pumpAndSettle();
      }

      // Should be on login screen
      expect(find.text('Accedi'), findsOneWidget);

      // Enter credentials
      await tester.enterText(
        find.byType(TextField).first,
        'test@savy.app',
      );
      await tester.enterText(
        find.byType(TextField).last,
        'TestPassword123!',
      );
      await tester.pumpAndSettle();

      // Tap login button
      await tester.tap(find.widgetWithText(ElevatedButton, 'Accedi'));
      await tester.pumpAndSettle(const Duration(seconds: 3));

      // Should navigate to dashboard
      expect(find.text('Dashboard'), findsOneWidget);
    });

    testWidgets('2. Create Category flow', (tester) async {
      app.main();
      await tester.pumpAndSettle(const Duration(seconds: 2));

      // Assume logged in, navigate to categories
      await tester.tap(find.text('Categorie'));
      await tester.pumpAndSettle();

      // Tap add category button
      await tester.tap(find.byIcon(Icons.add));
      await tester.pumpAndSettle();

      // Fill category form
      await tester.enterText(find.byType(TextField).first, 'Test Category');
      await tester.pumpAndSettle();

      // Tap save
      await tester.tap(find.text('Salva'));
      await tester.pumpAndSettle(const Duration(seconds: 2));

      // Should show success message or return to list
      expect(find.text('Test Category'), findsOneWidget);
    });

    testWidgets('3. Add Transaction flow', (tester) async {
      app.main();
      await tester.pumpAndSettle(const Duration(seconds: 2));

      // Navigate to transactions
      await tester.tap(find.text('Transazioni'));
      await tester.pumpAndSettle();

      // Tap add transaction
      await tester.tap(find.byIcon(Icons.add));
      await tester.pumpAndSettle();

      // Fill transaction form
      await tester.enterText(find.byType(TextField).at(0), '50.00');
      await tester.enterText(find.byType(TextField).at(1), 'Test Purchase');
      await tester.pumpAndSettle();

      // Select category
      await tester.tap(find.text('Seleziona Categoria'));
      await tester.pumpAndSettle();
      await tester.tap(find.text('Alimentari').first);
      await tester.pumpAndSettle();

      // Save transaction
      await tester.tap(find.text('Salva'));
      await tester.pumpAndSettle(const Duration(seconds: 2));

      // Verify transaction appears in list
      expect(find.text('Test Purchase'), findsOneWidget);
    });

    testWidgets('4. Chat with AI Coach flow', (tester) async {
      app.main();
      await tester.pumpAndSettle(const Duration(seconds: 2));

      // Navigate to chat
      await tester.tap(find.byIcon(Icons.chat_bubble_rounded));
      await tester.pumpAndSettle();

      // Enter message
      await tester.enterText(
        find.byType(TextField),
        'Can I afford a €100 purchase?',
      );
      await tester.pumpAndSettle();

      // Send message
      await tester.tap(find.byIcon(Icons.send));
      await tester.pumpAndSettle(const Duration(seconds: 5));

      // Should receive AI response
      expect(find.textContaining('€'), findsWidgets);
    });

    testWidgets('5. View Spending Report flow', (tester) async {
      app.main();
      await tester.pumpAndSettle(const Duration(seconds: 2));

      // Navigate to reports
      await tester.tap(find.text('Report'));
      await tester.pumpAndSettle();

      // Should show spending chart
      expect(find.byType(PieChart), findsOneWidget);

      // Verify spending data is displayed
      expect(find.textContaining('€'), findsWidgets);
    });

    testWidgets('6. Settings & Logout flow', (tester) async {
      app.main();
      await tester.pumpAndSettle(const Duration(seconds: 2));

      // Navigate to settings
      await tester.tap(find.byIcon(Icons.settings));
      await tester.pumpAndSettle();

      // Scroll to logout button
      await tester.scrollUntilVisible(
        find.text('Esci'),
        500.0,
      );

      // Tap logout
      await tester.tap(find.text('Esci'));
      await tester.pumpAndSettle(const Duration(seconds: 2));

      // Should return to login screen
      expect(find.text('Accedi'), findsOneWidget);
    });
  });

  group('E2E: Pull-to-Refresh', () {
    testWidgets('Pull to refresh on Dashboard', (tester) async {
      app.main();
      await tester.pumpAndSettle(const Duration(seconds: 2));

      // Perform pull-to-refresh gesture
      await tester.drag(
        find.byType(RefreshIndicator),
        const Offset(0, 300),
      );
      await tester.pumpAndSettle(const Duration(seconds: 2));

      // Data should be refreshed
      expect(find.byType(CircularProgressIndicator), findsNothing);
    });
  });

  group('E2E: Offline Mode', () {
    testWidgets('App works offline with cached data', (tester) async {
      // TODO: Test offline mode
      // 1. Load data while online
      // 2. Disconnect network
      // 3. Verify cached data is still accessible
      // 4. Reconnect and verify sync
    });
  });
}
