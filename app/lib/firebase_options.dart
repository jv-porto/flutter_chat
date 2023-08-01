// File generated by FlutterFire CLI.
// ignore_for_file: lines_longer_than_80_chars, avoid_classes_with_only_static_members
import 'package:firebase_core/firebase_core.dart' show FirebaseOptions;
import 'package:flutter/foundation.dart'
    show defaultTargetPlatform, kIsWeb, TargetPlatform;

/// Default [FirebaseOptions] for use with your Firebase apps.
///
/// Example:
/// ```dart
/// import 'firebase_options.dart';
/// // ...
/// await Firebase.initializeApp(
///   options: DefaultFirebaseOptions.currentPlatform,
/// );
/// ```
class DefaultFirebaseOptions {
  static FirebaseOptions get currentPlatform {
    if (kIsWeb) {
      return web;
    }
    switch (defaultTargetPlatform) {
      case TargetPlatform.android:
        return android;
      case TargetPlatform.iOS:
        return ios;
      case TargetPlatform.macOS:
        return macos;
      case TargetPlatform.windows:
        throw UnsupportedError(
          'DefaultFirebaseOptions have not been configured for windows - '
          'you can reconfigure this by running the FlutterFire CLI again.',
        );
      case TargetPlatform.linux:
        throw UnsupportedError(
          'DefaultFirebaseOptions have not been configured for linux - '
          'you can reconfigure this by running the FlutterFire CLI again.',
        );
      default:
        throw UnsupportedError(
          'DefaultFirebaseOptions are not supported for this platform.',
        );
    }
  }

  static const FirebaseOptions web = FirebaseOptions(
    apiKey: 'AIzaSyA9Q7CXfBif1lfVPb2h9rMnqlPXuF994-k',
    appId: '1:545408171424:web:417fa841fe7ddbf71138c5',
    messagingSenderId: '545408171424',
    projectId: 'jvporto-chat-app',
    authDomain: 'jvporto-chat-app.firebaseapp.com',
    storageBucket: 'jvporto-chat-app.appspot.com',
  );

  static const FirebaseOptions android = FirebaseOptions(
    apiKey: 'AIzaSyDjJ96OZM4lZEp5t3FLtJp6MikGaeHnEFg',
    appId: '1:545408171424:android:ec3b882459d9e06e1138c5',
    messagingSenderId: '545408171424',
    projectId: 'jvporto-chat-app',
    storageBucket: 'jvporto-chat-app.appspot.com',
  );

  static const FirebaseOptions ios = FirebaseOptions(
    apiKey: 'AIzaSyDxY4MQ8fhJiuMJO89M4dh5BKFZrI1WArk',
    appId: '1:545408171424:ios:3edb171fc11da7f41138c5',
    messagingSenderId: '545408171424',
    projectId: 'jvporto-chat-app',
    storageBucket: 'jvporto-chat-app.appspot.com',
    iosClientId: '545408171424-joe268vas3mau2n37clkkmns0eh4adq2.apps.googleusercontent.com',
    iosBundleId: 'com.jvporto.chatApp',
  );

  static const FirebaseOptions macos = FirebaseOptions(
    apiKey: 'AIzaSyDxY4MQ8fhJiuMJO89M4dh5BKFZrI1WArk',
    appId: '1:545408171424:ios:045cb293310e49621138c5',
    messagingSenderId: '545408171424',
    projectId: 'jvporto-chat-app',
    storageBucket: 'jvporto-chat-app.appspot.com',
    iosClientId: '545408171424-274s8s4npqtg3kn1s9pbbotcbb044qvo.apps.googleusercontent.com',
    iosBundleId: 'com.example.chatApp.RunnerTests',
  );
}
