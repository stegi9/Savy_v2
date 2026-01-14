import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:go_router/go_router.dart';
import '../../../../core/services/api_client.dart';
import '../../../../core/theme/app_colors.dart';

final apiClientProvider = Provider<ApiClient>((ref) {
  return ApiClient(baseUrl: 'http://10.0.2.2:8000/api/v1');
});

class LoginScreen extends ConsumerStatefulWidget {
  const LoginScreen({super.key});

  @override
  ConsumerState<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends ConsumerState<LoginScreen>
    with SingleTickerProviderStateMixin {
  final _emailController = TextEditingController(text: 'demo@savy.app');
  final _passwordController = TextEditingController(text: 'password123');
  bool _isLoading = false;
  bool _isRegisterMode = false;
  final _storage = const FlutterSecureStorage();
  final _nameController = TextEditingController();
  late AnimationController _animController;
  late Animation<double> _fadeAnimation;
  late Animation<Offset> _slideAnimation;

  @override
  void initState() {
    super.initState();
    _animController = AnimationController(
      duration: const Duration(milliseconds: 800),
      vsync: this,
    );
    _fadeAnimation = Tween<double>(begin: 0.0, end: 1.0).animate(
      CurvedAnimation(parent: _animController, curve: Curves.easeInOut),
    );
    _slideAnimation = Tween<Offset>(
      begin: const Offset(0, 0.3),
      end: Offset.zero,
    ).animate(CurvedAnimation(parent: _animController, curve: Curves.easeOutCubic));
    _animController.forward();
  }

  @override
  void dispose() {
    _emailController.dispose();
    _passwordController.dispose();
    _nameController.dispose();
    _animController.dispose();
    super.dispose();
  }

  Future<void> _login() async {
    if (_emailController.text.isEmpty || _passwordController.text.isEmpty) {
      _showSnackBar('Compila tutti i campi', isError: true);
      return;
    }

    setState(() => _isLoading = true);

    try {
      final apiClient = ref.read(apiClientProvider);
      final response = await apiClient.login(
        _emailController.text,
        _passwordController.text,
      );

      await _storage.write(
        key: 'access_token',
        value: response['access_token'],
      );

      if (mounted) {
        context.go('/dashboard');
      }
    } catch (e) {
      if (mounted) {
        _showSnackBar('Email o password errati', isError: true);
      }
    } finally {
      if (mounted) setState(() => _isLoading = false);
    }
  }

  Future<void> _register() async {
    if (_emailController.text.isEmpty ||
        _passwordController.text.isEmpty ||
        _nameController.text.isEmpty) {
      _showSnackBar('Compila tutti i campi', isError: true);
      return;
    }

    if (_passwordController.text.length < 6) {
      _showSnackBar('Password troppo corta (min 6 caratteri)', isError: true);
      return;
    }

    setState(() => _isLoading = true);

    try {
      final apiClient = ref.read(apiClientProvider);
      final response = await apiClient.register(
        _emailController.text,
        _passwordController.text,
        _nameController.text,
      );

      await _storage.write(
        key: 'access_token',
        value: response['access_token'],
      );

      if (mounted) {
        _showSnackBar('Account creato con successo!', isError: false);
        await Future.delayed(const Duration(milliseconds: 500));
        context.go('/dashboard');
      }
    } catch (e) {
      if (mounted) {
        _showSnackBar('Errore: ${e.toString()}', isError: true);
      }
    } finally {
      if (mounted) setState(() => _isLoading = false);
    }
  }

  void _showSnackBar(String message, {required bool isError}) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
        backgroundColor: isError ? AppColors.error : AppColors.success,
        behavior: SnackBarBehavior.floating,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
        margin: const EdgeInsets.all(16),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Container(
        decoration: BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
            colors: [
              AppColors.primary,
              AppColors.primary.withOpacity(0.7),
              AppColors.primaryDark,
            ],
          ),
        ),
        child: SafeArea(
          child: Center(
            child: SingleChildScrollView(
              padding: const EdgeInsets.all(24),
              child: FadeTransition(
                opacity: _fadeAnimation,
                child: SlideTransition(
                  position: _slideAnimation,
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      // Logo & Title
                      Container(
                        padding: const EdgeInsets.all(20),
                        decoration: BoxDecoration(
                          color: Colors.white.withOpacity(0.2),
                          shape: BoxShape.circle,
                        ),
                        child: const Icon(
                          Icons.account_balance_wallet_rounded,
                          size: 64,
                          color: Colors.white,
                        ),
                      ),
                      const SizedBox(height: 24),
                      const Text(
                        'SAVY',
                        style: TextStyle(
                          fontSize: 48,
                          fontWeight: FontWeight.bold,
                          color: Colors.white,
                          letterSpacing: 2,
                        ),
                      ),
                      const SizedBox(height: 8),
                      Text(
                        _isRegisterMode
                            ? 'Crea il tuo account'
                            : 'Il tuo coach finanziario personale',
                        style: const TextStyle(
                          fontSize: 16,
                          color: Colors.white70,
                        ),
                      ),
                      const SizedBox(height: 48),

                      // Form Card
                      Container(
                        padding: const EdgeInsets.all(24),
                        decoration: BoxDecoration(
                          color: Colors.white,
                          borderRadius: BorderRadius.circular(24),
                          boxShadow: [
                            BoxShadow(
                              color: Colors.black.withOpacity(0.1),
                              blurRadius: 20,
                              offset: const Offset(0, 10),
                            ),
                          ],
                        ),
                        child: Column(
                          children: [
                            if (_isRegisterMode) ...[
                              _buildTextField(
                                controller: _nameController,
                                label: 'Nome completo',
                                icon: Icons.person_outline,
                              ),
                              const SizedBox(height: 16),
                            ],
                            _buildTextField(
                              controller: _emailController,
                              label: 'Email',
                              icon: Icons.email_outlined,
                              keyboardType: TextInputType.emailAddress,
                            ),
                            const SizedBox(height: 16),
                            _buildTextField(
                              controller: _passwordController,
                              label: 'Password',
                              icon: Icons.lock_outline,
                              isPassword: true,
                            ),
                            const SizedBox(height: 24),
                            _buildActionButton(),
                            const SizedBox(height: 16),
                            _buildSwitchModeButton(),
                          ],
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildTextField({
    required TextEditingController controller,
    required String label,
    required IconData icon,
    bool isPassword = false,
    TextInputType? keyboardType,
  }) {
    return TextField(
      controller: controller,
      decoration: InputDecoration(
        labelText: label,
        prefixIcon: Icon(icon, color: AppColors.primary),
        filled: true,
        fillColor: AppColors.surfaceVariant,
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: BorderSide.none,
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: const BorderSide(color: AppColors.primary, width: 2),
        ),
      ),
      obscureText: isPassword,
      keyboardType: keyboardType,
      style: const TextStyle(color: Colors.black87), // Force black text on white card
    );
  }

  Widget _buildActionButton() {
    return SizedBox(
      width: double.infinity,
      height: 56,
      child: ElevatedButton(
        onPressed: _isLoading
            ? null
            : (_isRegisterMode ? _register : _login),
        style: ElevatedButton.styleFrom(
          backgroundColor: AppColors.primary,
          foregroundColor: Colors.white,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(12),
          ),
          elevation: 0,
        ),
        child: _isLoading
            ? const SizedBox(
                height: 24,
                width: 24,
                child: CircularProgressIndicator(
                  strokeWidth: 2,
                  color: Colors.white,
                ),
              )
            : Text(
                _isRegisterMode ? 'Registrati' : 'Accedi',
                style: const TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.bold,
                ),
              ),
      ),
    );
  }

  Widget _buildSwitchModeButton() {
    return TextButton(
      onPressed: () {
        setState(() {
          _isRegisterMode = !_isRegisterMode;
          _animController.reset();
          _animController.forward();
        });
      },
      child: RichText(
        text: TextSpan(
          style: const TextStyle(color: AppColors.textSecondary, fontSize: 14),
          children: [
            TextSpan(
              text: _isRegisterMode
                  ? 'Hai già un account? '
                  : 'Non hai un account? ',
            ),
            TextSpan(
              text: _isRegisterMode ? 'Accedi' : 'Registrati',
              style: const TextStyle(
                color: AppColors.primary,
                fontWeight: FontWeight.bold,
              ),
            ),
          ],
        ),
      ),
    );
  }
}
