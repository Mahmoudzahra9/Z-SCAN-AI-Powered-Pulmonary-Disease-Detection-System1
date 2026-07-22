import 'dart:convert';
import 'dart:io';
import 'dart:typed_data';
import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import 'package:http/http.dart' as http;
import 'package:flutter/foundation.dart' show kIsWeb;
import 'package:url_launcher/url_launcher.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  File? _image;
  XFile? _xfile;
  Uint8List? _webImageBytes; // FIX: نحفظ bytes الصورة للعرض في الويب
  final picker = ImagePicker();

  bool _isLoading = false;
  String? _prediction;
  double? _confidence;
  String? _adviceAr;
  String? _adviceEn;
  String? _dietAr;
  String? _dietEn;
  String? _doctorsAr;
  String? _doctorsEn;
  List<dynamic> _videos = [];
  String? _errorMessage;

  // عنوان الباكند — يدعم المحاكي والجهاز الحقيقي وWeb
  String get _baseUrl {
    if (kIsWeb) {
      // Flutter Web — يتصل بـ localhost مباشرة
      return 'http://localhost:5000';
    } else if (Platform.isAndroid) {
      // ⚠️ اختر واحدة:
      // للجهاز الحقيقي (Real Device): استخدم IP الجهاز
      return 'http://192.168.100.27:5000';
      // للمحاكي (Emulator): uncomment السطر التالي وcomment السطر فوقه
      // return 'http://10.0.2.2:5000';
    } else if (Platform.isIOS) {
      // iOS Simulator يستخدم localhost مباشرة
      return 'http://localhost:5000';
    } else {
      return 'http://localhost:5000';
    }
  }

  Future<void> _pickImage(ImageSource source) async {
    try {
      final pickedFile = await picker.pickImage(
        source: source,
        imageQuality: 85, // ضغط خفيف لتسريع الإرسال
      );
      if (pickedFile != null) {
        // FIX: نقرأ الـ bytes دائماً (للويب والموبايل)
        final bytes = await pickedFile.readAsBytes();
        setState(() {
          _xfile = pickedFile;
          _webImageBytes = bytes;
          if (!kIsWeb) _image = File(pickedFile.path);
          _prediction = null;
          _confidence = null;
          _adviceAr = null;
          _adviceEn = null;
          _dietAr = null;
          _dietEn = null;
          _doctorsAr = null;
          _doctorsEn = null;
          _videos = [];
          _errorMessage = null;
        });
      }
    } catch (e) {
      setState(() {
        _errorMessage = 'Failed to pick image: $e';
      });
    }
  }

  Future<void> _predictImage() async {
    if (_xfile == null && _image == null) return;

    setState(() {
      _isLoading = true;
      _errorMessage = null;
      _prediction = null;
      _confidence = null;
      _adviceAr = null;
      _adviceEn = null;
      _dietAr = null;
      _dietEn = null;
      _doctorsAr = null;
      _doctorsEn = null;
      _videos = [];
    });

    try {
      var request = http.MultipartRequest(
        'POST',
        Uri.parse('$_baseUrl/predict'),
      );

      // FIX: نستخدم fromBytes دائماً — يعمل على الويب والموبايل
      if (_webImageBytes != null) {
        final filename = _xfile?.name ?? 'xray.jpg';
        request.files.add(
          http.MultipartFile.fromBytes(
            'file',
            _webImageBytes!,
            filename: filename,
          ),
        );
      } else if (_image != null) {
        request.files.add(
          await http.MultipartFile.fromPath('file', _image!.path),
        );
      }

      // FIX: timeout للطلب 30 ثانية
      final streamedResponse = await request.send().timeout(
        const Duration(seconds: 30),
        onTimeout: () {
          throw Exception('Request timed out. Is the Flask server running on port 5000?');
        },
      );

      final responseData = await streamedResponse.stream.bytesToString();
      final jsonData = json.decode(responseData);

      if (streamedResponse.statusCode == 200) {
        setState(() {
          _prediction = jsonData['prediction'];
          _confidence = (jsonData['confidence'] as num).toDouble() * 100;
          _adviceAr = jsonData['advice_ar'];
          _adviceEn = jsonData['advice_en'];
          _dietAr = jsonData['diet_ar'];
          _dietEn = jsonData['diet_en'];
          _doctorsAr = jsonData['doctors_ar'];
          _doctorsEn = jsonData['doctors_en'];
          _videos = jsonData['videos'] ?? [];
        });
      } else {
        setState(() {
          _errorMessage = jsonData['error'] ?? 'Server error (${streamedResponse.statusCode})';
        });
      }
    } on SocketException catch (e) {
      setState(() {
        _errorMessage =
            '❌ Cannot connect to server!\n\nMake sure:\n1. Flask backend is running (start_app.bat)\n2. No firewall blocking port 5000\n\nDetails: $e';
      });
    } catch (e) {
      setState(() {
        _errorMessage = '❌ Network Error:\n$e';
      });
    } finally {
      setState(() {
        _isLoading = false;
      });
    }
  }

  // FIX: widget لعرض الصورة يدعم الويب والموبايل بشكل صحيح
  Widget _buildImagePreview() {
    if (_webImageBytes != null) {
      // استخدام Image.memory — يعمل على كل المنصات
      return Image.memory(_webImageBytes!, fit: BoxFit.cover);
    } else if (_image != null) {
      return Image.file(_image!, fit: BoxFit.cover);
    }
    return const Column(
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        Icon(Icons.image_search, size: 60, color: Colors.grey),
        SizedBox(height: 16),
        Text(
          'No image selected',
          style: TextStyle(color: Colors.grey, fontSize: 16),
        ),
      ],
    );
  }

  Widget _buildResultBox() {
    if (_isLoading) {
      return const Column(
        children: [
          SizedBox(height: 24),
          CircularProgressIndicator(color: Colors.blueAccent),
          SizedBox(height: 16),
          Text(
            'Analyzing Image...',
            style: TextStyle(fontSize: 16, color: Colors.grey),
          ),
        ],
      );
    }

    if (_errorMessage != null) {
      return Container(
        margin: const EdgeInsets.only(top: 24),
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: Colors.redAccent.withValues(alpha: 0.1),
          borderRadius: BorderRadius.circular(12),
          border: Border.all(color: Colors.redAccent),
        ),
        child: Text(
          _errorMessage!,
          style: const TextStyle(color: Colors.redAccent),
          textAlign: TextAlign.center,
        ),
      );
    }

    if (_prediction != null && _confidence != null) {
      Color resultColor =
          _prediction == 'NORMAL' ? Colors.greenAccent : Colors.orangeAccent;
      return Container(
        margin: const EdgeInsets.only(top: 24),
        width: double.infinity,
        padding: const EdgeInsets.all(24),
        decoration: BoxDecoration(
          color: const Color(0xFF2C2C2C),
          borderRadius: BorderRadius.circular(16),
          boxShadow: [
            BoxShadow(
              color: resultColor.withValues(alpha: 0.2),
              blurRadius: 10,
              spreadRadius: 2,
            )
          ],
        ),
        child: Column(
          children: [
            Text(
              'Prediction',
              style: TextStyle(fontSize: 16, color: Colors.grey[400]),
            ),
            const SizedBox(height: 8),
            Text(
              _prediction!,
              style: TextStyle(
                fontSize: 28,
                fontWeight: FontWeight.bold,
                color: resultColor,
                letterSpacing: 2,
              ),
            ),
            const SizedBox(height: 16),
            Text(
              'Confidence',
              style: TextStyle(fontSize: 16, color: Colors.grey[400]),
            ),
            const SizedBox(height: 8),
            Text(
              '${_confidence!.toStringAsFixed(1)}%',
              style: const TextStyle(
                fontSize: 24,
                fontWeight: FontWeight.w500,
                color: Colors.white,
              ),
            ),
            if (_adviceAr != null && _adviceAr!.isNotEmpty) ...[
              const Divider(color: Colors.white24, height: 32),
              const Row(
                children: [
                  Icon(Icons.medical_information, color: Colors.blueAccent),
                  SizedBox(width: 8),
                  Text('Medical Advice / نصائح طبية', style: TextStyle(fontSize: 18, color: Colors.blueAccent, fontWeight: FontWeight.bold)),
                ],
              ),
              const SizedBox(height: 8),
              SizedBox(
                width: double.infinity,
                child: Text(
                  _adviceEn ?? '',
                  style: const TextStyle(fontSize: 15, color: Colors.white70),
                  textAlign: TextAlign.left,
                ),
              ),
              const SizedBox(height: 4),
              SizedBox(
                width: double.infinity,
                child: Text(
                  _adviceAr!,
                  style: const TextStyle(fontSize: 16, color: Colors.white),
                  textAlign: TextAlign.right,
                  textDirection: TextDirection.rtl,
                ),
              ),
            ],
            if (_dietAr != null && _dietAr!.isNotEmpty) ...[
              const SizedBox(height: 16),
              const Row(
                children: [
                  Icon(Icons.restaurant, color: Colors.greenAccent),
                  SizedBox(width: 8),
                  Text('Diet / النظام الغذائي', style: TextStyle(fontSize: 18, color: Colors.greenAccent, fontWeight: FontWeight.bold)),
                ],
              ),
              const SizedBox(height: 8),
              SizedBox(
                width: double.infinity,
                child: Text(
                  _dietEn ?? '',
                  style: const TextStyle(fontSize: 15, color: Colors.white70),
                  textAlign: TextAlign.left,
                ),
              ),
              const SizedBox(height: 4),
              SizedBox(
                width: double.infinity,
                child: Text(
                  _dietAr!,
                  style: const TextStyle(fontSize: 16, color: Colors.white),
                  textAlign: TextAlign.right,
                  textDirection: TextDirection.rtl,
                ),
              ),
            ],
            if (_doctorsAr != null && _doctorsAr!.isNotEmpty) ...[
              const SizedBox(height: 16),
              const Row(
                children: [
                  Icon(Icons.person_search, color: Colors.pinkAccent),
                  SizedBox(width: 8),
                  Text('Doctors / أطباء مقترحون', style: TextStyle(fontSize: 18, color: Colors.pinkAccent, fontWeight: FontWeight.bold)),
                ],
              ),
              const SizedBox(height: 8),
              SizedBox(
                width: double.infinity,
                child: Text(
                  _doctorsEn ?? '',
                  style: const TextStyle(fontSize: 15, color: Colors.white70),
                  textAlign: TextAlign.left,
                ),
              ),
              const SizedBox(height: 4),
              SizedBox(
                width: double.infinity,
                child: Text(
                  _doctorsAr!,
                  style: const TextStyle(fontSize: 16, color: Colors.white),
                  textAlign: TextAlign.right,
                  textDirection: TextDirection.rtl,
                ),
              ),
            ],
            if (_videos.isNotEmpty) ...[
              const SizedBox(height: 16),
              const Row(
                children: [
                  Icon(Icons.video_library, color: Colors.redAccent),
                  SizedBox(width: 8),
                  Text('Educational Videos / فيديوهات تعليمية', style: TextStyle(fontSize: 18, color: Colors.redAccent, fontWeight: FontWeight.bold)),
                ],
              ),
              const SizedBox(height: 8),
              ..._videos.map((video) {
                return InkWell(
                  onTap: () async {
                    final Uri url = Uri.parse(video['url']);
                    if (!await launchUrl(url)) {
                      throw Exception('Could not launch ${video['url']}');
                    }
                  },
                  child: Container(
                    margin: const EdgeInsets.only(bottom: 8),
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(
                      color: Colors.white.withValues(alpha: 0.05),
                      borderRadius: BorderRadius.circular(8),
                      border: Border.all(color: Colors.white12),
                    ),
                    child: Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        const Icon(Icons.play_circle_fill, color: Colors.redAccent),
                        Expanded(
                          child: Text(
                            video['title'] ?? '',
                            style: const TextStyle(color: Colors.white, fontSize: 16),
                            textAlign: TextAlign.right,
                            textDirection: TextDirection.rtl,
                          ),
                        ),
                      ],
                    ),
                  ),
                );
              }),
            ],
          ],
        ),
      );
    }

    return const SizedBox.shrink();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            ClipRRect(
              borderRadius: BorderRadius.circular(8),
              child: Image.asset(
                'assets/logo.png',
                width: 40,
                height: 40,
                fit: BoxFit.cover,
                errorBuilder: (c, e, s) =>
                    const Icon(Icons.medical_services),
              ),
            ),
            const SizedBox(width: 12),
            const Text('Z-SCAN Analysis'),
          ],
        ),
        centerTitle: true,
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(20),
        child: Column(
          children: [
            Card(
              child: Padding(
                padding: const EdgeInsets.all(16.0),
                child: Column(
                  children: [
                    Container(
                      height: 300,
                      width: double.infinity,
                      decoration: BoxDecoration(
                        color: const Color(0xFF2C2C2C),
                        borderRadius: BorderRadius.circular(12),
                        border: Border.all(color: const Color(0xFF3C3C3C)),
                      ),
                      child: ClipRRect(
                        borderRadius: BorderRadius.circular(12),
                        child: _buildImagePreview(),
                      ),
                    ),
                    const SizedBox(height: 20),
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                      children: [
                        ElevatedButton.icon(
                          onPressed: () => _pickImage(ImageSource.camera),
                          icon: const Icon(Icons.camera_alt),
                          label: const Text('Camera'),
                          style: ElevatedButton.styleFrom(
                            backgroundColor: const Color(0xFF333333),
                          ),
                        ),
                        ElevatedButton.icon(
                          onPressed: () => _pickImage(ImageSource.gallery),
                          icon: const Icon(Icons.photo_library),
                          label: const Text('Gallery'),
                        ),
                      ],
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 24),
            if (_xfile != null || _image != null)
              SizedBox(
                width: double.infinity,
                child: ElevatedButton(
                  onPressed: _isLoading ? null : _predictImage,
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.blueAccent,
                    padding: const EdgeInsets.symmetric(vertical: 16),
                  ),
                  child: const Text(
                    'Analyze Image',
                    style:
                        TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                  ),
                ),
              ),
            _buildResultBox(),
          ],
        ),
      ),
    );
  }
}
