from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Student, SmartDevice, StudyRoomReservation

class StudentRegistrationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = Student
        fields = ['username', 'first_name', 'last_name', 'email', 'student_id', 'phone_number', 'age', 'sex']

class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['first_name', 'last_name', 'email', 'phone_number', 'age', 'sex']

class SmartDeviceForm(forms.ModelForm):
    class Meta:
        model = SmartDevice
        fields = ['name', 'device_type', 'room', 'brand', 'connectivity', 'battery_level', 'description']

class RenameDeviceForm(forms.ModelForm):
    class Meta:
        model = SmartDevice
        fields = ['name']
        labels = {'name': 'New Name'}

class ManageDeviceForm(forms.ModelForm):
    class Meta:
        model = SmartDevice
        fields = [
            'is_on', 'power_consumption', 'brand',
            'connectivity', 'battery_level',
            'last_interaction', 'description'
        ]
        labels = {
            'is_on': "Turn device on",
            'power_consumption': 'Power consumption (Watts)',
        }
        widgets = {
            'last_interaction': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'description': forms.Textarea(attrs={'rows': 4}),
        }

class RoomReservationForm(forms.ModelForm):
    class Meta:
        model = StudyRoomReservation
        fields = ['study_room', 'reservation_date', 'start_time', 'end_time']
        widgets = {
            'reservation_date': forms.DateInput(attrs={'type': 'date'}),
            'start_time': forms.TimeInput(attrs={'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'type': 'time'}),
        }