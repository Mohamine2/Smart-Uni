from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from functools import wraps
from django.db.models import Sum, Q
from decimal import Decimal
from .models import Student, News, ConnectedDevice, Room, StudyRoom, RoomReservation, Apartment

# --- 1. HOME & NEWS MODULE ---

def home_view(request):
    category = request.GET.get('category', '')
    q_news = request.GET.get('q_news', '')
    cat_filter = request.GET.get('category', '')
    order = request.GET.get('order', '-publication_date')

    news_list = News.objects.all()

    if q_news:
        news_list = news_list.filter(Q(title__icontains=q_news) | Q(content__icontains=q_news))

    if cat_filter:
        news_list = news_list.filter(category=cat_filter)

    if order in ['publication_date', '-publication_date']:
        news_list = news_list.order_by(order)
    else:
        news_list = news_list.order_by('-publication_date')

    # --- GAMIFICATION ---
    if request.user.is_authenticated and (q_news or cat_filter):
        request.user.browsing_points += Decimal('0.50')
        request.user.save()

    context = {
        'news_list': news_list,
        'categories': News.CATEGORY_CHOICES,
        'selected_cat': category,
        'selected_order': order,
        'rooms': Room.objects.all(),
        'type_choices': ConnectedDevice.TYPE_CHOICES,
    }

    return render(request, 'index.html', context)

def news_detail(request, pk):
    news_item = get_object_or_404(News, pk=pk)
    return render(request, 'news_detail.html', {'news_item': news_item})


# --- 2. AUTHENTICATION MODULE ---

def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        user_password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')
        user_first_name = request.POST.get('first_name')
        user_last_name = request.POST.get('last_name')
        user_phone = request.POST.get('phone')
        user_email = request.POST.get('email')
        user_student_id = request.POST.get('student_id')
        user_age = request.POST.get('age')
        user_sex = request.POST.get('sex')

        if user_password != password_confirm:
            messages.error(request, "Passwords do not match. Please try again.")
            return render(request, 'register.html')

        user, created = Student.objects.get_or_create(
            username=username,
            defaults={
                'first_name': user_first_name,
                'last_name': user_last_name,
                'email': user_email,
                'phone_number': user_phone,
                'student_id': user_student_id,
                'age': user_age,
                'sex': user_sex,
                'is_active': True,
            }
        )

        if created:
            user.set_password(user_password)
            user.save()
            messages.success(request, "Registration successful! Please log in.")
            return redirect('login')
        else:
            messages.error(request, "This username is already taken. Please choose another one.")

    return render(request, 'register.html')

def login_view(request):
    if request.method == 'POST':
        user_name = request.POST.get('username')
        user_password = request.POST.get('password')

        user = authenticate(request, username=user_name, password=user_password)

        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, "Invalid credentials.")

    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    return redirect('home')

@login_required
def dashboard_view(request):
    return render(request, 'dashboard.html', {'student': request.user})

@login_required
def edit_profile(request):
    user = request.user
    if request.method == 'POST':
        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        user.email = request.POST.get('email')
        user.phone_number = request.POST.get('phone')
        user.age = request.POST.get('age')
        user.sex = request.POST.get('sex')

        user.save()
        messages.success(request, "Your profile has been updated successfully!")
        return redirect('dashboard')

    return render(request, 'edit_profile.html', {'user': user})

@login_required
def student_list(request):
    students = Student.objects.filter(is_superuser=False, is_active=True).order_by('last_name', 'first_name')
    return render(request, 'student_list.html', {'students': students})

@login_required
def my_reservations(request):
    reservations = RoomReservation.objects.filter(student=request.user).order_by('-reservation_date', '-start_time')
    return render(request, 'my_reservations.html', {'reservations': reservations})

@login_required
def cancel_reservation(request, reservation_id):
    reservation = get_object_or_404(RoomReservation, id=reservation_id, student=request.user)

    if request.method == 'POST':
        reservation.delete()
        messages.success(request, "Reservation successfully canceled.")
        return redirect('my_reservations')

    return redirect('my_reservations')


