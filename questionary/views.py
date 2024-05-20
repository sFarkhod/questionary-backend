from django.contrib.auth.models import User

from .models import Question, Subject, Teacher
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated, AllowAny
from .serializers import QuestionSerializer, SubjectListSerializer, UserCreateUpdateSerializer, UserSerializer, LoginSerializer, PasswordResetRequestSerializer, PasswordResetConfirmSerializer, TeacherSerializer
from .permissions import IsAdminUser

# Register View (only POST)
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

# Login View (only POST)
class LoginView(APIView):
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data
        refresh = RefreshToken.for_user(user)
        return Response({
            "is_Admin": user.is_staff,
            "token": {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
            })


# Confirmation Code View (only POST)
class PasswordResetRequestView(APIView):
    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"message": "Password reset code sent to your email."}, status=status.HTTP_200_OK)


# Reset Password (only POST)
class PasswordResetConfirmView(APIView):
    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"message": "Password reset successful."}, status=status.HTTP_200_OK)


# Subject list (only GET, no authentication required)
class SubjectListView(generics.ListAPIView):
    queryset = Subject.objects.all()
    serializer_class = SubjectListSerializer
    permission_classes = [AllowAny]
    pagination_class = None


# Subject list
class SubjectListCreateView(generics.ListCreateAPIView):
    queryset = Subject.objects.all()
    serializer_class = SubjectListSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    

# Subject CRUD
class SubjectCreateView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Subject.objects.all()
    serializer_class = SubjectListSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]


# Teacher list (only GET, no authentication required)
class TeacherListView(generics.ListAPIView):
    queryset = Teacher.objects.all()
    serializer_class = TeacherSerializer
    permission_classes = [AllowAny]
    pagination_class = None


# Teacher list and create
class TeacherListCreateView(generics.ListCreateAPIView):
    queryset = Teacher.objects.all()
    serializer_class = TeacherSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]


# Teacher CRUD
class TeacherCreateView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Teacher.objects.all()
    serializer_class = TeacherSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]


# Question list (only GET, no authentication required)
class QuestionListView(generics.ListAPIView):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    permission_classes = [AllowAny]
    pagination_class = None


# Question list and create
class QuestionListCreateView(generics.ListCreateAPIView):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]


# Question CRUD
class QuestionCreateView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]


# User Create and List
class UserCreateView(generics.ListCreateAPIView):
    queryset = User.objects.filter(is_superuser=False).filter(is_staff=True).order_by('id')
    serializer_class = UserCreateUpdateSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get_queryset(self):
        return User.objects.exclude(is_superuser=True).order_by('id')

    def create(self, request, *args, **kwargs):
        if request.user.is_superuser:
            return super().create(request, *args, **kwargs)
        else:
            return Response({"message": "You do not have permission to perform this action."}, status=status.HTTP_403_FORBIDDEN)

    
# UserUpdateDelete
class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.exclude(is_superuser=True)
    serializer_class = UserCreateUpdateSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

    def update(self, request, *args, **kwargs):
        if request.user.is_superuser:
            return super().update(request, *args, **kwargs)
        else:
            return Response({"message": "You do not have permission to perform this action."}, status=status.HTTP_403_FORBIDDEN)

    def destroy(self, request, *args, **kwargs):
        if request.user.is_superuser:
            return super().destroy(request, *args, **kwargs)
        else:
            return Response({"message": "You do not have permission to perform this action."}, status=status.HTTP_403_FORBIDDEN)
