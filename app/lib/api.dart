import 'dart:io';
import 'dart:convert';
import 'package:chat_app/models/auth_info.dart';
import 'package:chat_app/models/user.dart';
import 'package:http/http.dart' as http;
import 'package:rx_shared_preferences/rx_shared_preferences.dart';

final rxPrefs = RxSharedPreferences.getInstance();

const apiUrl = 'https://flutter-chat-app.15lb2f1vk1o3.us-south.codeengine.appdomain.cloud/api';
bool _reauthing = false;


Future<AuthInfo> _setTokenFromJson(json) async {
  final Map<String, dynamic> filteredJson = Map.from(json);
  filteredJson.removeWhere((key, value) => (value == null || value == ''));

  if (!filteredJson.containsKey('access_token')) {
    filteredJson['access_token'] = await rxPrefs.getString('access_token');
  }
  if (!filteredJson.containsKey('refresh_token')) {
    filteredJson['refresh_token'] = await rxPrefs.getString('refresh_token');
  }
  if (!filteredJson.containsKey('username')) {
    filteredJson['username'] = await rxPrefs.getString('username');
  }

  final authInfo = AuthInfo(
    accessToken: filteredJson['access_token'] as String,
    refreshToken: filteredJson['refresh_token'] as String,
    tokenType: 'Bearer',
    receivedAt: DateTime.now().toUtc(),
    username: filteredJson['username'] as String,
  );


  await rxPrefs.setString('access_token', authInfo.accessToken);
  await rxPrefs.setString('refresh_token', authInfo.refreshToken);
  await rxPrefs.setString('token_type', authInfo.tokenType);
  await rxPrefs.setString('received_at', authInfo.receivedAt.toIso8601String());
  await rxPrefs.setString('username', authInfo.username);

  final currentUserInfo = API.auth.getCurrentUser();

  final user = User(
    username: currentUserInfo['username'] as String,
    email: currentUserInfo['email'] as String,
    firstName: currentUserInfo['first_name'] as String,
    lastName: currentUserInfo['last_name'] as String,
    imageUrl: currentUserInfo['image_url'] as String,
    isEnabled: currentUserInfo['is_enabled'] as bool,
  );

  await rxPrefs.setString('username', user.username);
  await rxPrefs.setString('email', user.email);
  await rxPrefs.setString('first_name', user.firstName);
  await rxPrefs.setString('last_name', user.lastName);
  await rxPrefs.setString('image_url', user.imageUrl);
  await rxPrefs.setBool('is_enabled', user.isEnabled);

  return authInfo;
}


class API {
  static ApiAuth auth = const ApiAuth();
  static ApiChatMessage chatMessage = const ApiChatMessage();
  static ApiUser user = const ApiUser();

  static get reauthing {return _reauthing;}

  static Future<Map<String, String>> get headers async {
    final accessToken = await rxPrefs.getString('access_token');

    return {
      HttpHeaders.authorizationHeader: 'Bearer $accessToken',
    };
  }

  static Future<Map<String, String>> get refreshHeaders async {
    final refreshToken = await rxPrefs.getString('refresh_token');

    return {
      HttpHeaders.authorizationHeader: 'Bearer $refreshToken',
    };
  }

  static Future<Map<String, String>> get jsonHeaders async {
    final accessToken = await rxPrefs.getString('access_token');

    return {
      HttpHeaders.authorizationHeader: 'Bearer $accessToken',
      HttpHeaders.contentTypeHeader: 'application/json',
    };
  }

  static Map<Symbol, dynamic> _symbolizeKeys(Map map){
    return map.map((k, v) => MapEntry(Symbol(k), v));
  }