# Level Requirement Decorator
def level_required(min_points):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if request.user.total_points >= min_points:
                return view_func(request, *args, **kwargs)
            else:
                messages.error(request, f"Insufficient level. You need {min_points} points to access this feature.")
                return redirect('dashboard')
        return _wrapped_view
    return decorator


@login_required
def book_room(request):
    study_rooms = StudyRoom.objects.all()

    if request.method == 'POST':
        room_id = request.POST.get('room')
        res_date = request.POST.get('date')
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')

        room = get_object_or_404(StudyRoom, id=room_id)

        conflict = RoomReservation.objects.filter(
            room=room,
            reservation_date=res_date
        ).filter(
            Q(start_time__lt=end_time, end_time__gt=start_time)
        ).exists()

        if conflict:
            messages.error(request, f"Sorry, the {room.name} is already booked during this time slot.")
            return render(request, 'book_room.html', {'rooms': study_rooms})

        RoomReservation.objects.create(
            room=room,
            student=request.user,
            reservation_date=res_date,
            start_time=start_time,
            end_time=end_time
        )

        request.user.browsing_points += Decimal('0.50')
        request.user.save()
        messages.success(request, "Reservation confirmed!")
        return redirect('dashboard')

    return render(request, 'book_room.html', {'rooms': study_rooms})


# --- 3. CONNECTED DEVICES MODULE ---

def search_devices(request):
    keyword = request.GET.get('q', '')
    selected_type = request.GET.get('device_type', '')
    selected_status = request.GET.get('status', '')
    selected_room = request.GET.get('room', '')

    devices = ConnectedDevice.objects.all()

    if keyword:
        devices = devices.filter(name__icontains=keyword)
    if selected_type:
        devices = devices.filter(device_type=selected_type)
    if selected_status == 'active':
        devices = devices.filter(is_on=True)
    elif selected_status == 'inactive':
        devices = devices.filter(is_on=False)
    if selected_room:
        devices = devices.filter(room_id=selected_room)

    rooms = Room.objects.all()

    context = {
        'devices': devices,
        'rooms': rooms,
        'keyword': keyword,
        'selected_type': selected_type,
        'selected_status': selected_status,
        'selected_room': selected_room,
        'type_choices': ConnectedDevice.TYPE_CHOICES,
    }

    return render(request, 'search_devices.html', context)

def min_level_required(min_level_value):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if request.user.level_value >= min_level_value:
                return view_func(request, *args, **kwargs)
            else:
                messages.error(request, "Insufficient level. Claim your next level on your dashboard!")
                return redirect('dashboard')
        return _wrapped_view
    return decorator


def get_device_if_owner(request, device_id):
    device = get_object_or_404(ConnectedDevice, id=device_id)
    if device.room.apartment.occupant != request.user:
        return None
    return device


@login_required
def level_up(request):
    if request.method == 'POST':
        user = request.user
        points = user.total_points

        if user.level == 'Beginner' and points >= 3:
            user.level = 'Intermediate'
            messages.success(request, "Congratulations! You have unlocked the Intermediate level and device addition!")
        elif user.level == 'Intermediate' and points >= 5:
            user.level = 'Advanced'
            messages.success(request, "Congratulations! Advanced level reached. You can now configure and delete devices.")
        elif user.level == 'Advanced' and points >= 7:
            user.level = 'Expert'
            messages.success(request, "Congratulations! You are now an Expert. Statistics are unlocked.")
        else:
            messages.error(request, "You don't have enough points to claim this level yet.")

        user.save()
    return redirect('dashboard')


