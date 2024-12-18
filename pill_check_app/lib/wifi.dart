import 'package:flutter/material.dart';
import 'custom_app_bar.dart';
import 'custom_bottom_bar.dart';
import 'main_home.dart';
// 네트워크 서비스 추가

class WifiDisconnectedPage extends StatelessWidget {
  final String userId;

  const WifiDisconnectedPage({super.key, required this.userId});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: CustomAppBar(
        title: 'Pill Check',
        onBackPressed: () {
          Navigator.pushReplacement(
            context,
            MaterialPageRoute(builder: (context) => MainHomePage(userId: userId)),
          );
        },
      ),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(Icons.wifi_off, size: 120, color: Colors.red),
            const SizedBox(height: 20),
            const Text(
              '인터넷 연결이 끊어졌습니다.\n연결을 확인하고 다시 시도하세요.',
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 30),
                   ],
        ),
      ),
      bottomNavigationBar: CustomBottomBar(
        onHomePressed: () {
          Navigator.pushReplacement(
            context,
            MaterialPageRoute(builder: (context) => MainHomePage(userId: userId)),
          );
        },
      ),
    );
  }
}
