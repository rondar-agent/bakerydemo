from wagtail.models import Page, Site
from wagtail.test.utils import WagtailPageTestCase

from bakerydemo.blog.models import BlogIndexPage, BlogPage
from bakerydemo.recipes.models import RecipeIndexPage, RecipePage


class ReadMoreLinkTest(WagtailPageTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.root = Page.get_first_root_node()
        Site.objects.create(
            hostname="testserver",
            root_page=cls.root,
            is_default_site=True,
        )

    def test_blog_index_shows_read_more_inside_each_post_link(self):
        blog_index = self.root.add_child(
            instance=BlogIndexPage(title="Blog", slug="test-blog")
        )
        posts = [
            blog_index.add_child(instance=BlogPage(title=title, slug=title))
            for title in ("first-post", "second-post")
        ]

        response = self.client.get(blog_index.url)

        self.assertContains(response, ">Read more</p>", count=len(posts))
        content = response.content.decode()
        for post in posts:
            start = content.index(f'href="/test-blog/{post.slug}/"')
            self.assertIn("Read more", content[start : content.index("</a>", start)])

    def test_recipe_index_does_not_show_read_more(self):
        recipe_index = self.root.add_child(
            instance=RecipeIndexPage(title="Recipes", slug="test-recipes")
        )
        recipe_index.add_child(instance=RecipePage(title="Bread", slug="bread"))

        response = self.client.get(recipe_index.url)

        self.assertContains(response, "blog-listing-card__title")
        self.assertNotContains(response, "Read more")
