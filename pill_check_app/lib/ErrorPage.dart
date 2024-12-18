import 'package:flutter/material.dart';
import 'custom_app_bar.dart'; // CustomAppBar 컴포넌트 불러오기
import 'custom_bottom_bar.dart'; // CustomBottomBar 컴포넌트 불러오기
import 'main_home.dart'; // MainHomePage를 import
import 'entry_point.dart'; // SettingsPage를 import

class ErrorPage extends StatelessWidget {
  final String userId; // 사용자 ID 필드 추가

  const ErrorPage({super.key, required this.userId});

  @override
  Widget build(BuildContext context) {
    return ValueListenableBuilder(
      valueListenable: ThemeState.backgroundColor,
      builder: (context, backgroundColor, child) {
        return ValueListenableBuilder(
          valueListenable: ThemeState.textColor,
          builder: (context, textColor, child) {
            return ValueListenableBuilder(
              valueListenable: ThemeState.textSize,
              builder: (context, textSize, child) {
                return ValueListenableBuilder(
                  valueListenable: ThemeState.fontIndex,
                  builder: (context, fontIndex, child) {
                    final fonts = ['Default', 'Serif', 'Monospace'];
                    return Scaffold(
                      appBar: CustomAppBar(
                        title: 'Pill Check',
                        onBackPressed: () {
                          Navigator.pushReplacement(
                            context,
                            MaterialPageRoute(
                              builder: (context) => MainHomePage(userId: userId),
                            ),
                          );
                        },
                      ),
                      body: Stack(
                        children: [
                          Positioned.fill(
                            child: Container(
                              color: backgroundColor, // 배경색
                            ),
                          ),
                          Center(
                            child: Column(
                              mainAxisAlignment: MainAxisAlignment.center,
                              crossAxisAlignment: CrossAxisAlignment.center,
                              children: [
                                Icon(
                                  Icons.error_outline,
                                  size: 80,
                                  color: textColor,
                                ),
                                const SizedBox(height: 20),
                                Text(
                                  '불러온 이미지가 부정확하거나\n검색 결과가 없습니다',
                                  textAlign: TextAlign.center,
                                  style: TextStyle(
                                    fontSize: textSize,
                                    fontWeight: FontWeight.bold,
                                    color: textColor,
                                    fontFamily: fonts[fontIndex] == 'Default'
                                        ? null
                                        : fonts[fontIndex],
                                  ),
                                ),
                                const SizedBox(height: 30),
                                ElevatedButton.icon(
                                  onPressed: () {
                                    // 갤러리에서 사진 다시 불러오기 기능 (추후 구현)
                                  },
                                  style: ElevatedButton.styleFrom(
                                    backgroundColor: const Color(0xFFB2E9E9),
                                    padding: const EdgeInsets.symmetric(
                                      horizontal: 40.0,
                                      vertical: 32.0,
                                    ),
                                  ),
                                  icon: const Icon(
                                    Icons.camera_alt,
                                    color: Colors.black,
                                  ),
                                  label: Text(
                                    '사진 불러오기',
                                    style: TextStyle(
                                      fontSize: textSize,
                                      color: Colors.black,
                                      fontFamily: fonts[fontIndex] == 'Default'
                                          ? null
                                          : fonts[fontIndex],
                                    ),
                                  ),
                                ),
                                const SizedBox(height: 20),
                                Text(
                                  '흐릿하거나 멀리서 찍은 사진은\n구별하기 어려울 수 있어요!',
                                  textAlign: TextAlign.center,
                                  style: TextStyle(
                                    fontSize: textSize * 0.8,
                                    color: textColor.withOpacity(0.6),
                                    fontFamily: fonts[fontIndex] == 'Default'
                                        ? null
                                        : fonts[fontIndex],
                                  ),
                                ),
                              ],
                            ),
                          ),
                          Positioned(
                            bottom: 30,
                            left: 20,
                            child: Row(
                              children: [
                                IconButton(
                                  icon: Icon(
                                    Icons.settings,
                                    color: textColor.withOpacity(0.6),
                                    size: 40,
                                  ),
                                  onPressed: () {
                                    Navigator.push(
                                      context,
                                      MaterialPageRoute(
                                        builder: (context) =>
                                            SettingsPage(userId: userId),
                                      ),
                                    );
                                  },
                                ),
                                const SizedBox(width: 8),
                                GestureDetector(
                                  onTap: () {
                                    Navigator.push(
                                      context,
                                      MaterialPageRoute(
                                        builder: (context) =>
                                            SettingsPage(userId: userId),
                                      ),
                                    );
                                  },
                                  child: Text(
                                    '설정',
                                    style: TextStyle(
                                      fontSize: textSize,
                                      color: textColor.withOpacity(0.6),
                                      fontWeight: FontWeight.bold,
                                      fontFamily: fonts[fontIndex] == 'Default'
                                          ? null
                                          : fonts[fontIndex],
                                    ),
                                  ),
                                ),
                              ],
                            ),
                          ),
                        ],
                      ),
                      bottomNavigationBar: CustomBottomBar(
                        onHomePressed: () {
                          Navigator.pushReplacement(
                            context,
                            MaterialPageRoute(
                              builder: (context) => MainHomePage(userId: userId),
                            ),
                          );
                        },
                      ),
                    );
                  },
                );
              },
            );
          },
        );
      },
    );
  }
}
