from BeautifulSoup import BeautifulSoup
import urllib2, urlparse
import re
import time

class Crawler(object):
	def __init__(self, init_url):
		self.pages = [init_url]
		self.done = set()
		
		self.url_match = None
		self.wait_time = 0
	
	def set_url_restrict(self, regexp):
		self.url_match = re.compile(regexp)
	
	def set_wait_time(self, seconds):
		self.wait_time = seconds
	
	def crawl(self):
		while len(self.pages) > 0:
			time.sleep(self.wait_time)
			
			next_url = self.pages.pop()
			print next_url
			
			try:
				html = self.visit_url(next_url)
			except:
				continue
			finally:
				self.done.add(next_url)
			
			try:
				for page in self.extract_urls(html):
					page = urlparse.urljoin(next_url, page)
					
					if not page in self.done and self.url_match.search(page):
						self.pages.append(page)
			except UnicodeEncodeError:
				pass
	
	def visit_url(self, url):
		return urllib2.urlopen(url)
	
	def extract_urls(self, page):
		soup = BeautifulSoup(page)
		return [link.get('href') for link in soup.findAll('a')]
	

c = Crawler("http://stefan-koch.name/")
c.set_url_restrict("http://stefan-koch.name/.+")
c.set_wait_time(5)
c.crawl()
