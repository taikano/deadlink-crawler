from BeautifulSoup import BeautifulSoup
import urllib2, urlparse
import re
import time
import httplib

# TODO: Do not apply wait time to external links

class Crawler(object):
	def __init__(self, init_url):
		# A list of to be crawled urls, where the second element
		# in the tuple is the URL via which we found this URL
		self.pages = [(init_url, None)]
		
		# Urls we have already visited
		self.found = set()
		
		# List of deadlinks for each URL we have,
		# i.e. url1: [deadlink1, deadlink2]
		self.deadlinks = {}
		
		# Regular expression for URLs we are interested in (our internal
		# URLs)
		self.url_match = None
		
		# Timeout in seconds to wait, so that we do not kill our server
		self.wait_time = 0
	
	def set_url_restrict(self, regexp):
		self.url_match = re.compile(regexp)
	
	def set_wait_time(self, seconds):
		self.wait_time = seconds
	
	def crawl(self):
		while len(self.pages) > 0:
			time.sleep(self.wait_time)
			
			next_url = self.pages.pop()
			
			try:
				self.visit_url(next_url[0], next_url[1])
			except urllib2.URLError:
				continue
		
		print("DEADLINKS")
		print(self.deadlinks)
	
	def visit_url(self, url, found_via):
		response = self.check_url(url, found_via)
		
		if response != None and self.url_match.search(url):
			self.collect_new_urls(url, response.read())
	
	def collect_new_urls(self, url, html):
		print("Fetching new URLs from: %s" % url)
		
		try:
			for page in self.extract_urls(html):
				page = urlparse.urljoin(url, page)
				
				if not page in self.found:
					self.pages.append((page, url))
					self.found.add(page)
		except UnicodeEncodeError:
			pass
	
	def check_url(self, url, found_via):
		print("Trying URL: %s" % url)
		
		request = urllib2.Request(url)
		
		try:
			response = urllib2.urlopen(request, None, 10)
		except (urllib2.HTTPError, httplib.BadStatusLine):
			# We receive an exception in case of 404
			self.add_to_deadlinks(url, found_via)
			return None
		
		status = response.getcode()
		if status != None and status >= 400:
			self.add_to_deadlinks(url, found_via)
		
		return response
	
	def add_to_deadlinks(self, url, found_via):
		self.deadlinks.setdefault(found_via, [])
		self.deadlinks[found_via].append(url)
		
		print("Found new deadlink %s on %s" % (url, found_via))
	
	def extract_urls(self, page):
		soup = BeautifulSoup(page)
		return [link.get('href') for link in soup.findAll('a')]
	

c = Crawler("http://stefan-koch.name/")
c.set_url_restrict("http://stefan-koch.name/.*")
c.set_wait_time(1)
c.crawl()
