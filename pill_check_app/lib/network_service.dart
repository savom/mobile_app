import 'package:connectivity_plus/connectivity_plus.dart';
import 'package:flutter/material.dart';


class NetworkService {
  /// 네트워크 연결을 확인하는 메서드
  static Future<bool> checkNetworkConnectivity(BuildContext context) async {
    var connectivityResult = await Connectivity().checkConnectivity();
    if (connectivityResult == ConnectivityResult.none) {
      // 네트워크 연결이 끊어졌을 때 Snackbar 표시
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('네트워크에 연결되지 않았습니다. 인터넷 연결을 확인해주세요.'),
          duration: Duration(seconds: 3),
        ),
      );
      return false;
    } else {
      return true;
    }
  }
}
