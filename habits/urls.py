from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.habit_list, name='habit-list'),

    # Authentication
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    
    # Go to profile settings
    path('profile/', views.profile, name='profile'),

    # Habit create, update and delete
    path('habit/add/', views.habit_create, name='habit-add'),
    path('habit/<int:pk>/edit/', views.habit_update, name='habit-edit'),
    path('habit/<int:pk>/delete/', views.habit_delete, name='habit-delete'),

    # Update habit 
    path('habit/<int:pk>/inc/', views.increment_completion, name='habit-increment'),
    path('habit/<int:pk>/dec/', views.decrement_completion, name='habit-decrement'),
]
