from datetime import time

from wagtail.models import Page, Site
from wagtail.test.utils import WagtailPageTestCase

from bakerydemo.locations.models import (
    LocationOperatingDay,
    LocationOperatingTimeSlot,
    LocationPage,
    LocationsIndexPage,
)


class LocationPageOpeningHoursTest(WagtailPageTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.root = Page.get_first_root_node()
        Site.objects.create(
            hostname="testserver", root_page=cls.root, is_default_site=True
        )

        cls.index = LocationsIndexPage(title="Locations", slug="test-locations")
        cls.root.add_child(instance=cls.index)

        cls.location = LocationPage(
            title="Reykjavik",
            slug="reykjavik",
            introduction="A cosy bakery by the harbour.",
            address="Laugavegur 36",
            lat_long="64.144367, -21.939182",
        )
        cls.index.add_child(instance=cls.location)

    def add_operating_day(self):
        day = LocationOperatingDay.objects.create(location=self.location, day="MON")
        LocationOperatingTimeSlot.objects.create(
            day=day, opening_time=time(9), closing_time=time(18)
        )

    def test_opening_hours_come_before_the_rest_of_the_page(self):
        self.add_operating_day()

        html = self.client.get(self.location.url).content.decode()

        hours = html.index("Opening hours")
        self.assertIn("9 a.m. - 6 p.m.", html)
        self.assertLess(hours, html.index("Operating Status"))
        self.assertLess(hours, html.index("Laugavegur 36"))
        self.assertLess(hours, html.index("A cosy bakery by the harbour."))

    def test_opening_hours_heading_hidden_without_operating_days(self):
        response = self.client.get(self.location.url)

        self.assertNotContains(response, "Opening hours")
        self.assertContains(response, "Operating Status")