  static evaluateResponse({required http.Response response, required Map<String, dynamic> pointer}) async {
    try {
      if (response.statusCode == 200) {
        final jsonResponse = jsonDecode(response.body);

        _reauthing = false;
        // print(jsonResponse);
        return jsonResponse;
      } else {
        final responseInfo = {
          'status_code': response.statusCode,
          'response': response.body,
        };

        try {
          final responseMap = Map<String, dynamic>.from(jsonDecode(responseInfo['response'] as String));

          if (responseMap.containsKey('detail') &&
              responseMap['detail'] == 'Signature has expired.') {
            return null;
          }

          final reauthResponse = await API.auth.reauth();

          if (_reauthing || reauthResponse.runtimeType != AuthInfo) {
            _reauthing = false;
            print('1 $responseInfo');
            return responseInfo;
          }

          _reauthing = true;
          final kwargs = API._symbolizeKeys(pointer['params'] as Map);
          await Function.apply(pointer['func'] as Function, [], kwargs);
        } catch (error) {
          _reauthing = false;
          print('2 $error');
          return responseInfo;
        }
      }
    } catch (error) {
      _reauthing = false;
      print('3 $error');
      return null;
    }
  }
}

class ApiAuth {
  const ApiAuth();

  auth({required String username, required String password}) async {
    final url = Uri.parse('$apiUrl/auth/login');

    final response = await http.post(
      url,
      headers: await API.jsonHeaders,
      body: jsonEncode({
        'username': username,
        'password': password,
      }),
    );

    try {
      if (response.statusCode == 200) {
        final jsonResponse = jsonDecode(response.body);
        jsonResponse['username'] = username;

        final authInfo = await _setTokenFromJson(jsonResponse);

        return authInfo;
      } else {
        return {
          'status_code': response.statusCode,
          'response': response.body,
        };
      }
    } catch (error) {
      return null;
    }
  }

  reauth() async {
    print('reauthing...');

    final url = Uri.parse('$apiUrl/auth/update_token');

    final response = await http.get(
      url,
      headers: await API.refreshHeaders,
    );

    try {
      if (response.statusCode == 200) {
        final jsonResponse = jsonDecode(response.body);

        if (jsonResponse.containsKey('detail') &&
            jsonResponse['detail'] == 'Signature has expired.') {
          print('logging out...');
          return null;
          // await logout();
        }

        final authInfo = await _setTokenFromJson(jsonResponse);

        return authInfo;
      } else {
        final jsonResponse = jsonDecode(response.body);

        if (jsonResponse.containsKey('detail') && jsonResponse['detail'] == 'No user found with this username.') {
          print('logging out...');
          // await logout();
        }

        return {
          'status_code': response.statusCode,
          'response': response.body,
        };
      }
    } catch (error) {
      return null;
    }
  }

  // logout() async {}

  getCurrentUser() async {
    final url = Uri.parse('$apiUrl/auth/me');

    final response = await http.get(
      url,
      headers: await API.headers,
    );

    final pointer = {'func': getCurrentUser, 'params': {}};
    API.evaluateResponse(response: response, pointer: pointer);
  }

  // readUsersMe() async {}

  // readOwnItems() async {}
}

class ApiChatMessage {
  const ApiChatMessage();

  post({required String message, required String username}) async {
    final url = Uri.parse('$apiUrl/chat_message');

    final response = await http.post(
      url,
      headers: await API.jsonHeaders,
      body: jsonEncode({
        'text': message,
        'user_username': username,
      }),
    );

    final pointer = {'func': post, 'params': {'message': message, 'username': username}};
    API.evaluateResponse(response: response, pointer: pointer);
  }

  get({required String id}) async {
    final url = Uri.parse('$apiUrl/chat_message/$id');

    final response = await http.get(
      url,
      headers: await API.headers,
    );

    final pointer = {'func': get, 'params': {'id': id}};
    API.evaluateResponse(response: response, pointer: pointer);
  }

  getAll() async {
    final url = Uri.parse('$apiUrl/chat_messages');

    final response = await http.get(
      url,
      headers: await API.headers,
    );

    final pointer = {'func': getAll, 'params': {}};
    API.evaluateResponse(response: response, pointer: pointer);
  }

  getAllAvailable() async {
    final url = Uri.parse('$apiUrl/chat_messages/available');

    final response = await http.get(
      url,
      headers: await API.headers,
    );

    final pointer = {'func': getAllAvailable, 'params': {}};
    API.evaluateResponse(response: response, pointer: pointer);
  }

