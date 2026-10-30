from datetime import time

from wagtail.models import Page, Site
from wagtail.test.utils import WagtailPageTestCase

from bakerydemo.locations.models import (
    LocationOperatingDay,
    LocationOperatingTimeSlot,
    LocationPage,
    LocationsIndexPage,
)


class LocationPageRenderTest(WagtailPageTestCase):
    @classmethod
    def setUpTestData(cls):
        root = Page.get_first_root_node()
        Site.objects.create(
            hostname="testserver",
            root_page=root,
            is_default_site=True,
        )
        cls.index = LocationsIndexPage(title="Locations", slug="test-locations")
        root.add_child(instance=cls.index)
        cls.location = LocationPage(
            title="Selfoss",
            slug="selfoss",
            introduction="A bakery by the river.",
            address="Eyravegur",
            lat_long="63.9331, -20.9971",
        )
        cls.index.add_child(instance=cls.location)

    def test_opening_hours_are_shown_before_the_rest_of_the_page(self):
        monday = LocationOperatingDay.objects.create(location=self.location, day="MON")
        LocationOperatingTimeSlot.objects.create(
            day=monday, opening_time=time(8), closing_time=time(12)
        )
        LocationOperatingTimeSlot.objects.create(
            day=monday, opening_time=time(13), closing_time=time(18)
        )
        LocationOperatingDay.objects.create(
            location=self.location, day="TUE", closed=True
        )

        response = self.client.get(self.location.url)

        self.assertContains(response, "8 a.m. - noon,")
        self.assertContains(response, "1 p.m. - 6 p.m.")
        self.assertContains(response, "Closed")
        content = response.content.decode()
        hours = content.index(">Opening hours<")
        self.assertLess(hours, content.index(">Operating Status<"))
        self.assertLess(hours, content.index(">Address<"))

    def test_opening_hours_heading_is_hidden_without_operating_days(self):
        response = self.client.get(self.location.url)

        self.assertNotContains(response, ">Opening hours<")
        self.assertContains(response, ">Operating Status<")