@login_required
@min_level_required(1)
def add_device(request):
    my_apartments = Apartment.objects.filter(occupant=request.user)
    my_rooms = Room.objects.filter(apartment__in=my_apartments)

    if request.method == 'POST':
        name = request.POST.get('device_name')
        dev_type = request.POST.get('device_type')
        room_id = request.POST.get('room')

        brand = request.POST.get('brand')
        connectivity = request.POST.get('connectivity')
        description = request.POST.get('description')

        battery_level = request.POST.get('battery_level')
        last_interaction = request.POST.get('last_interaction')

        room = get_object_or_404(my_rooms, id=room_id)

        if battery_level and battery_level.strip():
            battery_value = int(battery_level)
        else:
            battery_value = None

        ConnectedDevice.objects.create(
            name=name,
            device_type=dev_type,
            room=room,
            is_on=False,
            power_consumption=0.0,
            brand=brand if brand else None,
            connectivity=connectivity if connectivity else None,
            description=description if description else None,
            battery_level=battery_value,
            last_interaction=last_interaction if last_interaction else None,
        )

        request.user.browsing_points += Decimal('0.50')
        request.user.save()
        messages.success(request, "The device has been added to your apartment.")
        return redirect('dashboard')

    context = {
        'rooms': my_rooms,
        'type_choices': ConnectedDevice.TYPE_CHOICES
    }
    return render(request, 'add_device.html', context)


@login_required
@min_level_required(1)
def rename_device(request, device_id):
    device = get_device_if_owner(request, device_id)
    if not device:
        messages.error(request, "Access denied.")
        return redirect('dashboard')

    if request.method == 'POST':
        new_name = request.POST.get('new_name')
        if new_name:
            device.name = new_name
            device.save()
            messages.success(request, "The device has been successfully renamed.")
            return redirect('dashboard')

    return render(request, 'rename_device.html', {'device': device})


@login_required
@min_level_required(2)
def delete_device(request, device_id):
    device = get_device_if_owner(request, device_id)
    if not device:
        messages.error(request, "Access denied.")
        return redirect('dashboard')

    device.delete()
    request.user.browsing_points += Decimal('0.50')
    request.user.save()
    messages.success(request, "The device has been deleted.")
    return redirect('dashboard')


@login_required
@min_level_required(2)
def configure_device(request, device_id):
    device = get_device_if_owner(request, device_id)
    if not device:
        messages.error(request, "Access denied.")
        return redirect('dashboard')

    if request.method == 'POST':
        # Correction : 'on' est la valeur par défaut envoyée par une checkbox HTML
        device.is_on = request.POST.get('status') == 'on'

        if device.is_on:
            power_val = request.POST.get('power')
            device.power_consumption = float(power_val) if power_val else 0.0
        else:
            device.power_consumption = 0.0

        device.description = request.POST.get('description')
        device.brand = request.POST.get('brand')
        device.connectivity = request.POST.get('connectivity')

        battery_level = request.POST.get('battery_level')
        device.battery_level = int(battery_level) if battery_level and battery_level.isdigit() else None

        last_interaction = request.POST.get('last_interaction')
        device.last_interaction = last_interaction if last_interaction else None

        device.save()
        request.user.browsing_points += Decimal('0.50')
        request.user.save()
        messages.success(request, f"The settings for {device.name} have been updated.")
        return redirect('dashboard')

    return render(request, 'configure_device.html', {'device': device})

@login_required
@min_level_required(3)
def consumption_statistics(request):
    my_apartments = request.user.apartments.all()
    my_devices = ConnectedDevice.objects.filter(room__apartment__in=my_apartments)

    aggregation = my_devices.aggregate(total=Sum('power_consumption'))

    if aggregation['total'] is None:
        total_consumption = 0.0
    else:
        total_consumption = float(aggregation['total'])

    active_devices = my_devices.filter(is_on=True)
    inactive_devices = my_devices.filter(is_on=False)

    context = {
        'total_consumption': total_consumption,
        'active_count': active_devices.count(),
        'inactive_count': inactive_devices.count(),
        'active_devices': active_devices,
    }
    return render(request, 'statistics.html', context)