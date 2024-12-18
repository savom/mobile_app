import 'package:flutter/material.dart';

class CustomBottomBar extends StatelessWidget {
  final VoidCallback? onHomePressed;

  const CustomBottomBar({
    Key? key,
    this.onHomePressed,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return BottomAppBar(
      color: const Color(0xFFE9E9E9),
      child: Container(
        height: 78,
        alignment: Alignment.center,
        child: IconButton(
          icon: const Icon(Icons.home, size: 30, color: Colors.black),
          onPressed: onHomePressed,
        ),
      ),
    );
  }
}
