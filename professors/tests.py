from datetime import datetime
from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework import status
from django.test import TestCase
from rest_framework.test import APIClient
from django.urls import reverse
from .models import Professors, Timetable
from .serializers import TimetableSerializer

class ProfessorsModelTestCase(APITestCase):
    def setUp(self):
        # Creating a test user
        self.user = User.objects.create_user(
            username='testuser', password='testpassword'
        )
        # Creating a test professor
        self.professor = Professors.objects.create(
            user=self.user,
            firstName='John',
            surname='Doe',
            info='Information about John Doe',
            photo=None,
            tg_username='johndoe',
            tg_idbot='johndoe123',
            phone='+1234567890',
            rate=4.5,
            price={"service": 500},
            language='English',
            experience='1-3',
        )

    def test_model_can_create_a_professor(self):
        """Test the professor model can create a professor."""
        old_count = Professors.objects.count()
        user2 = User.objects.create_user(
            username='testuser2', password='testpassword2'
        )
        professor = Professors.objects.create(
            user=user2,
            firstName='Jane',
            surname='Doe',
            info='Information about Jane Doe',
            photo=None,
            tg_username='janedoe',
            tg_idbot='janedoe123',
            phone='+0987654321',
            rate=4.0,
            price={"service": 700},
            language='Spanish',
            experience='3-5',
        )
        new_count = Professors.objects.count()
        self.assertNotEqual(old_count, new_count)


class ProfessorsViewTestCase(APITestCase):
    def setUp(self):
        # Creating a test user
        self.user = User.objects.create_user(
            username='testuser', password='testpassword'
        )
        # Creating a test professor
        self.professor = Professors.objects.create(
            user=self.user,
            firstName='John',
            surname='Doe',
            info='Information about John Doe',
            photo=None,
            tg_username='johndoe',
            tg_idbot='johndoe123',
            phone='+1234567890',
            rate=4.5,
            price={"service": 500},
            language='English',
            experience='1-3',
        )
        # Authenticate the client
        self.client.login(username='testuser', password='testpassword')

    def test_api_can_get_a_professor(self):
        """Test the api can get a given professor."""
        professor = Professors.objects.get()
        response = self.client.get(f'/professors/{professor.id}/', format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, 'John')


class ModelTimetableTestCase(TestCase):
    """This class defines the test suite for the Timetable model."""

    def setUp(self):
        # Assuming there's a Professor instance created already
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser', password='testpassword'
        )
        self.professor = Professors.objects.create(
            user=self.user,
            firstName='John',
            surname='Doe',
            info='Information about John Doe',
            photo=None,
            tg_username='johndoe',
            tg_idbot='johndoe123',
            phone='+1234567890',
            rate=4.5,
            price={"service": 500},
            language='English',
            experience='1-3',
        )
        self.timetable_data = {'professor': self.professor.id, 'monday': ['9:00', '12:00'], 'tuesday': ['10:00', '12:00']}
        self.professor = Professors.objects.first()
        self.monday = ['9:00', '12:00']
        self.tuesday = ['10:00', '12:00']
        
        
        
    
    def test_model_can_create_a_timetable(self):
        """Test the Timetable model can create a timetable."""
        old_count = Timetable.objects.count()
        Timetable.objects.create(professor=self.professor, monday=self.monday, tuesday=self.tuesday)
        
        new_count = Timetable.objects.count()
        self.assertNotEqual(old_count, new_count)


class ViewTimetableTestCase(TestCase):
    """Test suite for the Timetable views."""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser', password='testpassword'
        )
        self.professor = Professors.objects.create(
            user=self.user,
            firstName='John',
            surname='Doe',
            info='Information about John Doe',
            photo=None,
            tg_username='johndoe',
            tg_idbot='johndoe123',
            phone='+1234567890',
            rate=4.5,
            price={"service": 500},
            language='English',
            experience='1-3',
        )
        self.monday = ['09:00:00', '12:00:00']
        self.tuesday = ['10:00:00', '12:00:00']
        self.timetable_data = {'professor': self.professor.id, 'monday': self.monday, 'tuesday': self.tuesday}
        self.response = self.client.post(
            reverse('timetable-list'),
            self.timetable_data,
            format="json")

    def test_model_can_create_a_timetable(self):
        old_count = Timetable.objects.count()
        timetable = Timetable.objects.create(professor=self.professor, monday=self.monday, tuesday=self.tuesday)
        new_count = Timetable.objects.count()
        self.assertNotEqual(old_count, new_count)

    def test_api_can_get_a_timetable(self):
        timetable = Timetable.objects.get()
        response = self.client.get(
            reverse('timetable-detail',
            kwargs={'pk': timetable.id}), format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        formatted_times = [t.strftime('%H:%M:%S') for t in timetable.monday]      
        self.assertEqual(formatted_times, response.data['monday'])
        
    def test_api_can_update_timetable(self):
        timetable = Timetable.objects.get()
        change_timetable = {'monday': ['10:00', '14:00'], 'professor': self.professor.id}  # make sure to include all required fields
        res = self.client.put(
            reverse('timetable-detail', kwargs={'pk': timetable.id}),
            change_timetable, format='json'
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_api_can_delete_timetable(self):
        """Test the api can delete a timetable."""
        timetable = Timetable.objects.get()
        response = self.client.delete(
            reverse('timetable-detail', kwargs={'pk': timetable.id}),
            format='json',
            follow=True)

        self.assertEquals(response.status_code, status.HTTP_204_NO_CONTENT)