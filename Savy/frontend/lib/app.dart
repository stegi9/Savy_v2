import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'core/theme/app_theme.dart';
import 'features/auth/presentation/screens/login_screen.dart';
import 'features/dashboard/presentation/screens/dashboard_screen.dart';
import 'features/transactions/presentation/screens/transactions_screen.dart';
import 'features/categories/presentation/screens/categories_screen.dart';
import 'features/bills/presentation/screens/bills_screen.dart';
import 'features/settings/presentation/screens/settings_screen.dart';
import 'features/reports/presentation/screens/spending_report_screen.dart';
import 'features/chat/presentation/screens/chat_screen.dart';
import 'features/optimization/presentation/screens/optimization_screen.dart';
import 'features/analytics/presentation/screens/deep_dive_screen.dart';
import 'features/bank_integration/presentation/bank_connect_screen.dart';

import 'core/providers/preferences_provider.dart';

class SavyApp extends ConsumerWidget {
  const SavyApp({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final preferencesState = ref.watch(preferencesProvider);
    final router = ref.watch(routerProvider);

    return MaterialApp.router(
      title: 'Savy - Personal Finance Coach',
      debugShowCheckedModeBanner: false,
      theme: AppTheme.lightTheme,
      darkTheme: AppTheme.darkTheme,
      themeMode: preferencesState.themeMode,
      locale: preferencesState.locale,
      routerConfig: router,
    );
  }
}

final routerProvider = Provider<GoRouter>((ref) {
  return GoRouter(
    initialLocation: '/login',
    routes: [
      GoRoute(
        path: '/login',
        builder: (context, state) => const LoginScreen(),
      ),
      GoRoute(
        path: '/',
        redirect: (context, state) => '/dashboard',
      ),
      GoRoute(
        path: '/dashboard',
        builder: (context, state) => const DashboardScreen(),
      ),
      GoRoute(
        path: '/transactions',
        builder: (context, state) => const TransactionsScreen(),
      ),
      GoRoute(
        path: '/categories',
        builder: (context, state) => const CategoriesScreen(),
      ),
      GoRoute(
        path: '/bills',
        builder: (context, state) => const BillsScreen(),
      ),
      GoRoute(
        path: '/settings',
        builder: (context, state) => const SettingsScreen(),
      ),
      GoRoute(
        path: '/reports',
        builder: (context, state) => const SpendingReportScreen(),
      ),
      GoRoute(
        path: '/analytics/deep-dive',
        builder: (context, state) => const DeepDiveScreen(),
      ),
      GoRoute(
        path: '/chat',
        builder: (context, state) => const ChatScreen(),
      ),
      GoRoute(
        path: '/optimization',
        builder: (context, state) => const OptimizationScreen(),
      ),
      GoRoute(
        path: '/bank-connect',
        builder: (context, state) {
          final success = state.uri.queryParameters['success'];
          return BankConnectScreen(initialSuccess: success == 'true');
        },
      ),
      GoRoute(
        path: '/callback',
        redirect: (context, state) => '/bank-connect?success=true',
      ),
    ],
  );
});


