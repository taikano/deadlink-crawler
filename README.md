Deadlink crawler
================

This is a small crawler searching your website for deadlinks.

Dependencies
------------

This program requires **BeautifulSoup** which can be installed using e.g.

`sudo easy_install beautifulsoup`

Via command line
----------------

There is a CLI interface to use the crawler. You **must** pass an URL as the starting point for crawling. This might be the home page of your website.

Additional options available are:

- `--restrict`: Pass a regular expression for restricting your URL to a subset of all websites it finds. Defaults to domain of start URL.
- `--wait`: Set some time for waiting in seconds between each URL opening.
- `--politeness`: Set the time to wait between calling two URLs of the same domain
- `--exclude`: Exclude URLs matching the given regex from the crawl
- `--silent`: Turn off verbose output. Only print summary at the end.
- `--debug`: Be super-verbose, printing all links found on each page
- `--report40x`: Report only 404 as dead, not the other 40x errors

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
The crawler is licensed under the Apache Software License v2.0, see LICENSE.txt for details

Version history
---------------
See CHANGES.md for complete version history
