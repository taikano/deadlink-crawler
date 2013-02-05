import urlparse
import time
import heapq

class Frontier(object):
	def __init__(self):
		# A list containing the next crawltimes on domain level, 
		# to achieve a optimal throughput maintaining a polite policy
		self.frontier = []
		self.websites = {}
		
		# Urls we have already found and in our set
		self.found = set()
		
		self._polite_time = 1
	
	@property
	def polite_time(self):
		return self._polite_time
	
	@polite_time.setter
	def polite_time(self, seconds):
		if seconds >= 0:
			self._polite_time = seconds
	
	def add(self, url, found_via):
		if url in self.found:
			return False
		
		domain = urlparse.urlparse(url).netloc
		
		# means this is the first URL in our set
		if domain in self.websites:
			website = self.websites[domain]
		else:
			website = Website(domain)
			heapq.heappush(self.frontier, (time.time(), website))
			self.websites[domain] = website
		
		website.add_url(url, found_via)
		self.found.add(url)
		
		return True
	
	def next(self):
		next_time, next_domain = heapq.heappop(self.frontier)
		
		next_url = next_domain.next_url()
		
		return next_time, next_url
	
	def notify_visit(self, url):
		domain = urlparse.urlparse(url).netloc
		website = self.websites[domain]
		
		# If there are still other urls on this domain to crawl, add crawl time
		if len(website.urls) > 0:
			heapq.heappush(self.frontier, (time.time() + self.polite_time, website))
		else:
			del(self.websites[domain])
	
	def __len__(self):
		return sum([len(website.urls) for time, website 
			in self.frontier])


class Website(object):
	def __init__(self, domain):
		self.domain = domain
		self.urls = []
		self.robots = None
	
	def is_allowed(self, url):
		# TODO
		return True
	
	def add_url(self, url, found_via):
		self.urls.append((url, found_via))
	
	def next_url(self):
		return self.urls.pop()
