Deadlink crawler
================

This is a small crawler searching your website for deadlinks.

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
