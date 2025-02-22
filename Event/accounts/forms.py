from django import forms
from captcha.fields import CaptchaField

class ContactForm(forms.Form):
    email = forms.EmailField(label="Email", required=True)
    mobile = forms.CharField(label="Mobile Number", max_length=10, required=True)
    captcha = CaptchaField()