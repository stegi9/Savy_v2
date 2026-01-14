import 'package:flutter/material.dart';
import 'package:fl_chart/fl_chart.dart';
import 'dart:math' as math;
import '../../../../core/theme/app_colors.dart';

class CumulativeLineChartWidget extends StatelessWidget {
  final List<Map<String, dynamic>> currentData;
  final List<Map<String, dynamic>> previousData;
  final double projected;
  final double totalSpent;

  const CumulativeLineChartWidget({
    super.key,
    required this.currentData,
    required this.previousData,
    required this.projected,
    required this.totalSpent,
  });

  @override
  Widget build(BuildContext context) {
    if (currentData.isEmpty) {
      return const SizedBox(
        height: 300,
        child: Center(child: Text('Nessun dato disponibile')),
      );
    }

    final currentMax = currentData.isNotEmpty
        ? currentData.map((d) => (d['cumulative_amount'] as num).toDouble()).reduce(math.max)
        : 0.0;
    final previousMax = previousData.isNotEmpty
        ? previousData.map((d) => (d['cumulative_amount'] as num).toDouble()).reduce(math.max)
        : 0.0;
    final maxY = math.max(math.max(currentMax, previousMax), projected) * 1.1;

    return SizedBox(
      height: 300,
      child: Padding(
        padding: const EdgeInsets.only(right: 16, top: 16),
        child: LineChart(
          LineChartData(
            minY: 0,
            maxY: maxY,
            lineBarsData: [
              _buildCurrentPeriodLine(),
              _buildPreviousPeriodLine(),
              _buildProjectionLine(),
            ],
            titlesData: FlTitlesData(
              bottomTitles: AxisTitles(
                sideTitles: SideTitles(
                  showTitles: true,
                  reservedSize: 30,
                  getTitlesWidget: (value, meta) {
                    if (value.toInt() >= 0 && value.toInt() < currentData.length) {
                      final date = DateTime.parse(currentData[value.toInt()]['date'] as String);
                      return Padding(
                        padding: const EdgeInsets.only(top: 8),
                        child: Text('${date.day}/${date.month}', style: const TextStyle(fontSize: 10, color: AppColors.textSecondary)),
                      );
                    }
                    return const SizedBox();
                  },
                  interval: (currentData.length / 5).ceilToDouble(),
                ),
              ),
              leftTitles: AxisTitles(
                sideTitles: SideTitles(
                  showTitles: true,
                  reservedSize: 50,
                  getTitlesWidget: (value, meta) {
                    return Text('€${value.toInt()}', style: const TextStyle(fontSize: 10, color: AppColors.textSecondary));
                  },
                ),
              ),
              topTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
              rightTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
            ),
            gridData: FlGridData(
              show: true,
              drawVerticalLine: false,
              horizontalInterval: maxY / 5,
              getDrawingHorizontalLine: (value) => const FlLine(color: AppColors.surfaceVariant, strokeWidth: 1),
            ),
            borderData: FlBorderData(
              show: true,
              border: const Border(
                left: BorderSide(color: AppColors.surfaceVariant),
                bottom: BorderSide(color: AppColors.surfaceVariant),
              ),
            ),
            lineTouchData: LineTouchData(
              enabled: true,
              touchTooltipData: LineTouchTooltipData(
                getTooltipItems: (touchedSpots) {
                  return touchedSpots.map((spot) {
                    String label = '';
                    if (spot.barIndex == 0) {
                      label = 'Corrente: €${spot.y.toStringAsFixed(2)}';
                    } else if (spot.barIndex == 1) label = 'Precedente: €${spot.y.toStringAsFixed(2)}';
                    else if (spot.barIndex == 2) label = 'Proiezione: €${spot.y.toStringAsFixed(2)}';
                    return LineTooltipItem(label, const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 12));
                  }).toList();
                },
              ),
            ),
          ),
        ),
      ),
    );
  }

  LineChartBarData _buildCurrentPeriodLine() {
    final spots = <FlSpot>[];
    for (int i = 0; i < currentData.length; i++) {
      spots.add(FlSpot(i.toDouble(), (currentData[i]['cumulative_amount'] as num).toDouble()));
    }
    return LineChartBarData(
      spots: spots,
      isCurved: true,
      color: AppColors.primary,
      barWidth: 3,
      dotData: const FlDotData(show: false),
      belowBarData: BarAreaData(
        show: true,
        gradient: LinearGradient(
          colors: [AppColors.primary.withOpacity(0.3), AppColors.primary.withOpacity(0.0)],
          begin: Alignment.topCenter,
          end: Alignment.bottomCenter,
        ),
      ),
    );
  }

  LineChartBarData _buildPreviousPeriodLine() {
    if (previousData.isEmpty) return LineChartBarData(spots: []);
    final spots = <FlSpot>[];
    final ratio = currentData.length / previousData.length;
    for (int i = 0; i < previousData.length; i++) {
      spots.add(FlSpot((i * ratio).toDouble(), (previousData[i]['cumulative_amount'] as num).toDouble()));
    }
    return LineChartBarData(
      spots: spots,
      isCurved: true,
      color: AppColors.textSecondary,
      barWidth: 2,
      dotData: const FlDotData(show: false),
      dashArray: [5, 5],
    );
  }

  LineChartBarData _buildProjectionLine() {
    if (currentData.isEmpty) return LineChartBarData(spots: []);
    final lastIndex = currentData.length - 1;
    final lastCumulative = (currentData[lastIndex]['cumulative_amount'] as num).toDouble();
    final projectedEndIndex = currentData.length * 1.5;
    return LineChartBarData(
      spots: [FlSpot(lastIndex.toDouble(), lastCumulative), FlSpot(projectedEndIndex, projected)],
      isCurved: false,
      color: AppColors.warning,
      barWidth: 2,
      dotData: FlDotData(
        show: true,
        getDotPainter: (spot, percent, barData, index) {
          return FlDotCirclePainter(radius: 4, color: AppColors.warning, strokeWidth: 2, strokeColor: Colors.white);
        },
      ),
      dashArray: [8, 4],
    );
  }
}

class LegendItem extends StatelessWidget {
  final Color color;
  final String label;
  final bool isArea;
  final bool isDashed;

  const LegendItem({super.key, required this.color, required this.label, this.isArea = false, this.isDashed = false});

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        Container(
          width: 24,
          height: isDashed ? 2 : (isArea ? 12 : 3),
          decoration: isDashed ? null : BoxDecoration(color: color, borderRadius: isArea ? BorderRadius.circular(2) : null),
          child: isDashed ? CustomPaint(painter: DashedLinePainter(color: color)) : null,
        ),
        const SizedBox(width: 8),
        Text(label, style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w500)),
      ],
    );
  }
}

class DashedLinePainter extends CustomPainter {
  final Color color;
  DashedLinePainter({required this.color});

  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()..color = color..strokeWidth = 2..style = PaintingStyle.stroke;
    const dashWidth = 4;
    const dashSpace = 3;
    double startX = 0;
    while (startX < size.width) {
      canvas.drawLine(Offset(startX, size.height / 2), Offset(startX + dashWidth, size.height / 2), paint);
      startX += dashWidth + dashSpace;
    }
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => false;
}


