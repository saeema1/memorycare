from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User


class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2', 'phone_number', 'date_of_birth', 'address', 'emergency_contact_name', 'emergency_contact_phone', 'alzheimers_duration_years']

    def clean(self):
        cleaned = super().clean()
        # Ensure alzheimers duration, if provided, is non-negative
        dur = cleaned.get('alzheimers_duration_years')
        if dur is not None and dur < 0:
            self.add_error('alzheimers_duration_years', 'Duration must be a non-negative number')
        return cleaned
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)  # Remove user from kwargs before calling super
        super().__init__(*args, **kwargs)
    
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


    # Backwards-compatibility alias: some modules expect `PatientRegistrationForm`
    PatientRegistrationForm = UserRegistrationForm
