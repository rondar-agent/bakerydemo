from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from wagtail.models import Page, Site

from bakerydemo.breads.models import BreadPage, BreadsIndexPage


class BreadPageEditLinkTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        root = Page.get_first_root_node()
        index = root.add_child(instance=BreadsIndexPage(title="Breads", slug="breads"))
        cls.bread = index.add_child(
            instance=BreadPage(title="Sourdough", slug="sourdough")
        )
        Site.objects.all().delete()
        Site.objects.create(
            hostname="testserver", root_page=index, is_default_site=True
        )

    def test_anonymous_visitor_cannot_see_edit_link(self):
        response = self.client.get(self.bread.url)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Edit this bread")

    def test_signed_in_non_admin_cannot_see_edit_link(self):
        user = get_user_model().objects.create_user(username="reader")
        self.client.force_login(user)
        response = self.client.get(self.bread.url)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Edit this bread")

    def test_signed_in_admin_sees_link_to_this_breads_editor(self):
        user = get_user_model().objects.create_user(username="admin", is_staff=True)
        self.client.force_login(user)
        response = self.client.get(self.bread.url)
        self.assertContains(
            response,
            f'<a href="{reverse("wagtailadmin_pages:edit", args=[self.bread.pk])}">'
            "Edit this bread</a>",
            html=True,
        )
