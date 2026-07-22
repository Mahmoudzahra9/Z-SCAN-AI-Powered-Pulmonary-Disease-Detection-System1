// Z-SCAN Medical AI App - Widget Tests
//
// These tests verify the core UI elements of the Z-SCAN app
// are rendered correctly without requiring a running backend.

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:frontend/main.dart';

void main() {
  group('AIMedicalApp Tests', () {
    testWidgets('App renders without crashing', (WidgetTester tester) async {
      // Build the app
      await tester.pumpWidget(const AIMedicalApp());
      // Verify it renders
      expect(find.byType(MaterialApp), findsOneWidget);
    });

    testWidgets('App title is Z-SCAN', (WidgetTester tester) async {
      await tester.pumpWidget(const AIMedicalApp());
      // Check the app bar title
      expect(find.text('Z-SCAN Analysis'), findsOneWidget);
    });

    testWidgets('Camera and Gallery buttons are present', (WidgetTester tester) async {
      await tester.pumpWidget(const AIMedicalApp());
      await tester.pump();

      expect(find.text('Camera'), findsOneWidget);
      expect(find.text('Gallery'), findsOneWidget);
    });

    testWidgets('Camera icon is present', (WidgetTester tester) async {
      await tester.pumpWidget(const AIMedicalApp());
      await tester.pump();

      expect(find.byIcon(Icons.camera_alt), findsOneWidget);
    });

    testWidgets('Gallery icon is present', (WidgetTester tester) async {
      await tester.pumpWidget(const AIMedicalApp());
      await tester.pump();

      expect(find.byIcon(Icons.photo_library), findsOneWidget);
    });

    testWidgets('Image placeholder is shown when no image selected',
        (WidgetTester tester) async {
      await tester.pumpWidget(const AIMedicalApp());
      await tester.pump();

      expect(find.text('No image selected'), findsOneWidget);
    });

    testWidgets('Analyze button is NOT shown before image is selected',
        (WidgetTester tester) async {
      await tester.pumpWidget(const AIMedicalApp());
      await tester.pump();

      // The analyze button should not appear without an image
      expect(find.text('Analyze Image'), findsNothing);
    });

    testWidgets('Dark theme is applied', (WidgetTester tester) async {
      await tester.pumpWidget(const AIMedicalApp());
      final MaterialApp app = tester.widget(find.byType(MaterialApp));
      expect(app.themeMode, equals(ThemeMode.dark));
    });
  });
}
