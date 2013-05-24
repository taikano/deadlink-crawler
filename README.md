Deadlink crawler
================

This is a small crawler searching a website for deadlinks.

Dependencies
------------

This program requires **BeautifulSoup** which can be installed using e.g.:  
`sudo easy_install beautifulsoup`

Via command line
----------------

There is a CLI interface to use the crawler. You **must** pass an URL as the starting point for crawling. This might be the home page of your website.

Additional options available are:

- `--restrict`: Restrict crawl to pages with URLs matching the given regular expression
  - If not specified, defaults to all pages within the domain of the start URL
- `--wait`: Time (s) to wait between each URL opening
- `--politeness`: Time to wait (s) between calling two URLs in the same domain
- `--exclude`: Exclude URLs matching the given regex from the crawl and from deadlink-checking
- `--silent`: Turn off verbose output. Only print summary at the end.
- `--debug`: Be super-verbose, printing all links found on each page
- `--report40x`: Report only 404 as dead, not the other 40x errors

Examples:
```bash
# Crawl all subsites of http://stefan-koch.name/ for deadlinks (including external deadlinks)
# Wait one second between opening each URL
python2.7 crawler.py --wait 1 http://stefan-koch.name/

# Crawl all article pages of example.com for deadlinks.
# We assume that there are linked articles on the main page
python2.7 crawler.py --restrict http://example.com/article/.+ http://example.com/

# Crawl all subdomains of example.com, with silent mode and reporting HTTP 40x as dead
python2.7 crawler.py --silent --report40x --restrict http://.*\.example\.com/.* http://www.example.com/

# Crawl example.com, excluding print pages and calendars
python2.7 crawler.py --exclude print|calendar http://www.example.com/
```


Using an instance of the class
------------------------------

You can use it by creating a new instance of the class and running the crawler. The crawler class supports different options.

```python
# Begin crawling at example.com
c = Crawler("http://example.com/")

# Restrict crawling only to your own domain
c.set_url_restrict("http://example.com/.*")

# Set a second wait time between each URL to avoid putting
# too much load on your website. But usually on personal PCs
# this should not matter, because our crawler is not distributed
# and your bandwidth is small.
c.set_wait_time(1)

# start the crawling process
c.crawl()
```

License
-------
The crawler is licensed under the Apache Software License v2.0, see [LICENSE.txt](LICENSE.txt) for details

Version history
---------------
See [CHANGES.md](CHANGES.md) for complete version history
