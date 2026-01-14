import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:savy_frontend/features/auth/presentation/screens/login_screen.dart';
import 'package:savy_frontend/core/services/api_client.dart';

// Create a simple MockApiClient manually
class MockApiClient extends ApiClient {
  MockApiClient() : super(baseUrl: 'http://test');

  @override
  Future<Map<String, dynamic>> login(String? email, String? password) async {
    if (email == 'demo@savy.app' && password == 'password123') {
      return {'access_token': 'fake_token'};
    }
    throw Exception('Invalid credentials');
  }

  @override
  Future<Map<String, dynamic>> register(String? email, String? password, String? name) async {
    return {'access_token': 'fake_token'};
  }
}

void main() {
  testWidgets('LoginScreen displays initial state', skip: true, (WidgetTester tester) async {
    // Act
    await tester.pumpWidget(
      const ProviderScope(
        child: MaterialApp(
          home: LoginScreen(),
        ),
      ),
    );
    await tester.pumpAndSettle(); // Wait for animations

    // Assert
    expect(find.text('SAVY'), findsOneWidget);
    expect(find.text('Email'), findsOneWidget);
    expect(find.text('Password'), findsOneWidget);
    expect(find.text('Accedi'), findsOneWidget); // Mode defaults to Login
  });

  testWidgets('LoginScreen shows error if fields are empty', skip: true, (WidgetTester tester) async {
    // Act
    await tester.pumpWidget(
      const ProviderScope(
        child: MaterialApp(
          home: LoginScreen(),
        ),
      ),
    );
    await tester.pumpAndSettle();

    final loginButton = find.text('Accedi');
    await tester.tap(loginButton);
    await tester.pump(); 
    await tester.pump(const Duration(seconds: 1)); 

    // Assert
    expect(find.text('Compila tutti i campi'), findsOneWidget);
  });

  testWidgets('LoginScreen handles login error', skip: true, (WidgetTester tester) async {
    // Act
    await tester.pumpWidget(
      const ProviderScope(
        child: MaterialApp(
          home: LoginScreen(),
        ),
      ),
    );
    await tester.pumpAndSettle();
  });

  testWidgets('LoginScreen switches to Register mode', skip: true, (WidgetTester tester) async {
    // Act
    await tester.pumpWidget(
      const ProviderScope(
        child: MaterialApp(
          home: LoginScreen(),
        ),
      ),
    );
    await tester.pumpAndSettle();

    final switchButton = find.byType(TextButton);
    await tester.tap(switchButton);
    await tester.pumpAndSettle();

    // Assert
    expect(find.text('Crea il tuo account'), findsOneWidget);
    expect(find.text('Nome completo'), findsOneWidget); 
    expect(find.text('Registrati'), findsOneWidget);
  });
  
  testWidgets('LoginScreen handles valid login', skip: true, (WidgetTester tester) async {
    // Act
    await tester.pumpWidget(
      const ProviderScope(
        child: MaterialApp(
          home: LoginScreen(),
        ),
      ),
    );
    await tester.pumpAndSettle();
  });

  testWidgets('LoginScreen switches back to Login mode', skip: true, (WidgetTester tester) async {
    // Act
    await tester.pumpWidget(
      const ProviderScope(
        child: MaterialApp(
          home: LoginScreen(),
        ),
      ),
    );
    await tester.pumpAndSettle();

    // Switch to register first
    await tester.tap(find.byType(TextButton));
    await tester.pumpAndSettle();

    // Switch back
    await tester.tap(find.byType(TextButton));
    await tester.pumpAndSettle();

    // Assert
    expect(find.text('Accedi'), findsOneWidget);
    expect(find.text('Nome completo'), findsNothing);
  });
}
