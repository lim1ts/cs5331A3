import urlparse
import requests
import scrapy
import json
from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from scrapy.utils.response import get_base_url

class JavascriptScrap(BaseSpider):
    name = "jsSpider"
    start_urls = [
        "https://app3.com/",
        "https://app1.com/",
        "https://app5.com/",
        "https://app7.com/",
        "https://app9.com/"
    ]
    def verifyAbsolutePath(self, path):
        return bool(urlparse.urlparse(path).netloc)

    def scrapJavascript(self, res, urlPath):
        # javascriptList = res.xpath("//script/@src").extract()
        finalJavascriptList = []
        javascriptList = res
        for src in javascriptList:
            if self.verifyAbsolutePath(src):
                finalJavascriptList.append(src)
            else:
                finalJavascriptList.append(urlPath+src)
        return finalJavascriptList

    def extractEndPointsFromJavascript(self, url, host):
        meth = url.split(",")
        meth[1] = meth[1].strip(" \"\'\n\t\r")
        self.checkIfSrcHasParam(meth[1], host)

    def checkIfSrcHasParam(self, url, host):
        components={}
        if self.verifyAbsolutePath(url):
            components = urlparse.urlparse(url)
        else:
            components = urlparse.urlparse(host+url)
        parameters = urlparse.parse_qs(components.query)
        result = {components.scheme+"://"+components.netloc+components.path:[{"type":"GET"}, parameters]}
        parsed = json.dumps(result)
        with open("test.txt", "a") as outfile:
            json.dump(result, outfile)
            outfile.write("\n")
            outfile.close()

    def connectToJavaScriptSrc(self, src, host):
        requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
        r = requests.get(src, verify = False)
        bodyList = r.content.split("\r")
        for index, content in enumerate(bodyList):
            endpoint = ""
            if "client.open" in content:
                if ");" not in content:
                    # print content.strip()+bodyList[index+1].strip()
                    endpoint = content.strip()+bodyList[index+1].strip(" ").strip(");")
                    # print endpoint
                else:
                    # print content
                    endpoint = content.strip(");")
                    # print endpoint
                self.extractEndPointsFromJavascript(endpoint, host)

    def javascriptStart(self, response):
        jsList = response.xpath("//script/@src").extract()
        # print jsList
        base_url = get_base_url(response)
        thislist = self.scrapJavascript(jsList, base_url);
        for urlSrc in thislist:
            self.connectToJavaScriptSrc(urlSrc, base_url)
            self.checkIfSrcHasParam(urlSrc, base_url)

    def parse(self, response):
        self.javascriptStart(response)
