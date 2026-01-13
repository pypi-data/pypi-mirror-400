from django import forms
from django.utils.translation import gettext_lazy as _

from .models import RegisterParticipant


class ParticipantRegistrationForm(forms.ModelForm):
    confirm_password = forms.CharField(
        label=_("Confirm password"),
        widget=forms.PasswordInput(attrs={
            "placeholder": _("Password confirmation"),
            "autocomplete": "new-password"
        })
    )

    class Meta:
        model = RegisterParticipant
        fields = [
            "firstname",
            "lastname",
            "email",
            "password",
            "confirm_password",
            "organisation",
            "organisationAddress",
            "organisationRegistrationNumber",
            "optin_register",
        ]
        widgets = {
            "firstname": forms.TextInput(
                attrs={
                    "placeholder": _("Enter your first name"),
                }
            ),
            "lastname": forms.TextInput(
                attrs={
                    "placeholder": _("Enter your last name"),
                }
            ),
            "email": forms.EmailInput(
                attrs={
                    "placeholder": _("Enter your email"),
                }
            ),
            "password": forms.PasswordInput(
                attrs={
                    "placeholder": _("Enter the password you will use on LI Wallet"),
                }
            ),
            "confirm_password": forms.PasswordInput(
                attrs={
                    "placeholder": _("Password confirmation"),
                }
            ),
            "organisation": forms.TextInput(
                attrs={
                    "placeholder": _("Enter your organisation"),
                }
            ),
            "organisationAddress": forms.TextInput(
                attrs={
                    "placeholder": _("Enter your organisation address"),
                }
            ),
            "organisationRegistrationNumber": forms.TextInput(
                attrs={
                    "placeholder": _("Enter your organisation registration number"),
                }
            ),
            "optin_register": forms.CheckboxInput(
              attrs={
                "required":("true"),
              }
            ),
        }


    def clean_confirm_password(self):
        password = self.cleaned_data.get("password")
        confirm_password = self.cleaned_data.get("confirm_password")
        if not confirm_password:
            raise forms.ValidationError(_("This field is required."))
        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError(_("Passwords and confirmation do not match."))
        return confirm_password


    def save(self, commit=True):
        inst = super().save(commit=False)
        inst.password = self.cleaned_data["password"]
        if commit:
            inst.save()
        return inst
