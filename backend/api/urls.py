"""
URL configuration for api project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

# media files 경로 설정
from django.conf import settings
from django.conf.urls.static import static
import debug_toolbar
from drf_spectacular.views import ( # Swagger가 제공하는 뷰들
    SpectacularAPIView,        # OpenAPI JSON 스키마
    SpectacularSwaggerView,    # Swagger UI
    SpectacularRedocView,      # Redoc UI (선택)
)

urlpatterns = [
    path('admin/', admin.site.urls),    
    path('api/v1/accounts/signup/', include('dj_rest_auth.registration.urls')),
    path('api/v1/accounts/', include('dj_rest_auth.urls')),
    path('api/v1/users/', include('accounts.urls')), # 인증 관련 경로보다 아래에 위치해야함
    path('api/v1/books/', include('books.urls')),
    path('api/v1/libraries/', include('libraries.urls')),
    path('api/v1/reviews/', include('reviews.urls')),
    path('api/v1/galfies/', include('galfies.urls')),
    path('api/v1/comments/', include('comments.urls')),
    path('api/v1/likes/', include('likes.urls')),
    path('api/recommendations', include('recommendations.urls')),
    # schema (Swagger UI가 이 endpoint를 읽어서 문서를 그림)
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    # swagger UI (브라우저에서 사람이 보는 문서 화면)
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    # redoc UI (브라우저에서 사람이 보는 문서 화면)
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


# debug toolbar를 url에 붙인다. 
# if settings.DEBUG: // 운영환경일 경우 해당 기능 적용 x
urlpatterns += [
    path('__debug__/', include(debug_toolbar.urls)),
]
