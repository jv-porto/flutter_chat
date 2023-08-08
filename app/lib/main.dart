import 'package:chat_app/api.dart';
import 'package:chat_app/screens/auth.dart';
import 'package:chat_app/screens/chat.dart';
import 'package:chat_app/screens/splash.dart';
import 'package:flutter/material.dart';
import 'package:rx_shared_preferences/rx_shared_preferences.dart';

final rxPrefs = RxSharedPreferences.getInstance();


void main() async {
  runApp(const App());
}


class App extends StatelessWidget {
  const App({super.key});

  void init() async {
    // await rxPrefs.clear();
    await API.auth.reauth();
  }

  @override
  Widget build(BuildContext context) {
    init();

    return MaterialApp(
      title: 'FlutterChat',
      theme: ThemeData().copyWith(
        useMaterial3: true,
        colorScheme: ColorScheme.fromSeed(
            seedColor: const Color.fromARGB(255, 63, 17, 177)),
      ),
      home: StreamBuilder(
        stream: rxPrefs.getStringStream('username').asBroadcastStream(),
        builder: (ctx, snapshot) {
          if (snapshot.connectionState == ConnectionState.waiting) {
            return const SplashScreen();
          }

          if (snapshot.hasData) {
            return const ChatScreen();
          }

          return const AuthScreen();
        },
      ),
    );
  }
}
