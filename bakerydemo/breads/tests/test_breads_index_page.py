from wagtail.models import Page, Site
from wagtail.test.utils import WagtailPageTestCase

from bakerydemo.breads.models import BreadsIndexPage
from bakerydemo.people.models import PeopleIndexPage

TAGLINE = "Every loaf is baked fresh each morning."


class BreadsIndexPageTaglineTest(WagtailPageTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.root = Page.get_first_root_node()
        Site.objects.create(
            hostname="testserver", root_page=cls.root, is_default_site=True
        )

        cls.breads = BreadsIndexPage(title="Breads", slug="test-breads")
        cls.root.add_child(instance=cls.breads)
        cls.people = PeopleIndexPage(title="People", slug="test-people")
        cls.root.add_child(instance=cls.people)

    def test_tagline_renders_on_breads_page(self):
        response = self.client.get(self.breads.url)

        self.assertContains(
            response,
            f'<p class="index-header__tagline">{TAGLINE}</p>',
            html=True,
        )

    def test_tagline_not_on_other_index_pages(self):
        response = self.client.get(self.people.url)

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, TAGLINE)
