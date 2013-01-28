from BeautifulSoup import BeautifulSoup
import urllib2, httplib, urlparse
import re
import time
import heapq

import argparse

class Crawler(object):
	def __init__(self, init_url):
		init_domain = urlparse.urlparse(init_url).netloc
		
		# A list of urls that still have to be searched sorted by
		# domains, 
		self.frontier = {}
		self.frontier[init_domain] = [(init_url, None)]
		
		# A list containing the next crawltimes on domain level, 
		# to achieve a optimal throughput maintaining a polite policy
		self.crawltimes = [(time.time(), init_domain)]
		
		# Urls we have already visited
		self.found = set()
		
		# List of deadlinks for each URL we have,
		# i.e. url1: [deadlink1, deadlink2]
		self.deadlinks = {}
		
		# Regular expression for URLs we are interested in (our internal
		# URLs)
		self._url_match = None
		
		# Timeout in seconds to wait, so that we do not kill our server
		self._wait_time = 0
		
		# Timeout for waiting between each call to the same
		# domain twice, this determines how polite the crawler is
		self._polite_time = 1
	
	@property
	def restrict(self):
		return self._url_match
	
	@restrict.setter
	def restrict(self, url_match):
		self._url_match = re.compile(url_match)
	
	@property
	def wait_time(self):
		return self._wait_time
	
	@wait_time.setter
	def wait_time(self, seconds):
		if seconds >= 0:
			self._wait_time = seconds
	
	@property
	def polite_time(self):
		return self._polite_time
	
	@polite_time.setter
	def polite_time(self, seconds):
		if seconds >= 0:
			self._polite_time = seconds
	
	def crawl(self):
		while len(self.frontier) > 0:
			time.sleep(self.wait_time)
			
			next_time, next_domain = heapq.heappop(self.crawltimes)
			next_url = self.frontier[next_domain].pop()
			
			while time.time() < next_time:
				time.sleep(0.5)
			
			if len(self.frontier[next_domain]) > 0:
				next_crawl = time.time() + self.polite_time
				heapq.heappush(self.crawltimes,
					(next_crawl, next_domain))
			else:
				del(self.frontier[next_domain])
			
			try:
				self.visit_url(next_url[0], next_url[1])
			except urllib2.URLError:
				continue
		
		self.print_deadlinks(self.deadlinks)
	
	def visit_url(self, url, found_via):
		response = self.check_url(url, found_via)
		
		if response != None and not self.excluded(url):
			self.collect_new_urls(url, response.read())
	
	def collect_new_urls(self, url, html):
		print("Fetching new URLs from: %s" % url)
		
		try:
			for page in self.extract_urls(html):
				page = urlparse.urljoin(url, page)
				domain = urlparse.urlparse(page).netloc
				
				if not page in self.found:
					if not domain in self.frontier:
						self.frontier.setdefault(domain, [])
						heapq.heappush(self.crawltimes, (time.time(), domain))
					self.frontier[domain].append((page, url))
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
	
	def excluded(self, url):
		return self._url_match != None and not self._url_match.search(url)
	
	def print_deadlinks(self, deadlinks):
		if len(deadlinks) == 0:
			print("No deadlinks were found. Hooray!")
		else:
			print("The following deadlinks were found")
			print()
			for via in deadlinks:
				print("%s" % via)
				for target in deadlinks[via]:
					print("\t%s" % target)


if __name__ == "__main__":
	parser = argparse.ArgumentParser(description="Search a website for deadlinks")
	parser.add_argument('url', metavar='URL', type=str, help="The starting point for your crawl")
	parser.add_argument('--restrict', dest='restrict', help="Restrict the crawl to specific URLs via a regular expression (usually your own domain")
	parser.add_argument('--wait', dest='wait_time', type=float, help="Set some waiting time between each URL fetch")
	parser.add_argument('--politeness', dest='polite_time', type=float, help="Set the time to wait between calling two URLs of the same domain")

	args = parser.parse_args()

	c = Crawler(args.url)
	if args.restrict:
		c.restrict = args.restrict
	if args.wait_time:
		c.wait_time = args.wait_time
	if args.polite_time:
		c.polite_time = args.polite_time
	c.crawl()
