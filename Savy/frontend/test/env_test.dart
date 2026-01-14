import 'package:flutter_test/flutter_test.dart';
import 'package:savy_frontend/core/constants/env.dart';

void main() {
  test('Env constants are defined', () {
    expect(Env.apiBaseUrl, isNotEmpty);
    expect(Env.apiBaseUrl, startsWith('http'));
  });
}
