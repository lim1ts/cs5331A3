from scrapy.contrib.spiders.init import InitSpider
from scrapy.http import Request, FormRequest
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.contrib.spiders import Rule

class MySpider(InitSpider):
    name = 'app1scanner'
    allowed_domains = ['app1.com']
    login_page = 'https://app1.com/admin/index.php?page=login'
    start_urls = ['https://app1.com/admin', 'https://app1.com/admin/index.php']

    rules = (
        Rule(SgmlLinkExtractor(allow=r'-\w+.html$'),
             callback='parse_item', follow=True),
    )

    def init_request(self):
        """This function is called before crawling starts."""
        return Request(url=self.login_page, callback=self.login)

    def login(self, response):
        """Generate a login request."""
        return FormRequest(self.login_page,
                    formdata={'adminname': 'admin', 'password': 'admin'},
                    callback=self.check_login_response)

    def check_login_response(self, response):
        """Check the response returned by a login request to see if we are
        successfully logged in.
        """
        if "Welcome to the awesome admin panel admin" in response.body:
            self.log("Successfully logged in. Let's start crawling!")
            # Now the crawling can begin..
            self.initialized()
            self.parse(response)
        else:
            self.log("Bad times :(")
            # Something went wrong, we couldn't log in, so nothing happens.
    # def parse_item(self, response):
        # Scrape data from page
    def parse(self, response):
        print response.status, "awlejalkwej"
        print response.body
