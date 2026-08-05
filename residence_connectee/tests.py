from datetime import date, time
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from residence_connectee.models import (
    Apartment,
    News,
    Room,
    SmartDevice,
    StudyRoom,
    StudyRoomReservation,
)

Student = get_user_model()


class BaseTestCase(TestCase):
    """Base setup class providing shared fixtures across test modules."""

    def setUp(self):
        # Primary test user
        self.student = Student.objects.create_user(
            username='amine_test',
            password='testpassword123',
            email='amine@student.cytech.fr',
            level='Beginner',
            browsing_points=Decimal('0.00'),
            login_points=Decimal('0.00')
        )

        # Secondary user for access control & isolation tests
        self.other_student = Student.objects.create_user(
            username='hacker',
            password='hackerpassword',
            level='Beginner'
        )

        # Accommodation data for smart device testing
        self.apartment = Apartment.objects.create(
            address='Campus',
            apartment_number='12',
            occupant=self.student
        )
        self.room = Room.objects.create(
            name='Bedroom',
            apartment=self.apartment
        )
        self.device = SmartDevice.objects.create(
            name='Ma Lampe',
            device_type='Lamp',
            room=self.room,
            is_on=False
        )

        # Study room fixture
        self.study_room = StudyRoom.objects.create(
            name='Salle Turing',
            capacity=5
        )


class AuthenticationAndNavigationTests(BaseTestCase):
    """Tests related to user authentication flow and general page availability."""

    def test_login_and_logout(self):
        """Verify the complete user authentication lifecycle (login, access, logout)."""
        # Test Login POST
        response_login = self.client.post(reverse('login'), {
            'username': 'amine_test',
            'password': 'testpassword123'
        })
        self.assertRedirects(response_login, reverse('dashboard'))

        # Access Dashboard GET
        self.assertEqual(self.client.get(reverse('dashboard')).status_code, 200)

        # Test Logout GET
        response_logout = self.client.get(reverse('logout'))
        self.assertRedirects(response_logout, reverse('home'))

    def test_basic_views_rendering(self):
        """Verify standard pages load successfully for an authenticated user."""
        self.client.login(username='amine_test', password='testpassword123')

        self.assertEqual(self.client.get(reverse('student_list')).status_code, 200)
        self.assertEqual(self.client.get(reverse('my_reservations')).status_code, 200)
        self.assertEqual(self.client.get(reverse('edit_profile')).status_code, 200)


class GamificationTests(BaseTestCase):
    """Tests covering point allocation and level advancement features."""

    def test_home_gamification_points_added(self):
        """Ensure searching news on home page awards points when logged in."""
        self.client.login(username='amine_test', password='testpassword123')

        response = self.client.get(reverse('home'), {'q_news': 'test'})

        self.assertEqual(response.status_code, 200)
        self.student.refresh_from_db()
        self.assertEqual(self.student.browsing_points, Decimal('0.50'))

    def test_level_up_success(self):
        """Verify successful user level upgrade when sufficient points are accumulated."""
        self.client.login(username='amine_test', password='testpassword123')

        # Grant points required for 'Intermediate' level (>= 3 points)
        self.student.login_points = Decimal('3.50')
        self.student.save()

        response = self.client.post(reverse('level_up'))
        self.assertRedirects(response, reverse('dashboard'))

        self.student.refresh_from_db()
        self.assertEqual(self.student.level, 'Intermediate')


