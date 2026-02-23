from django import forms
from .models import MoodEntry, DailyActivity


class MoodForm(forms.ModelForm):
    class Meta:
        model = MoodEntry
        fields = ['mood', 'note']
        widgets = {
            'note': forms.Textarea(attrs={'rows': 3}),
        }


class DailyActivityForm(forms.ModelForm):
    scheduled_for = forms.DateTimeField(widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}))

    class Meta:
        model = DailyActivity
        fields = ['user', 'name', 'activity_type', 'scheduled_for', 'recurrence', 'recurrence_interval', 'recurrence_end']

    def clean(self):
        cleaned = super().clean()
        rec = cleaned.get('recurrence')
        rec_end = cleaned.get('recurrence_end')
        from django.utils import timezone
        if rec and rec != 'none' and rec_end and rec_end < timezone.now().date():
            self.add_error('recurrence_end', 'Recurrence end must be today or later')
        return cleaned