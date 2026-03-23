import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:url_launcher/url_launcher.dart';
import '../data/bank_service.dart';
import '../../../../core/l10n/app_strings.dart';
import '../../../../core/theme/app_colors.dart';

class BankConnectScreen extends ConsumerStatefulWidget {
  final bool initialSuccess;
  const BankConnectScreen({super.key, this.initialSuccess = false});

  @override
  ConsumerState<BankConnectScreen> createState() => _BankConnectScreenState();
}

class _BankConnectScreenState extends ConsumerState<BankConnectScreen> {
  bool _isLoading = false;
  String? _syncStatus;

  @override
  void initState() {
    super.initState();
    if (widget.initialSuccess) {
      WidgetsBinding.instance.addPostFrameCallback((_) {
        _syncBank(); // Automatically start sync on success redirect
      });
    }
  }

  Future<void> _connectBank() async {
    setState(() => _isLoading = true);
    try {
      final link = await ref.read(bankServiceProvider).connectBank();
      final url = Uri.parse(link);
      
      if (await canLaunchUrl(url)) {
        await launchUrl(url, mode: LaunchMode.externalApplication);
      } else {
        throw 'Could not launch bank login';
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error: $e')),
        );
      }
    } finally {
      setState(() => _isLoading = false);
    }
  }

  Future<void> _syncBank() async {
    setState(() {
      _isLoading = true;
      _syncStatus = "Sincronizzazione in corso... Non chiudere l'app.";
    });
    try {
      await ref.read(bankServiceProvider).syncData();
      
      if (mounted) {
        setState(() => _syncStatus = "Completato! Caricamento conti...");
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Sincronizzazione riuscita! Hai collegato il tuo conto alla perfezione.'),
            backgroundColor: Colors.green,
            behavior: SnackBarBehavior.floating,
          ),
        );
        // Refresh global providers to fetch new synced accounts + transactions
        context.go('/accounts');
      }
    } catch (e) {
      if (mounted) {
        setState(() => _syncStatus = "Errore durante la sincronizzazione: $e");
      }
    } finally {
      if (mounted) {
        setState(() => _isLoading = false);
      }
    }
  }

  @override
  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;

    return Scaffold(
      backgroundColor: theme.scaffoldBackgroundColor,
      appBar: AppBar(
        title: Text(AppStrings.get('bankIntegrationTitle')),
        backgroundColor: colorScheme.primary,
        foregroundColor: colorScheme.onPrimary,
      ),
      body: SafeArea( // Ensure content avoids system UI
        child: Padding(
          padding: const EdgeInsets.all(16.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Text(
                AppStrings.get('bankIntegrationSubtitle'),
                style: TextStyle(
                  fontSize: 18, 
                  fontWeight: FontWeight.bold,
                  color: colorScheme.onSurface, // Explicit text color
                ),
              ),
              const SizedBox(height: 10),
              Text(
                AppStrings.get('bankCredentialsInfo'),
                style: const TextStyle(color: AppColors.textSecondary),
              ),
              const SizedBox(height: 30),
              
              ElevatedButton.icon(
                onPressed: _isLoading ? null : _connectBank,
                icon: const Icon(Icons.link),
                label: Text('${AppStrings.get('connectButton')} (Connect Session)'),
                style: ElevatedButton.styleFrom(
                  backgroundColor: colorScheme.primary,
                  foregroundColor: colorScheme.onPrimary,
                  padding: const EdgeInsets.symmetric(vertical: 16),
                ),
              ),
              
              const SizedBox(height: 20),
              const Divider(),
              const SizedBox(height: 20),
              
              if (_syncStatus != null)
                Container(
                  padding: const EdgeInsets.all(10),
                  decoration: BoxDecoration(
                    color: colorScheme.primary.withOpacity(0.1),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Text(
                    _syncStatus!,
                    style: TextStyle(color: colorScheme.onSurface),
                  ),
                ),
                
              const SizedBox(height: 20),

              ElevatedButton.icon(
                onPressed: _isLoading ? null : _syncBank,
                icon: const Icon(Icons.sync),
                label: Text('${AppStrings.get('syncButton')} (Sync)'),
                style: ElevatedButton.styleFrom(
                  backgroundColor: AppColors.success,
                  foregroundColor: Colors.white,
                  padding: const EdgeInsets.symmetric(vertical: 16),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
