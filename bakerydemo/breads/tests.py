from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from wagtail.models import Page, Site

from bakerydemo.breads.models import BreadPage, BreadsIndexPage


class BreadPageEditLinkTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        root = Page.get_first_root_node()
        home = root.add_child(instance=Page(title="Home", slug="test-home"))
        Site.objects.update_or_create(
            is_default_site=True,
            defaults={"hostname": "localhost", "root_page": home},
        )
        index = home.add_child(instance=BreadsIndexPage(title="Breads", slug="breads"))
        cls.bread = index.add_child(
            instance=BreadPage(title="Sourdough", slug="sourdough")
        )
        cls.edit_url = reverse("wagtailadmin_pages:edit", args=[cls.bread.id])

        User = get_user_model()
        cls.superuser = User.objects.create_superuser(
            username="admin", email="admin@example.com", password="password"
        )
        cls.staff_user = User.objects.create_user(
            username="editor",
            email="editor@example.com",
            password="password",
            is_staff=True,
        )

    def get_bread_page(self):
        response = self.client.get(self.bread.url)
        self.assertEqual(response.status_code, 200)
        return response

    def test_anonymous_user_does_not_see_edit_link(self):
        response = self.get_bread_page()
        self.assertNotContains(response, "Edit this bread")
        self.assertNotContains(response, self.edit_url)

    def test_non_superuser_does_not_see_edit_link(self):
        self.client.force_login(self.staff_user)
        response = self.get_bread_page()
        self.assertNotContains(response, "Edit this bread")

    def test_superuser_sees_edit_link(self):
        self.client.force_login(self.superuser)
        response = self.get_bread_page()
        self.assertContains(response, "Edit this bread")
        self.assertContains(response, f'href="{self.edit_url}"')
