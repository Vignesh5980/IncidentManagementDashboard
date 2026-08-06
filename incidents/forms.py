from django import forms
from .models import Incident, Comment
from accounts.models import CustomUser


class IncidentCreateForm(forms.ModelForm):

    class Meta:
        model = Incident

        fields = [
            'title',
            'description',
            'application',
            'priority',
            'assigned_to'
        ]

        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter Incident Title'
            }),

            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5
            }),

            'application': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Application Name'
            }),

            'priority': forms.Select(attrs={
                'class': 'form-select'
            }),

            'assigned_to': forms.Select(attrs={
                'class': 'form-select'
            }),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)

        if 'assigned_to' in self.fields:
            self.fields['assigned_to'].queryset = CustomUser.objects.filter(
                role=CustomUser.SUPPORT
            )

        # Support Engineers cannot assign incidents
        if user and user.role == CustomUser.SUPPORT:
            self.fields.pop('assigned_to')


class IncidentUpdateForm(forms.ModelForm):

    class Meta:
        model = Incident

        fields = [
            'title',
            'description',
            'application',
            'priority',
            'status',
            'assigned_to',
            'root_cause',
            'resolution'
        ]

        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control'
            }),

            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5
            }),

            'application': forms.TextInput(attrs={
                'class': 'form-control'
            }),

            'priority': forms.Select(attrs={
                'class': 'form-select'
            }),

            'status': forms.Select(attrs={
                'class': 'form-select'
            }),

            'assigned_to': forms.Select(attrs={
                'class': 'form-select'
            }),

            'root_cause': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4
            }),

            'resolution': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4
            }),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)

        if 'assigned_to' in self.fields:
            self.fields['assigned_to'].queryset = CustomUser.objects.filter(
                role=CustomUser.SUPPORT
            )

        # Support Engineers cannot reassign incidents or change status
        if user and user.role == CustomUser.SUPPORT:

            if 'assigned_to' in self.fields:
                self.fields.pop('assigned_to')

            if 'status' in self.fields:
                self.fields.pop('status')

    def clean_title(self):

        title = self.cleaned_data['title']

        if len(title) < 5:
            raise forms.ValidationError(
                "Title should contain at least 5 characters."
            )

        return title

    def clean_description(self):

        description = self.cleaned_data['description']

        if len(description) < 20:
            raise forms.ValidationError(
                "Description should contain at least 20 characters."
            )

        return description

    def __init__(self, *args, user=None, **kwargs):

        super().__init__(*args, **kwargs)

        if user:

            if user.role == CustomUser.SUPPORT:

                self.fields.pop("assigned_to")

                self.fields.pop("status")

class CommentForm(forms.ModelForm):

    class Meta:

        model = Comment

        fields = ['comment']

        widgets = {

            'comment': forms.Textarea(attrs={
                'class':'form-control',
                'rows':3,
                'placeholder':'Add Comment'
            })

        }