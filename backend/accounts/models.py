from django.contrib.auth.models import AbstractUser
from django.db import models

# profile_image 저장 시 username으로 구분된 경로를 설정하기 위한 함수
def profile_image_path(instance, filename):
    return f'user/{instance.username}/{filename}'

class User(AbstractUser):
    followings = models.ManyToManyField('self', symmetrical=False, related_name='followers')
    profile_img = models.ImageField(upload_to=profile_image_path, blank=True)

    def __str__(self):
        return f'{self.last_name}{self.first_name}'
    
    @property
    def full_name(self):
        return f'{self.last_name}{self.first_name}'