from django.test import SimpleTestCase
from django.urls import reverse, resolve
from accounts.views import home, login_view, register, organizer, attendee, logout_view, forget

class TestUrls(SimpleTestCase):
    def test_home_urls_is_resolved(self):
        url = reverse('accounts:home')
        self.assertEqual(resolve(url).func, home)

    def test_login_urls_is_resolved(self):
        url = reverse('accounts:Login')
        self.assertEqual(resolve(url).func, login_view)

    def test_reg_urls_is_resolved(self):
        url = reverse('accounts:Register')
        self.assertEqual(resolve(url).func, register)

    def test_org_urls_is_resolved(self):
        url = reverse('accounts:Organizer')
        self.assertEqual(resolve(url).func, organizer)

    def test_att_urls_is_resolved(self):
        url = reverse('accounts:Attendee')
        self.assertEqual(resolve(url).func, attendee)

    def test_logout_urls_is_resolved(self):
        url = reverse('accounts:logout')
        self.assertEqual(resolve(url).func, logout_view)

    def test_forget_urls_is_resolved(self):
        url = reverse('accounts:Forget')
        self.assertEqual(resolve(url).func, forget)

