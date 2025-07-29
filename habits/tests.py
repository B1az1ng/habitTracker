from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from datetime import date

from .models import Habit, Completion, Profile

class HabitTrackerTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='pass1234')
        self.client.login(username='testuser', password='pass1234')

    def test_profile_auto_creation(self):
        profile = Profile.objects.get(user=self.user)
        self.assertIsNotNone(profile)
        self.assertFalse(bool(profile.avatar))  # no avatar by default

    def test_profile_avatar_upload(self):
        avatar = SimpleUploadedFile(
            'avatar.png',
            b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR...',
            content_type='image/png'
        )
        url = reverse('profile')

        response = self.client.post(
            url,
            data={},
            files={'avatar': avatar},
            follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Your profile has been updated.')



    def test_habit_crud_and_count_operations(self):
        
        response = self.client.post(reverse('habit-add'), {
            'name': 'Read Books',
            'daily_goal': 2,
        })
        self.assertRedirects(response, reverse('habit-list'))

        habit = Habit.objects.get(user=self.user, name='Read Books')
        self.assertEqual(habit.daily_goal, 2)

        inc_url = reverse('habit-increment', args=[habit.pk])
        self.client.get(inc_url)
        self.client.get(inc_url)
        comp = Completion.objects.get(habit=habit, date=date.today())
        self.assertEqual(comp.count, 2)

        dec_url = reverse('habit-decrement', args=[habit.pk])
        self.client.get(dec_url)
        comp.refresh_from_db()
        self.assertEqual(comp.count, 1)

    def test_habit_delete(self):
        habit = Habit.objects.create(user=self.user, name='Temporary', daily_goal=1)
        delete_url = reverse('habit-delete', args=[habit.pk])

        response = self.client.get(delete_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Delete Habit')

        response = self.client.post(delete_url)
        self.assertRedirects(response, reverse('habit-list'))
        self.assertFalse(Habit.objects.filter(pk=habit.pk).exists())

    def test_habit_list_display_and_progress(self):
        response = self.client.get(reverse('habit-list'))
        self.assertContains(response, "You have no habits yet.")

        Habit.objects.create(user=self.user, name='A', daily_goal=1)
        Habit.objects.create(user=self.user, name='B', daily_goal=1)

        response = self.client.get(reverse('habit-list'))
        self.assertContains(response, 'A')
        self.assertContains(response, 'B')
        self.assertContains(response, 'Progress: 0 / 2')

    def test_registration_and_login_flow(self):
        self.client.logout()

        response = self.client.post(reverse('register'), {
            'username': 'newuser',
            'email': 'new@example.com',
            'password1': 'ComplexPwd!1',
            'password2': 'ComplexPwd!1',
        })
        self.assertRedirects(response, reverse('login'))

        login_response = self.client.post(reverse('login'), {
            'username': 'newuser',
            'password': 'ComplexPwd!1',
        })
        self.assertRedirects(login_response, reverse('habit-list'))
