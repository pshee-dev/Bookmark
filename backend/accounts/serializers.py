from dj_rest_auth.registration.serializers import RegisterSerializer
from dj_rest_auth.serializers import UserDetailsSerializer, LoginSerializer
from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()

# [Signup] 회원가입 시 필요한 필드 추가
class CustomSignupSerializer(RegisterSerializer):
    last_name = serializers.CharField()
    first_name = serializers.CharField()
    profile_img = serializers.ImageField(required=False)

    def save(self, request):
        user = super().save(request)
        user.last_name = self.validated_data.get('last_name')
        user.first_name = self.validated_data.get('first_name')
        user.profile_img = self.validated_data.get('profile_img')
        user.save()
        return user


# [Login] 로그인 시 사용하지 않는 필드 제거
class CustomLoginSerializer(LoginSerializer):
    email = None


# [User Detail] 로그인 된 사용자 정보 GET, PUT, PATCH 가능 (회원정보 수정)
class CustomUserDetailsSerializer(UserDetailsSerializer):

    class Meta:        
        model = User
        fields = ('id', 'username', 'last_name', 'first_name', 'email', 'profile_img')
        read_only_fields = ('username',)


# [Profile] 유저 프로필 페이지 조회 - GET
class UserProfileSerializer(serializers.ModelSerializer):

    # Todo: reviews_count, galfies_count
    followings_count = serializers.IntegerField(read_only=True)
    followers_count = serializers.IntegerField(read_only=True)
    # reviews_count = serializers.IntegerField(read_only=True)
    # galfies_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = User
        fields = ('last_name', 'first_name', 'profile_img', 'followings_count', 'followers_count')


# [Following/Follower List] 팔로잉/팔로워 리스트 조회 - GET
class FollowListSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('id', 'last_name', 'first_name', 'profile_img')