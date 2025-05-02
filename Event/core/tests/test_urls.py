from django.test import SimpleTestCase
from django.urls import reverse, resolve
from core.views import home1, create_event, delete, details, ticket1, create_order, payment_success_page, payment_success, organizer_dashboard, my_ticket

class TestUrls(SimpleTestCase):
    def test_home1_urls_is_resolved(self):
        url = reverse('core:Home')
        self.assertEqual(resolve(url).func, home1)

    def test_create_urls_is_resolved(self):
        url = reverse('core:create_event')
        self.assertEqual(resolve(url).func, create_event)

    def test_delete_urls_is_resolved(self):
        url = reverse('core:delete_event', args=[1])
        self.assertEqual(resolve(url).func, delete)

    def test_details_urls_is_resolved(self):
        url = reverse('core:details', args=[1])
        self.assertEqual(resolve(url).func, details)

    def test_ticket_urls_is_resolved(self):
        url = reverse('core:ticket1', args=[1])
        self.assertEqual(resolve(url).func, ticket1)

    def test_order_urls_is_resolved(self):
        url = reverse('core:create_order', args=[1])
        self.assertEqual(resolve(url).func, create_order)

    def test_payment_urls_is_resolved(self):
        url = reverse('core:payment_success_page', args=[1])
        self.assertEqual(resolve(url).func, payment_success_page)

    def test_success_urls_is_resolved(self):
        url = reverse('core:payment_success')
        self.assertEqual(resolve(url).func, payment_success)

    def test_dashboard_urls_is_resolved(self):
        url = reverse('core:organizer_dashboard')
        self.assertEqual(resolve(url).func, organizer_dashboard)

    def test_my_ticket_urls_is_resolved(self):
        url = reverse('core:my_ticket')
        self.assertEqual(resolve(url).func, my_ticket)

