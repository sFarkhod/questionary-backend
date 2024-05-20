"""
URL configuration for questionary project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
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
from django.urls import path

from django.urls import re_path
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.conf import settings
from django.conf.urls.static import static

from questionary.views import QuestionCreateView, QuestionListCreateView, QuestionListView, RegisterView, LoginView, PasswordResetConfirmView, PasswordResetRequestView, SubjectCreateView, SubjectListCreateView, SubjectListView, TeacherCreateView, TeacherListCreateView, TeacherListView, UserCreateView, UserDetailView

schema_view = get_schema_view(
   openapi.Info(
      title="Questionary",
      default_version='v1',
      description="Questionary app",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="contact@snippets.local"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)


urlpatterns = [
    # path('admin/', admin.site.urls),

    # register and login for User and Admin
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('confirm-code/', PasswordResetRequestView.as_view(), name='reset-password'),
    path('reset-password/', PasswordResetConfirmView.as_view(), name='reset-password-confirm'),

    # Helpers (Not Paginated data)
    path('subjects/', SubjectListView.as_view(), name='subject-list'),
    path('teachers/', TeacherListView.as_view(), name='teacher-list'),
    path('questions/', QuestionListView.as_view(), name='teacher-list'),

    # admin views
    path('admin/subjects/', SubjectListCreateView.as_view(), name='subject-list-create'),
    path('admin/subjects/<int:pk>/', SubjectCreateView.as_view(), name='subject-detail'),
    path('admin/teachers/', TeacherListCreateView.as_view(), name='teacher-list-create'),
    path('admin/teachers/<int:pk>/', TeacherCreateView.as_view(), name='teacher-detail'),
    path('admin/questions/', QuestionListCreateView.as_view(), name='teacher-list-create'),
    path('admin/questions/<int:pk>/', QuestionCreateView.as_view(), name='teacher-detail'),
    path('admin/users/', UserCreateView.as_view(), name='user-create'),
    path('admin/users/<int:pk>/', UserDetailView.as_view(), name='user-update-delete'),


    # swagger
    path('swagger<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