  patch({required String id, required String message}) async {
    final url = Uri.parse('$apiUrl/chat_message/$id');

    final response = await http.patch(
      url,
      headers: await API.jsonHeaders,
      body: jsonEncode({
        'text': message,
      }),
    );

    final pointer = {'func': patch, 'params': {'id': id, 'message': message}};
    API.evaluateResponse(response: response, pointer: pointer);
  }

  toggleHide({required String id}) async {
    final url = Uri.parse('$apiUrl/chat_message/$id/toggle_hide');

    final response = await http.get(
      url,
      headers: await API.headers,
    );

    final pointer = {'func': toggleHide, 'params': {'id': id}};
    API.evaluateResponse(response: response, pointer: pointer);
  }

  delete({required String id}) async {
    final url = Uri.parse('$apiUrl/chat_message/$id');

    final response = await http.delete(
      url,
      headers: await API.headers,
    );

    final pointer = {'func': delete, 'params': {'id': id}};
    API.evaluateResponse(response: response, pointer: pointer);
  }
}

class ApiUser {
  const ApiUser();

  post({required String username, required String email, required String password, required String firstName, required String lastName, String? imageUrl}) async {
    final url = Uri.parse('$apiUrl/user');

    final response = await http.post(
      url,
      headers: await API.jsonHeaders,
      body: jsonEncode({
        'username': username,
        'email': email,
        'password': password,
        'first_name': firstName,
        'last_name': lastName,
        'image_url': imageUrl,
      }),
    );

    final pointer = {'func': post, 'params': {'username': username, 'email': email, 'password': password, 'firstName': firstName, 'lastName': lastName, 'imageUrl': imageUrl}};
    API.evaluateResponse(response: response, pointer: pointer);
  }

  get({required String username}) async {
    final url = Uri.parse('$apiUrl/user/$username');

    final response = await http.get(
      url,
      headers: await API.headers,
    );

    final pointer = {'func': get, 'params': {'username': username}};
    API.evaluateResponse(response: response, pointer: pointer);
  }

  getAll() async {
    final url = Uri.parse('$apiUrl/users');

    final response = await http.get(
      url,
      headers: await API.headers,
    );

    final pointer = {'func': getAll, 'params': {}};
    API.evaluateResponse(response: response, pointer: pointer);
  }

  getAllAvailable() async {
    final url = Uri.parse('$apiUrl/users/available');

    final response = await http.get(
      url,
      headers: await API.headers,
    );

    final pointer = {'func': getAllAvailable, 'params': {}};
    API.evaluateResponse(response: response, pointer: pointer);
  }

  patch({required String username, String? usernameToChange, String? email, String? password, String? firstName, String? lastName, String? imageUrl}) async {
    final url = Uri.parse('$apiUrl/user/$username');

    final response = await http.patch(
      url,
      headers: await API.jsonHeaders,
      body: jsonEncode({
        'username': usernameToChange,
        'email': email,
        'password': password,
        'first_name': firstName,
        'last_name': lastName,
        'image_url': imageUrl,
      }),
    );

    final pointer = {'func': patch, 'params': {'username': username, 'email': email, 'password': password, 'firstName': firstName, 'lastName': lastName, 'imageUrl': imageUrl}};
    API.evaluateResponse(response: response, pointer: pointer);
  }

  toggleEnable({required String username}) async {
    final url = Uri.parse('$apiUrl/user/$username/toggle_enable');

    final response = await http.get(
      url,
      headers: await API.headers,
    );

    final pointer = {'func': toggleEnable, 'params': {'username': username}};
    API.evaluateResponse(response: response, pointer: pointer);
  }

  delete({required String username}) async {
    final url = Uri.parse('$apiUrl/user/$username');

    final response = await http.delete(
      url,
      headers: await API.headers,
    );

    final pointer = {'func': delete, 'params': {'username': username}};
    API.evaluateResponse(response: response, pointer: pointer);
  }
}
