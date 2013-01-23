from BeautifulSoup import BeautifulSoup
import urllib2, urlparse
import re
import time

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
				self.visit_url(next_url)
			except urllib2.URLError:
				continue
	
	def visit_url(self, url_tuple):
		if self.url_match.search(url_tuple[0]):
			self.visit_url_internal(url_tuple[0])
		else:
			self.visit_url_external(url_tuple[0], url_tuple[1])
	
	def visit_url_internal(self, url):
		print("Crawling internal: %s" % url)
		
		html = urllib2.urlopen(url)
		
		try:
			for page in self.extract_urls(html):
				page = urlparse.urljoin(url, page)
				
				if not page in self.found:
					self.pages.append((page, url))
					self.found.add(page)
		except UnicodeEncodeError:
			pass
	
	def visit_url_external(self, url, found_via):
		print("Trying external: %s" % url)
		
		request = urllib2.Request(url)
		
		try:
			response = urllib2.urlopen(request)
		except urllib2.HTTPError:
			# We receive an exception in case of 404
			self.add_to_deadlinks(url, found_via)
			return
		
		status = response.getcode()
		if status != None and status >= 400:
			self.add_to_deadlinks(url, found_via)
	
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
