from django.contrib.auth.models import Group, Permission, User
from django.urls import reverse
from wagtail.models import GroupPagePermission, Page, Site
from wagtail.test.utils import WagtailPageTestCase

from bakerydemo.breads.models import BreadPage, BreadsIndexPage


class BreadPageEditLinkTest(WagtailPageTestCase):
    @classmethod
    def setUpTestData(cls):
        root = Page.get_first_root_node()
        Site.objects.create(hostname="testserver", root_page=root, is_default_site=True)
        cls.index = BreadsIndexPage(title="Breads", slug="test-breads")
        root.add_child(instance=cls.index)
        cls.bread = BreadPage(title="Sourdough", slug="sourdough")
        cls.index.add_child(instance=cls.bread)
        cls.edit_url = reverse("wagtailadmin_pages:edit", args=[cls.bread.id])

    def assertEditLink(self, shown):
        response = self.client.get(self.bread.url)
        self.assertEqual(response.status_code, 200)
        if shown:
            self.assertContains(response, "Edit this bread")
            self.assertContains(response, f'href="{self.edit_url}"')
        else:
            self.assertNotContains(response, "Edit this bread")
            self.assertNotContains(response, self.edit_url)

    def test_hidden_for_anonymous_visitor(self):
        self.assertEditLink(shown=False)

    def test_hidden_for_signed_in_non_admin(self):
        user = User.objects.create_user(username="visitor", password="password")
        self.client.force_login(user)
        self.assertEditLink(shown=False)

    def test_hidden_for_admin_without_edit_permission(self):
        user = User.objects.create_user(username="viewer", password="password")
        user.user_permissions.add(
            Permission.objects.get(
                content_type__app_label="wagtailadmin", codename="access_admin"
            )
        )
        self.client.force_login(user)
        self.assertEditLink(shown=False)

    def test_shown_for_editor_with_edit_permission(self):
        group = Group.objects.create(name="Bread editors")
        group.permissions.add(
            Permission.objects.get(
                content_type__app_label="wagtailadmin", codename="access_admin"
            )
        )
        GroupPagePermission.objects.create(
            group=group,
            page=self.index,
            permission=Permission.objects.get(codename="change_page"),
        )
        user = User.objects.create_user(username="editor", password="password")
        user.groups.add(group)
        self.client.force_login(user)
        self.assertEditLink(shown=True)

    def test_shown_for_superuser(self):
        user = User.objects.create_superuser(
            username="admin", email="admin@example.com", password="password"
        )
        self.client.force_login(user)
        self.assertEditLink(shown=True)
