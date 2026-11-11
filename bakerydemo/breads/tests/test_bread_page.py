from django.contrib.auth.models import User
from django.urls import reverse
from wagtail.models import Page, Site
from wagtail.test.utils import WagtailPageTestCase

from bakerydemo.breads.models import BreadPage


class BreadPageEditLinkTest(WagtailPageTestCase):
    @classmethod
    def setUpTestData(cls):
        root = Page.get_first_root_node()
        Site.objects.create(hostname="testserver", root_page=root, is_default_site=True)
        cls.bread = BreadPage(title="Sourdough", slug="test-sourdough")
        root.add_child(instance=cls.bread)
        cls.bread.save_revision().publish()
        cls.edit_url = reverse("wagtailadmin_pages:edit", args=[cls.bread.id])

    def test_link_hidden_from_anonymous_visitors(self):
        response = self.client.get(self.bread.url)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Edit this bread")
        self.assertNotContains(response, self.edit_url)

    def test_link_hidden_from_signed_in_non_superusers(self):
        user = User.objects.create_user(username="staff", password="password")
        user.is_staff = True
        user.save()
        self.client.force_login(user)
        response = self.client.get(self.bread.url)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Edit this bread")

    def test_link_shown_to_superusers(self):
        user = User.objects.create_superuser(
            username="admin", email="admin@example.com", password="password"
        )
        self.client.force_login(user)
        response = self.client.get(self.bread.url)
        self.assertContains(
            response, f'<a href="{self.edit_url}">Edit this bread</a>', html=True
        )
