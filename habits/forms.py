from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Profile, Habit

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['avatar']

class HabitForm(forms.ModelForm):
    class Meta:
        model = Habit
        fields = ['name', 'daily_goal']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter habit name'
            }),
            'daily_goal': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Times per day'
            }),
        }
        labels = {
            'name': 'Habit Name',
            'daily_goal': 'Daily Goal',
        }
