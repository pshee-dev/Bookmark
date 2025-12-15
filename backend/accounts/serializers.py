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


# [User Detail] 로그인 된 사용자 정보 GET, PUT, PATCH 가능한 시리얼라이저
class CustomUserDetailsSerializer(UserDetailsSerializer):

    class Meta():        
        model = User
        fields = ('id', 'username', 'last_name', 'first_name', 'email', 'profile_img')
        read_only_fields = ('username',)