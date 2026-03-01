from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User


class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    
    class Meta:
        model = User
        fields = [
            'username', 'email', 'first_name', 'last_name', 
            'phone_number', 'date_of_birth', 'address', 
            'gender', 'emergency_contact_name', 'emergency_contact_phone', 
            'alzheimers_duration_years'
        ]
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
        }

    def clean(self):
        cleaned = super().clean()
        # Ensure alzheimers duration, if provided, is non-negative
        dur = cleaned.get('alzheimers_duration_years')
        if dur is not None and dur < 0:
            self.add_error('alzheimers_duration_years', 'Duration must be a non-negative number')
        return cleaned
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        # Suppress password help texts
        self.fields['password1'].help_text = ""
        self.fields['password2'].help_text = ""
    
    def clean_username(self):
        """Override to allow any username without validation"""
        return self.cleaned_data.get('username')
    
    def save(self, commit=True):
        user = super().save(commit=False)
        # Explicitly assign common fields to ensure they're saved
        user.email = self.cleaned_data.get('email', '')
        user.first_name = self.cleaned_data.get('first_name', '')
        user.last_name = self.cleaned_data.get('last_name', '')
        # Ensure role matches model choices
        user.role = 'PATIENT'
        if commit:
            user.save()
        return user


class UserLoginForm(AuthenticationForm):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)


class PatientProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'phone_number', 'date_of_birth', 'address', 'emergency_contact_name', 'emergency_contact_phone']
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'})
        }


class CaregiverRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = [
            'username', 'email', 'first_name', 'last_name',
            'phone_number', 'specialization', 'license_number',
            'caregiving_experience_years'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'password1' in self.fields:
            self.fields['password1'].help_text = ""
        if 'password2' in self.fields:
            self.fields['password2'].help_text = ""

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'CAREGIVER'
        if commit:
            user.save()
        return user


class DoctorRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = [
            'username', 'email', 'first_name', 'last_name',
            'phone_number', 'specialization', 'license_number'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'password1' in self.fields:
            self.fields['password1'].help_text = ""
        if 'password2' in self.fields:
            self.fields['password2'].help_text = ""

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'DOCTOR'
        if commit:
            user.save()
        return user


class PatientRegistrationForm(UserRegistrationForm):
    """Alias for backwards compatibility with refinements for patient context"""
    pass
