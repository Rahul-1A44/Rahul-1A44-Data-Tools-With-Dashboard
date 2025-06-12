from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate

class CustomAuthenticationForm(AuthenticationForm):
    def confirm_login_allowed(self, user):
        if not user.is_active:
            raise forms.ValidationError(
                "This account is inactive. Please activate it via the email sent to you.",
                code='inactive',
            )

class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'password1': forms.PasswordInput(attrs={'class': 'form-control'}),
            'password2': forms.PasswordInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'username': 'Username',
            'email': 'Email',
            'password1': 'Password',
            'password2': 'Confirm Password',
        }
