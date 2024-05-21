from django.contrib.auth.models import User

from .models import Question, Questionary, Subject, Teacher
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated, AllowAny
from .serializers import QuestionSerializer, QuestionarySerializer, SubjectListSerializer, UserCreateUpdateSerializer, UserSerializer, LoginSerializer, PasswordResetRequestSerializer, PasswordResetConfirmSerializer, TeacherSerializer
from .permissions import IsAdminUser
from rest_framework.decorators import api_view, permission_classes
from datetime import datetime, timedelta
from django.db.models import Count, Avg
from django.utils import timezone
import calendar



ANSWER_VALUES = {
    "Strongly Agree": 6,
    "Agree": 5,
    "Slightly Agree": 4,
    "Slightly Disagree": 3,
    "Disagree": 2,
    "Strongly Disagree": 1,
}


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


# Questionary Create View
class QuestionaryCreateView(generics.CreateAPIView):
    queryset = Questionary.objects.all()
    serializer_class = QuestionarySerializer


# Questionary List 
@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminUser])
def questionary_list(request):
    questionaries = Questionary.objects.all()
    serializer = QuestionarySerializer(questionaries, many=True)
    return Response(serializer.data)


# Questionary Delete
@api_view(['DELETE'])
@permission_classes([IsAuthenticated, IsAdminUser])
def questionary_delete(request, pk):
    try:
        questionary = Questionary.objects.get(pk=pk)
        questionary.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    except Questionary.DoesNotExist:
        return Response({"error": "Questionary not found"}, status=status.HTTP_404_NOT_FOUND)


# Rating Stats View
@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminUser])
def rating_stats(request):
    teacher_id = request.headers.get('teacher-id')
    chart_type = request.headers.get('type')
    filter_date = request.GET.get('date')
    user_start_date = request.GET.get('start_date')
    user_end_date = request.GET.get('end_date')

    if not teacher_id or not chart_type:
        return Response({"error": "teacher_id and type are required in headers"}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        teacher = Teacher.objects.get(pk=teacher_id)
    except Teacher.DoesNotExist:
        return Response({"error": "Teacher not found"}, status=status.HTTP_404_NOT_FOUND)

    questionaries = Questionary.objects.filter(teacher=teacher)
    
    if chart_type != 'pie_chart':
        if filter_date == 'monthly':
            current_month = timezone.now().month
            if user_start_date == None or user_end_date == None:
                start_date = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
                end_date = start_date + timedelta(days=calendar.monthrange(start_date.year, start_date.month)[1])
            else:
                start_date = datetime.strptime(user_start_date, '%d-%m-%Y').date().strftime('%Y-%m-%d')
                end_date = datetime.strptime(user_end_date, '%d-%m-%Y').date().strftime('%Y-%m-%d')
            questionaries = questionaries.filter(created_at__range=[start_date, end_date])

        elif filter_date == 'yearly':
            current_year = timezone.now().year
            if user_start_date == None or user_end_date == None:
                start_date = timezone.datetime(current_year, 1, 1)
                end_date = timezone.datetime(current_year, 12, 31, 23, 59, 59)
            else:
                start_date = datetime.strptime(user_start_date, '%d-%m-%Y').date().strftime('%Y-%m-%d')
                end_date = datetime.strptime(user_end_date, '%d-%m-%Y').date().strftime('%Y-%m-%d')
            questionaries = questionaries.filter(created_at__range=[start_date, end_date])
        else:
            return Response({"error": "Invalid date filter"}, status=status.HTTP_400_BAD_REQUEST)
        questionaries = questionaries.filter(created_at__gte=start_date)

    if chart_type == 'pie_chart':
        answer_counts = {}
        total_answers = 0

        for questionary in questionaries:
            questions = questionary.questions
            for question_dict in questions:
                answer = question_dict.get('answer')
                if answer:
                    total_answers += 1
                    if answer in answer_counts:
                        answer_counts[answer] += 1
                    else:
                        answer_counts[answer] = 1

        response_data = {
            "rating": [{"name": answer, "percentage": (count / total_answers) * 100} for answer, count in answer_counts.items()]
        }
    elif chart_type in ['line_chart', 'bar_chart']:
        ratings = {}
        for questionary in questionaries:
            created_at = questionary.created_at
            questions = questionary.questions
            for question_dict in questions:
                answer = question_dict.get('answer')
                if answer:
                    date_str = created_at.strftime("%d-%m-%Y") 
                    if answer not in ratings:
                        ratings[answer] = {}
                    if date_str in ratings[answer]:
                        ratings[answer][date_str] += 1
                    else:
                        ratings[answer][date_str] = 1

        response_data = {
            "rating": [{"name": answer, "quantity": quantity, "date": date} for answer, dates in ratings.items() for date, quantity in dates.items()]
        }
    else:
        return Response({"error": "Invalid chart type"}, status=status.HTTP_400_BAD_REQUEST)

    return Response(response_data)


# User Stats View
@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminUser])
def user_stats(request):
    teacher_id = request.headers.get('teacher-id')

    if not teacher_id:
        return Response({"error": "teacher_id is required in headers"}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        teacher = Teacher.objects.get(pk=teacher_id)
    except Teacher.DoesNotExist:
        return Response({"error": "Teacher not found"}, status=status.HTTP_404_NOT_FOUND)

    questionaries = Questionary.objects.filter(teacher=teacher)

    total_questionaries = questionaries.count()
    if total_questionaries == 0:
        return Response({"error": "No questionaries found for the specified teacher"}, status=status.HTTP_404_NOT_FOUND)

    anonym_count = questionaries.filter(choice='anonym').count()
    non_anonym_count = total_questionaries - anonym_count

    anonym_percentage = (anonym_count / total_questionaries) * 100
    non_anonym_percentage = (non_anonym_count / total_questionaries) * 100

    response_data = {
        "rating": {
            "anonym": anonym_percentage,
            "not-anonym": non_anonym_percentage
        }
    }

    return Response(response_data)



# User Table Stat
@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminUser])
def user_table_stats(request):
    teacher_id = request.headers.get('teacher-id')

    if not teacher_id:
        return Response({"error": "teacher_id is required in headers"}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        teacher = Teacher.objects.get(pk=teacher_id)
    except Teacher.DoesNotExist:
        return Response({"error": "Teacher not found"}, status=status.HTTP_404_NOT_FOUND)

    questionaries = Questionary.objects.filter(teacher=teacher).select_related('user')

    response_data = []
    
    for questionary in questionaries:
        user = questionary.user
        questions = questionary.questions

        total_rating = 0
        num_answers = 0

        for question in questions:
            answer = question.get('answer')
            if answer in ANSWER_VALUES:
                total_rating += ANSWER_VALUES[answer]
                num_answers += 1
        
        if num_answers > 0:
            average_rating = total_rating / num_answers
        else:
            average_rating = 0

        response_data.append({
            "username": user.username,
            "rating": average_rating,
            "timestamp": questionary.created_at.strftime("%Y-%m-%d %H:%M:%S")
        })

    return Response(response_data, status=status.HTTP_200_OK)