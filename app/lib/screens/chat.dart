import 'dart:convert';

import 'package:chat_app/widgets/chat_messages.dart';
import 'package:chat_app/widgets/new_message.dart';
import 'package:flutter/material.dart';
import 'package:rx_shared_preferences/rx_shared_preferences.dart';
import 'package:web_socket_channel/io.dart';

final rxPrefs = RxSharedPreferences.getInstance();


class ChatScreen extends StatefulWidget {
  const ChatScreen({super.key});

  @override
  State<ChatScreen> createState() {
    return _ChatScreenState();
  }
}

class _ChatScreenState extends State<ChatScreen> {
  late String? authenticatedUser;
  late String? accessToken;
  final _messagesWebsocket = IOWebSocketChannel.connect(Uri.parse('wss://flutter-chat-app.15lb2f1vk1o3.us-south.codeengine.appdomain.cloud/ws/chat_messages'));
  
  void authWebsocket() async {
    authenticatedUser = await rxPrefs.getString('username');
    accessToken = await rxPrefs.getString('access_token');

    _messagesWebsocket.sink.add(jsonEncode({
      'access_token': accessToken,
    }));
  }

  @override
  void initState() {
    authWebsocket();
    super.initState();
  }

  @override
  void dispose() {
    _messagesWebsocket.sink.close();
    super.dispose();
  }

  // void setupPushNotifications() async {
  //   final fcm = FirebaseMessaging.instance;

  //   await fcm.requestPermission();

  //   // final token = await fcm.getToken();
  //   fcm.subscribeToTopic('chat');
  // }

  // @override
  // void initState() {
  //   super.initState();
  //   setupPushNotifications();
  // }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('FlutterChat'),
        actions: [
          IconButton(
            onPressed: () async {
              rxPrefs.clear();
            },
            icon: Icon(
              Icons.exit_to_app,
              color: Theme.of(context).colorScheme.primary,
            ),
          ),
        ],
      ),
      body: Column(
        children: [
          Expanded(
            child: ChatMessages(
              messagesWebsocket: _messagesWebsocket,
            ),
          ),
          NewMessage(
            messagesWebsocket: _messagesWebsocket,
          ),
        ],
      ),
    );
  }
}
