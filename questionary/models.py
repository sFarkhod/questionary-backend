from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from datetime import timedelta

# We use default User model from Django
class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


# For permanently storing password recovery code
class PasswordResetCode(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=6, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(minutes=10)
        super().save(*args, **kwargs)

    def is_expired(self):
        return timezone.now() > self.expires_at

    def __str__(self):
        return f'{self.user.email} - {self.code}'


# Subject model
class Subject(BaseModel):
    name = models.CharField(max_length=255)


# Teacher model
class Teacher(BaseModel):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    subjects = models.ManyToManyField(Subject)


# Question model 
class Question(BaseModel):
    name = models.CharField(max_length=255)


# Questionary model. Storing all data about questionary
class Questionary(BaseModel):
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    questions = models.JSONField()  
    choice = models.CharField(max_length=20, choices=[('anonym', 'Anonym'), ('not anonym', 'Not Anonym')])
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)

    def save(self, *args, **kwargs):
        if self.choice == 'anonym':
            anonym_user, created = User.objects.get_or_create(username='anonym', defaults={'password': 'anonym'})
            self.user = anonym_user
        super().save(*args, **kwargs)
