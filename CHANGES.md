# Version history for deadlink-crawler

## Version 1.1, May 2013
This version was contributed by https://github.com/janhoy
New features in this release:

 * Explicitly chose the Apache Software License for the product, added file LICENSE.txt
 * Added a CHANGES.md file to track changes.
 * Prints intro section with current time, start URL and restritions
 * Prints summary section with stats, timing and number of dead links found
 * Exits with error level 2 if dead links found - nice for acting in a shell script
 * Less verbose. By default it only prints pages crawled and deadlinks found, and a summary at the end
   * option `silent`: Be completely silent. Only print summary at the end. Nice for piping to script.
   * option `debug`: Be super-verbose, printing all links found on each page
 * option `report40x`: Report only 404 as dead, not the other 40x errors
 * option `exclude`: Exclude URLs matching the given regex from the crawl and deadlink-checking

Bug fixes:

 * Password protected pages were reported as dead. Now they are not (re-enable with `--report40x`)
 * Redirects were given wrong URL and reported as dead. Now handling redirects correctly
 * Catch UnicodeEncodeError when fetching and ignores the link
 * Same URL with different fragments, e.g. http://example.com/foo#fragment only needs to be checked once

## Version 1.0, February 2013
This was the first release with initial features

 * `restrict` option for limiting crawl
 * `wait` option for slower crawling
 * `politeness` option for playing nice with same host