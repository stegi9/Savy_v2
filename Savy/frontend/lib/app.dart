import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'core/theme/app_theme.dart';
import 'features/auth/presentation/screens/login_screen.dart';
import 'features/auth/presentation/screens/password_reset_screen.dart';
import 'features/auth/presentation/screens/email_verification_screen.dart';
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
import 'features/onboarding/presentation/screens/onboarding_screen.dart';
import 'features/accounts/presentation/screens/accounts_screen.dart';

import 'core/providers/preferences_provider.dart';
import 'core/providers/auth_provider.dart';
import 'core/services/storage_helper.dart';

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
  final authState = ref.watch(authStateProvider);

  return GoRouter(
    initialLocation: '/onboarding',  // Start with onboarding check
    redirect: (context, state) async {
      final isAuthenticated = ref.read(authStateProvider).isAuthenticated;
      final isLoading = ref.read(authStateProvider).isLoading;
      final currentPath = state.matchedLocation;
      
      // Public routes that don't need auth check
      final publicRoutes = ['/onboarding', '/login', '/reset-password', '/verify-email'];
      final isPublicRoute = publicRoutes.any((route) => currentPath.startsWith(route));

      // Check if onboarding is completed
      final storage = StorageHelper.instance;
      final onboardingCompleted = await storage.read(key: 'onboarding_completed');

      // Show onboarding if not completed
      if (onboardingCompleted == null && currentPath != '/onboarding') {
        return '/onboarding';
      }

      // Still checking auth status - stay on current route
      if (isLoading) {
        return null;
      }

      // After onboarding is done, check auth
      if (onboardingCompleted != null) {
        // Not authenticated and trying to access protected route
        if (!isAuthenticated && !isPublicRoute) {
          return '/login';
        }

        // Authenticated and on login/onboarding page - go to dashboard
        if (isAuthenticated && (currentPath == '/login' || currentPath == '/onboarding')) {
          return '/dashboard';
        }
      }

      return null;
    },
    routes: [
      GoRoute(
        path: '/onboarding',
        builder: (context, state) => const OnboardingScreen(),
      ),
      GoRoute(
        path: '/login',
        builder: (context, state) => const LoginScreen(),
      ),
      GoRoute(
        path: '/reset-password',
        builder: (context, state) {
          final token = state.uri.queryParameters['token'];
          return PasswordResetScreen(token: token);
        },
      ),
      GoRoute(
        path: '/verify-email',
        builder: (context, state) {
          final token = state.uri.queryParameters['token'];
          return EmailVerificationScreen(token: token);
        },
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
        path: '/accounts',
        builder: (context, state) => const AccountsScreen(),
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
    refreshListenable: GoRouterRefreshStream(authState),
  );
});

/// Helper to make GoRouter reactive to auth changes
class GoRouterRefreshStream extends ChangeNotifier {
  GoRouterRefreshStream(AuthState authState) {
    _authState = authState;
  }

  late AuthState _authState;

  void update(AuthState authState) {
    if (_authState.isAuthenticated != authState.isAuthenticated) {
      _authState = authState;
      notifyListeners();
    }
  }
}

