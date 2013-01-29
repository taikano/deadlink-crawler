import urlparse
import time
import heapq

class Frontier(object):
	def __init__(self):
		# A list of urls that still have to be searched sorted by
		# domains, 
		self.urls = {}
		
		# A list containing the next crawltimes on domain level, 
		# to achieve a optimal throughput maintaining a polite policy
		self.crawltimes = []
		
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
		if not domain in self.urls:
			self.urls[domain] = []
			heapq.heappush(self.crawltimes, (time.time(), domain))
		
		self.urls[domain].append((url, found_via))
		self.found.add(url)
		
		return True
	
	def next(self):
		next_time, next_domain = heapq.heappop(self.crawltimes)
		
		next_url = self.urls[next_domain].pop()
		
		if len(self.urls[next_domain]) == 0:
			del(self.urls[next_domain])
		
		return next_time, next_url
	
	def notify_visit(self, url):
		domain = urlparse.urlparse(url).netloc
				
		# If there are still other urls on this domain to crawl, add crawl time
		if domain in self.urls:
			heapq.heappush(self.crawltimes, (time.time() + self.polite_time, domain))
	
	def __len__(self):
		return sum([len(self.urls[domain]) for domain in self.urls])
