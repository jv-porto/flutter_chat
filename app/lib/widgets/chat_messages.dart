import 'dart:convert';
import 'package:chat_app/widgets/message_bubble.dart';
import 'package:flutter/material.dart';
import 'package:rx_shared_preferences/rx_shared_preferences.dart';
import 'package:web_socket_channel/io.dart';

final rxPrefs = RxSharedPreferences.getInstance();

class ChatMessages extends StatefulWidget {
  const ChatMessages({super.key});

  @override
  State<ChatMessages> createState() {
    return _ChatMessagesState();
  }
}

class _ChatMessagesState extends State<ChatMessages> {
  late String? authenticatedUser;
  late String? accessToken;
  final _channel = IOWebSocketChannel.connect(Uri.parse('wss://flutter-chat-app.15lb2f1vk1o3.us-south.codeengine.appdomain.cloud/ws/chat_messages'));
  
  void authWebsocket() async {
    authenticatedUser = await rxPrefs.getString('username');
    accessToken = await rxPrefs.getString('access_token');

    _channel.sink.add(jsonEncode({
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
    _channel.sink.close();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return StreamBuilder(
      stream: _channel.stream,
      builder: (ctx, chatSnapshots) {
        if (chatSnapshots.connectionState == ConnectionState.waiting) {
          return const Center(
            child: CircularProgressIndicator(),
          );
        }

        final List<dynamic> loadedMessages = jsonDecode(chatSnapshots.data);

        if (!chatSnapshots.hasData || loadedMessages.isEmpty) {
          return const Center(
            child: Text('No messages found'),
          );
        }

        if (chatSnapshots.hasError) {
          return const Center(
            child: Text('Something went wrong...'),
          );
        }

        return ListView.builder(
          padding: const EdgeInsets.only(
            bottom: 40,
            left: 13,
            right: 13,
          ),
          reverse: true,
          itemCount: loadedMessages.length,
          itemBuilder: (ctx, index) {
            final chatMessage = loadedMessages[index];
            final nextChatMessage = index + 1 < loadedMessages.length
                ? loadedMessages[index + 1]
                : null;

            final currentMessageUsername = chatMessage['user_username'];
            final nextMessageUsername = nextChatMessage != null
                ? nextChatMessage['user_username']
                : null;
            final nextUserIsSame = nextMessageUsername == currentMessageUsername;

            if (nextUserIsSame) {
              return MessageBubble.next(
                message: chatMessage['text'],
                isMe: authenticatedUser == currentMessageUsername,
              );
            } else {
              return MessageBubble.first(
                userImage: chatMessage['userImage'],
                username: chatMessage['user_username'],
                message: chatMessage['text'],
                isMe: authenticatedUser == currentMessageUsername,
              );
            }
          },
        );
      },
    );
  }
}
