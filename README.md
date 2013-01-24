Deadlink crawler
================

This is a small crawler searching your website for deadlinks.

Via command line
----------------

There is a CLI interface to use the crawler. You **must** pass an URL as the starting point for crawling. This might be the home page of your website.

Additional options available are:

- `--restrict`: Pass a regular expression for restricting your URL to a subset of all websites it finds. Usually you will want to use something like `http://example.com/.*` for this.
- `--wait`: Set some time for waiting in seconds between each URL opening.

```bash
# Crawl all subsites of http://stefan-koch.name/ for deadlinks (including external deadlinks)
python2.7 crawler.py --wait 1 --restrict http://stefan-koch.name/.* http://stefan-koch.name/
# Crawl all article pages of example.com for deadlinks. We assume that there are linked articles on the main page
python2.7 crawler.py --restrict http://example.com/article/.+ http://example.com/
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