class StudyRoomReservationTests(BaseTestCase):
    """Tests covering study room bookings, conflicts, and cancellations."""

    def test_book_study_room_success(self):
        """Verify successful study room reservation and reward points allocation."""
        self.client.login(username='amine_test', password='testpassword123')

        data = {
            'study_room': self.study_room.id,
            'reservation_date': date.today().strftime('%Y-%m-%d'),
            'start_time': '10:00',
            'end_time': '12:00'
        }

        response = self.client.post(reverse('book_room'), data)

        self.assertRedirects(response, reverse('dashboard'))
        self.assertEqual(StudyRoomReservation.objects.count(), 1)

        self.student.refresh_from_db()
        self.assertEqual(self.student.browsing_points, Decimal('0.50'))

    def test_book_study_room_conflict(self):
        """Ensure the view prevents booking overlapping time slots for the same room."""
        StudyRoomReservation.objects.create(
            student=self.other_student,
            study_room=self.study_room,
            reservation_date=date.today(),
            start_time=time(10, 0),
            end_time=time(12, 0)
        )

        self.client.login(username='amine_test', password='testpassword123')

        data = {
            'study_room': self.study_room.id,
            'reservation_date': date.today().strftime('%Y-%m-%d'),
            'start_time': '11:00',
            'end_time': '13:00'
        }

        response = self.client.post(reverse('book_room'), data)

        self.assertEqual(StudyRoomReservation.objects.count(), 1)
        self.assertEqual(response.status_code, 200)

    def test_cancel_reservation(self):
        """Verify students can cancel their own existing reservations."""
        self.client.login(username='amine_test', password='testpassword123')

        reservation = StudyRoomReservation.objects.create(
            student=self.student,
            study_room=self.study_room,
            reservation_date=date.today(),
            start_time=time(8, 0),
            end_time=time(10, 0)
        )

        response = self.client.post(reverse('cancel_reservation', args=[reservation.id]))
        self.assertRedirects(response, reverse('my_reservations'))
        self.assertEqual(StudyRoomReservation.objects.count(), 0)


class SmartDeviceManagementTests(BaseTestCase):
    """Tests covering device administration, authorization tiers, and data isolation."""

    def test_add_device_level_restriction(self):
        """Verify 'Beginner' level users are restricted from adding devices."""
        self.client.login(username='amine_test', password='testpassword123')

        response = self.client.get(reverse('add_device'))
        self.assertRedirects(response, reverse('dashboard'))

    def test_configure_device_not_owner(self):
        """Verify data isolation: users cannot configure devices belonging to others."""
        self.client.login(username='hacker', password='hackerpassword')
        self.other_student.level = 'Advanced'
        self.other_student.save()

        response = self.client.get(reverse('configure_device', args=[self.device.id]))
        self.assertRedirects(response, reverse('dashboard'))

    def test_add_device_success(self):
        """Verify users with required level ('Intermediate') can add new devices."""
        self.student.level = 'Intermediate'
        self.student.save()
        self.client.login(username='amine_test', password='testpassword123')

        data = {
            'name': 'Mon Nouveau Thermostat',
            'device_type': 'Thermostat',
            'room': self.room.id
        }

        response = self.client.post(reverse('add_device'), data)
        self.assertRedirects(response, reverse('dashboard'))
        self.assertEqual(SmartDevice.objects.count(), 2)

    def test_delete_device_success(self):
        """Verify 'Advanced' tier users can delete their own devices."""
        self.student.level = 'Advanced'
        self.student.save()
        self.client.login(username='amine_test', password='testpassword123')

        response = self.client.post(reverse('delete_device', args=[self.device.id]))

        self.assertRedirects(response, reverse('dashboard'))
        self.assertEqual(SmartDevice.objects.count(), 0)

    def test_consumption_statistics_access(self):
        """Verify 'Expert' tier users can access consumption analytics."""
        self.student.level = 'Expert'
        self.student.save()
        self.client.login(username='amine_test', password='testpassword123')

        response = self.client.get(reverse('statistics'))
        self.assertEqual(response.status_code, 200)


class NewsAndSearchTests(BaseTestCase):
    """Tests for news feeds and device search functionality."""

    def test_news_detail_view(self):
        """Verify single news item page renders correctly."""
        news = News.objects.create(title="Titre", content="Contenu", category="RESIDENCE")
        response = self.client.get(reverse('news_detail', args=[news.id]))
        self.assertEqual(response.status_code, 200)

    def test_search_devices_filters(self):
        """Verify device search endpoint handles GET query filters properly."""
        response = self.client.get(reverse('search_devices'), {'q': 'Lampe', 'status': 'inactive'})
        self.assertEqual(response.status_code, 200)