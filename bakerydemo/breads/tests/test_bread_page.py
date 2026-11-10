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

        cls.bread = BreadPage(
            title="Test Sourdough",
            slug="test-sourdough",
            introduction="A tangy loaf.",
        )
        root.add_child(instance=cls.bread)
        cls.bread.save_revision().publish()

        cls.edit_url = reverse("wagtailadmin_pages:edit", args=[cls.bread.id])

    def test_anonymous_user_does_not_see_edit_link(self):
        response = self.client.get(self.bread.url)

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Edit this bread")
        self.assertNotContains(response, self.edit_url)

    def test_non_superuser_does_not_see_edit_link(self):
        User.objects.create_user(username="editor", password="password", is_staff=True)
        self.client.login(username="editor", password="password")

        response = self.client.get(self.bread.url)

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Edit this bread")

    def test_superuser_sees_edit_link(self):
        User.objects.create_superuser(
            username="admin", email="admin@example.com", password="password"
        )
        self.client.login(username="admin", password="password")

        response = self.client.get(self.bread.url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response, f'<a href="{self.edit_url}">Edit this bread</a>', html=True
        )
