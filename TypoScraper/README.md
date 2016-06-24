# TypoScraper

###A Scraper that Looks for Typos in Links

####Purpose and Description

We wrote this tool while researching typosquat and bitsquat domains for ICS vendor. Notably domains such as 'sLemens.com' and 'siemsns.com' and 'schneide-electric.com' were found hosting malware during our research. We thought that it would be a good idea to have a tool to crawl existing websites for typo'd links, because they seemed like good candidates for attackers to register.

Fortunately, not many occurences of such typos have been found. We thought that making the tool publicly available would be nice, though.

One terrific use for this tool is for vendors to scour their support forums. Malicious users may post links on these forums to typo'd domains. This tool may help uncover such links.

####Authors

Reid Wightman [Digital Bond, Inc](http://www.digitalbond.com)

####Prerequisite packages

Python 2.7
Scrapy

####Sample usage

You will have to edit a few lines in the Scraper in order to use it on your website.

locate the line that begins with 'start_urls' and set this to be a url (or multiple urls) corresponding to the sites that you'd like to start spidering. For example you might set this to

start_urls = ['https://www.digitalbond.com']

locate the line that begins with 'rootdomains' and set this to the domains that you'd like to spider. For example you might set this to:

rootdomains = ['digitalbond.com']

You may also wish to change a few of the other hard-coded values. In particular you may want to add filenames to the 'ignoresuffixes' list, for files that should not be retrieved. Adding 'exe' to this list might be a good idea for example, unless your web application actually hosts cgi scripts with .exe scripts or something.

Finally you may need to pay attention to the scraper output. Some websites contain recursive links that will confuse the spider. One example from the digitalbond site is at http://digitalbond.com/page/wiki/Bandolier, which itself contains a link to a 'page/wiki' URI. The scraper will continue blinding following these links, resulting in retrieving URIs like http://digitalbond.com/page/wiki/Bandolier/page/wiki/Bandolier/page/wiki/Bandolier/page/wiki... forever. So, we will ignore any URIs which begin with '/page/wiki/Bandolier'. We can add additional directories to this list if we notice other recursion loops.

####Sample usage

Set the start_url variable to ['http://www.killerrobotsinc.com/'], and set the rootdomains to be ['killerrobotsinc.com'].  Then run the scraper as so:

$ scrapy runspider TypoScraper.py

You should see that a typo'd link is detected to 'www.killerobotsinc.com' (note the ommission of one of the 'r' characters), as in the screenshot below.

![Sample Output] (http://digibond.wpengine.netdna-cdn.com/wp-content/uploads/2016/06/typoscraper-example.jpg)

####Limitations

There are unfortunately a few annoyances with the code. It is great for scraping and finding typo and bitsquat links in simple websites, however any site with links which rely upon heavy use of JavaScript will almost certainly fail.

An unfortunate design decision with separating the URLs from the Domains the way that we do it now, is that the scraper will follow off-site links. For examples if you begin scraping a forum at forum.siemens.com, the scraper will crawl to siemens.com, blog.siemens.com, etc. The excluder will need a bit of rewriting to deal with limiting domains a bit better. Sorry for that.

The code is, in general, not well-written. Use at your own risk with a deprivileged account.

Only run this on your own website. It does not honor robots.txt files, and may cause your webserver some trouble, if your applications can't handle spidering.
