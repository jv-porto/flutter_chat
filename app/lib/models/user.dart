class User {
  User({
    required this.username,
    required this.email,
    required this.firstName,
    required this.lastName,
    required this.imageUrl,
    required this.isEnabled,
  });

  final String username;
  final String email;
  final String firstName;
  final String lastName;
  final String imageUrl;
  final bool isEnabled;

  static User fromJson(Map<String, dynamic> json) {
    return User(
      username: json['username'],
      email: json['email'],
      firstName: json['first_name'],
      lastName: json['last_name'],
      imageUrl: json['image_url'],
      isEnabled: json['is_enabled'],
    );
  }

  static Map<String, dynamic> toMap(User user) {
    final Map<String, dynamic> mapInfo = {
      'username': user.username,
      'email': user.email,
      'firstName': user.firstName,
      'lastName': user.lastName,
      'imageUrl': user.imageUrl,
      'isEnabled': user.isEnabled,
    };
    return mapInfo;
  }
}
