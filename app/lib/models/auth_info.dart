class AuthInfo {
  const AuthInfo({
    required this.accessToken,
    required this.refreshToken,
    required this.tokenType,
    required this.receivedAt,
    required this.username,
  });

  final String accessToken;
  final String refreshToken;
  final String tokenType;
  final DateTime receivedAt;
  final String username;

  static AuthInfo fromJson(Map<String, dynamic> json) {
    return AuthInfo(
      accessToken: json['access_token'] as String,
      refreshToken: json['refresh_token'] as String,
      tokenType: json['token_type'] as String,
      receivedAt: DateTime.now().toUtc(),
      username: json['username'] as String,
    );
  }

  static Map<String, dynamic> toMap(AuthInfo authInfo) {
    final Map<String, dynamic> mapInfo = {
      'accessToken': authInfo.accessToken,
      'refreshToken': authInfo.refreshToken,
      'tokenType': authInfo.tokenType,
      'receivedAt': authInfo.receivedAt,
      'username': authInfo.username,
    };
    return mapInfo;
  }

}
