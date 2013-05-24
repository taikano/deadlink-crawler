"""
Deadlink crawler - https://github.com/taikano/deadlink-crawler

Copyright 2013- taikano and other contributors at GitHub

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

from BeautifulSoup import BeautifulSoup
from time import gmtime, strftime, time
import urllib2, httplib, urlparse
import re
import time
import sys
import argparse
import socket
import frontier

class Crawler(object):
	def __init__(self, init_url):
		self.init_url = init_url
		self.init_domain = urlparse.urlparse(init_url).netloc
		
		# Manages our domains we want to visit or have visited
		self.frontier = frontier.Frontier()
		self.frontier.add(init_url, None)
		
		# List of deadlinks for each URL we have,
		# i.e. url1: [deadlink1, deadlink2]
		self.deadlinks = {}
		
		# Regular expression for URLs we are interested in (our internal
		# URLs)
		self._url_match = None
		
		# Regular expression for URLs we are interested in (our internal
		# URLs)
		self._exclude = None

		# Timeout in seconds to wait, so that we do not kill our server
		self._wait_time = 0
		
		# Verbose
		self._verbose = True
		
		# Debug
		self._debug = False
		
		# Report 40x http codes as deadlinks
		self._report40x = False
		
		# For progress reporting
		self._pages = 0
		self._links = 0
		self._via = 0
		self._dead = 0
	
	@property
	def restrict(self):
		return self._url_match
	
	@restrict.setter
	def restrict(self, url_match):
		self._url_match = re.compile(url_match)
	
	@property
	def exclude(self):
		return self._exclude
	
	@exclude.setter
	def exclude(self, exclude):
		self._exclude = re.compile(exclude)

	@property
	def verbose(self):
		return self._verbose
	
	@verbose.setter
	def verbose(self, verbose):
		self._verbose = verbose

	@property
	def debug(self):
		return self._debug
	
	@debug.setter
	def debug(self, debug):
		self._verbose = debug
		self._debug = debug

	@property
	def report40x(self):
		return self._report40x
	
	@report40x.setter
	def report40x(self, report40x):
		self._report40x = report40x

	@property
	def wait_time(self):
		return self._wait_time
	
	@wait_time.setter
	def wait_time(self, seconds):
		if seconds >= 0:
			self._wait_time = seconds
	
	@property
	def polite_time(self):
		return self.frontier.polite_time
	
	@polite_time.setter
	def polite_time(self, seconds):
		if seconds >= 0:
			self.frontier.polite_time = seconds
	
	def crawl(self):
		_starttime = time.time()
		if self.restrict == None:
			self.restrict = "http://%s.*" % self.init_domain

		print "Deadlink-crawler version 1.1"
		print "Starting crawl from URL %s at %s with restriction %s\n" % (self.init_url, strftime("%Y-%m-%d %H:%M:%S", gmtime()), "http://%s.*" % self.init_domain)

		while len(self.frontier) > 0:
			time.sleep(self.wait_time)
			
			next_time, next_url = self.frontier.next()
			
			while time.time() < next_time:
				time.sleep(0.5)
			
			try:
				self.visit_url(next_url[0], next_url[1])
			except urllib2.URLError:
				continue
		
		self.print_deadlinks(self.deadlinks)

		_elapsed = time.time() - _starttime
		
		print "\nSummary:\n--------"
		print "Crawled %d pages and checked %d links in %s time." % (self._pages, self._links, strftime("%H:%M:%S", gmtime(_elapsed)))
		print "Found a total of %d deadlinks in %d different pages" % (self._dead, self._via)
		
		if len(self.deadlinks) == 0:
			exit(0)
		else:
			exit(2)
	
	def visit_url(self, url, found_via):
		response = self.check_url(url, found_via)
		
		self.frontier.notify_visit(url)
			
		if response != None and not self.excluded(url):
			self.collect_new_urls(url, response.read())
	
	def collect_new_urls(self, url, html):
		if self._verbose:
			print("Processing %s" % url)
		
		# Keep track of how many of our site's pages we have crawled, and print status now and then
		self._pages += 1
		if self._pages % 100 == 0:
			print >> sys.stderr, "Processed %s links from %s pages" % (self._links, self._pages)

		try:
			for page in self.extract_urls(html):
				page = urlparse.urljoin(url, page)
				if self._exclude != None and self._exclude.search(page):
					if self._debug:
						print "Not adding link %s to crawl backlog (excluded by --exclude rule)" % page
				else:
					if self.frontier.add(page, url):
						if self._debug:
							print("Adding link %s to crawl backlog" % page)
		except UnicodeEncodeError:
			pass
	
	def check_url(self, url, found_via):
		if self._exclude != None and self._exclude.search(url):
			if self._debug:
				print "Not checking URL %s (excluded by --exclude rule)" % url
			return None
		
		if self._debug:
			print("Checking URL: %s" % url)

		self._links += 1
		request = urllib2.Request(url)
		
		try:
			response = urllib2.urlopen(request, timeout=10)
		except urllib2.HTTPError as e:
			# We receive an exception in case of 404
			if (e.code == 403 or e.code == 401 or e.code == 407) and not self._report40x:
				if self._debug:
					print "Got HTTP %s - not adding to deadlinks list (control with --report40x=True)" % (e.code)
			else:
				if self._debug:
					print "Got HTTP %s - Adding to deadlinks list" % (e.code)
				self.add_to_deadlinks(url, found_via)
			return None
		except httplib.BadStatusLine:
			if self._verbose:
				print "Got Exception BadStatusLine for url %s - Adding to deadlinks list" % url
			self.add_to_deadlinks(url, found_via)
			return None		  
		except UnicodeEncodeError:
			if self._verbose:
				print "Got UnicodeEncodeError for url %s, skipping" % url
			return None
		except urllib2.URLError as e:
			if self._verbose:
				print "Got URLError for page %s" % url
			return None
		except socket.timeout as e:
			print type(e)    #catched
			if self._verbose:
				print "Got timeout reading page %s, skipping" % url
			return None
		
		status = response.getcode()
		redirurl = response.geturl()
		if url != redirurl:
			if self._debug:
				print "Followed redirect from %s to %s" % (url, redirurl)
			url = redirurl
		if status != None and status >= 400:
			self.add_to_deadlinks(url, found_via)
		
		return response
	
	def add_to_deadlinks(self, url, found_via):
		self.deadlinks.setdefault(found_via, [])
		self.deadlinks[found_via].append(url)
		
		self._dead += 1
		
		if self._verbose:
			print "  Found deadlink: %s" % url
	
	def extract_urls(self, page):
		soup = BeautifulSoup(page)
		return [link.get('href') for link in soup.findAll('a')]
	
	def excluded(self, url):
		outside = self._url_match != None and not self._url_match.search(url)
		excluded = self._exclude != None and self._exclude.search(url)
		if excluded and self._debug:
			print "Not following URL %s which is excluded by --exclude rule" % url
		return outside or excluded
	
	def print_deadlinks(self, deadlinks):
		if len(deadlinks) == 0:
			print("\nNo deadlinks were found. Hooray!")
		else:
			print("\nThe following deadlinks were found\n")
			for via in deadlinks:
				self._via += 1
				print("%s" % via)
				for target in deadlinks[via]:
					print("\t%s" % target)


if __name__ == "__main__":
	parser = argparse.ArgumentParser(description="Search a website for deadlinks")
	parser.add_argument('url', metavar='URL', type=str, help="The starting point for your crawl")
	parser.add_argument('--restrict', dest='restrict', help="Restrict the crawl to specific URLs via a regular expression (usually your own domain")
	parser.add_argument('--wait', dest='wait_time', type=float, help="Set some waiting time between each URL fetch")
	parser.add_argument('--politeness', dest='polite_time', type=float, help="Set the time to wait between calling two URLs of the same domain")
	parser.add_argument('--exclude', dest='exclude', help="Exclude URLs matching the given regex from crawl and deadlink-checking")
	parser.add_argument('--silent', dest='silent', action='store_true', default=False, help="Turn off verbose output")
	parser.add_argument('--debug', dest='debug', action='store_true', default=False, help="Be super-verbose")
	parser.add_argument('--report40x', dest='report40x', action='store_true', default=False, help="Report only 404 as dead, not the other 40x errors")

	args = parser.parse_args()

	c = Crawler(args.url)
	if args.restrict:
		c.restrict = args.restrict
	if args.wait_time:
		c.wait_time = args.wait_time
	if args.polite_time:
		c.polite_time = args.polite_time
	if args.silent:
		c.verbose = not args.silent
	if args.debug:
		c.debug = args.debug
	if args.report40x:
		c.report40x = args.report40x
	if args.exclude:
		c.exclude = args.exclude
	c.crawl()
