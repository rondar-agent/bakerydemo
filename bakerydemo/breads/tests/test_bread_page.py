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
        cls.bread = BreadPage(title="Sourdough", slug="sourdough")
        root.add_child(instance=cls.bread)
        cls.bread.save_revision().publish()
        cls.edit_url = reverse("wagtailadmin_pages:edit", args=[cls.bread.id])

    def assert_no_edit_link(self, response):
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Edit this bread")
        self.assertNotContains(response, self.edit_url)

    def test_superuser_sees_edit_link(self):
        User.objects.create_superuser("admin", "admin@example.com", "password")
        self.client.login(username="admin", password="password")
        response = self.client.get(self.bread.url)
        self.assertContains(response, "Edit this bread")
        self.assertContains(response, f'href="{self.edit_url}"')

    def test_anonymous_user_does_not_see_edit_link(self):
        self.assert_no_edit_link(self.client.get(self.bread.url))

    def test_signed_in_non_superuser_does_not_see_edit_link(self):
        User.objects.create_user(
            "staff", "staff@example.com", "password", is_staff=True
        )
        self.client.login(username="staff", password="password")
        self.assert_no_edit_link(self.client.get(self.bread.url))
