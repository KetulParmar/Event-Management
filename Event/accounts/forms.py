from captcha.fields import CaptchaField
from django.forms import Form

class Cap(Form):
	cap = CaptchaField()


