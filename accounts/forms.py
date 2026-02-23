from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User


class PatientRegistrationForm(UserCreationForm):
    username = forms.CharField(required=True, help_text="Required. Any characters allowed.")
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    email = forms.EmailField(required=True)
    phone_number = forms.CharField(required=True)
    date_of_birth = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=True)
    gender = forms.ChoiceField(choices=User.GENDER_CHOICES, required=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 
                  'phone_number', 'date_of_birth', 'gender', 'address', 
                  'emergency_contact_name', 'emergency_contact_phone', 'alzheimers_duration_years']

    def clean(self):
        cleaned = super().clean()
        dur = cleaned.get('alzheimers_duration_years')
        if dur is not None and dur < 0:
            self.add_error('alzheimers_duration_years', 'Duration must be a non-negative number')
        return cleaned
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.phone_number = self.cleaned_data['phone_number']
        user.date_of_birth = self.cleaned_data['date_of_birth']
        user.gender = self.cleaned_data['gender']
        user.address = self.cleaned_data.get('address')
        user.emergency_contact_name = self.cleaned_data.get('emergency_contact_name')
        user.emergency_contact_phone = self.cleaned_data.get('emergency_contact_phone')
        user.alzheimers_duration_years = self.cleaned_data.get('alzheimers_duration_years')
        user.role = 'PATIENT'
        if commit:
            user.save()
        return user


class CaregiverRegistrationForm(UserCreationForm):
    username = forms.CharField(required=True, help_text="Required. Any characters allowed.")
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    email = forms.EmailField(required=True)
    phone_number = forms.CharField(required=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 
                  'phone_number', 'address', 'caregiving_experience_years', 'relationship_to_patient']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.phone_number = self.cleaned_data['phone_number']
        user.address = self.cleaned_data.get('address')
        user.caregiving_experience_years = self.cleaned_data.get('caregiving_experience_years')
        user.relationship_to_patient = self.cleaned_data.get('relationship_to_patient')
        user.role = 'CAREGIVER'
        if commit:
            user.save()
        return user



# DoctorRegistrationForm removed



class UserLoginForm(AuthenticationForm):
    pass


class PatientProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'phone_number', 'date_of_birth', 'address', 'emergency_contact_name', 'emergency_contact_phone']
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'})
        }
