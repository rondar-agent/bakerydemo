from django.core.cache import cache
from wagtail.models import Page, Site
from wagtail.test.utils import WagtailPageTestCase

from bakerydemo.blog.models import BlogIndexPage, BlogPage
from bakerydemo.recipes.models import RecipeIndexPage, RecipePage


class BlogListingReadMoreTest(WagtailPageTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.root = Page.get_first_root_node()
        cls.site = Site.objects.create(
            hostname="testserver",
            root_page=cls.root,
            is_default_site=True,
        )

        cls.blog_index = BlogIndexPage(title="Blog", slug="test-blog")
        cls.root.add_child(instance=cls.blog_index)
        cls.first_post = BlogPage(title="First post", slug="first-post")
        cls.second_post = BlogPage(title="Second post", slug="second-post")
        cls.blog_index.add_child(instance=cls.first_post)
        cls.blog_index.add_child(instance=cls.second_post)

        cls.recipe_index = RecipeIndexPage(title="Recipes", slug="test-recipes")
        cls.root.add_child(instance=cls.recipe_index)
        cls.recipe_index.add_child(instance=RecipePage(title="Rye", slug="rye"))

    def setUp(self):
        super().setUp()
        cache.clear()

    def test_each_post_teaser_has_read_more_inside_its_link(self):
        response = self.client.get(self.blog_index.url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "blog-listing-card__read-more", count=2)
        for post in (self.first_post, self.second_post):
            self.assertRegex(
                response.content.decode(),
                rf'(?s)<a class="blog-listing-card__link" href="{post.relative_url(self.site)}">'
                r"(?:(?!</a>).)*>Read more</span>",
            )

    def test_recipe_teasers_have_no_read_more(self):
        response = self.client.get(self.recipe_index.url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "blog-listing-card__title", count=1)
        self.assertNotContains(response, "Read more")
