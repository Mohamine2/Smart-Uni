from django.contrib import admin
from django.urls import path
from residence_connectee import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home_view, name='home'),
    path('index/', views.home_view, name='home'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('directory/', views.student_list, name='student_list'),
    path('reservations/', views.book_study_room, name='book_room'),
    path('my-reservations/', views.my_reservations, name='my_reservations'),
    path('cancel-reservation/<int:reservation_id>/', views.cancel_reservation, name='cancel_reservation'),

    # --- NEWS MODULE ---
    path('news/<int:pk>/', views.news_detail, name='news_detail'),

    # --- CONNECTED DEVICES MODULE ---
    path('devices/search/', views.search_devices, name='search_devices'),
    path('profile/level-up/', views.level_up, name='level_up'),

    # Level 3 (Intermediate)
    path('devices/add/', views.add_device, name='add_device'),
    path('devices/rename/<int:device_id>/', views.rename_device, name='rename_device'),

    # Level 5 (Advanced)
    path('devices/delete/<int:device_id>/', views.delete_device, name='delete_device'),
    path('devices/configure/<int:device_id>/', views.configure_device, name='configure_device'),

    # Level 7 (Expert)
    path('statistics/', views.consumption_statistics, name='statistics'),
]