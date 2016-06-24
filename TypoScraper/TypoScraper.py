import scrapy
from scrapy import signals
from scrapy.xlib.pydispatch import dispatcher

import dnstwist
import sys



class TypoScraper(scrapy.Spider):
    name = 'Squat Typo Searcher'
    start_urls = ['http://www.killerrobotsinc.com'] #['https://support.industry.siemens.com/tf/us/en/'] #['http://www.readingfordummies.com']
    rootdomains = ['killerrobotsinc.com'] # ['siemens.com'] #['readingfordummies.com']
    squatdomains = dnstwist.fuzz_domain(rootdomains[0]) # only works for one domain right now, whee
    checkedPages = []
    bogons = []
    ignoresuffixes = ['mov', 'jpg', 'pdf', 'doc', 'zip', 'bin', 'docx']
    ignoredirectories = ['/page/wiki/Bandolier'] # digitalbond.com has a loop on this uri
    download_maxsize = 1048576
    
    #def __init__(self):
        #dispatcher.connect(self.allDone, signals.spider_closed)
        
    
    # extract just the fully qualified domain name from a URL
    # e.g. "www.digitalbond.com"
    def extract_fqdn(self, full_url):
        return
    # extract the root domain from a URL
    # e.g. "digitalbond.com"
    # sorry this function has so many exits, should clean it up...
    def extract_root_domain(self, full_url):
        if full_url[0:7] == "mailto:":
            print "email link: ", full_url
            if "@" in full_url:
                mantissa = full_url.split("@")[1]
                return mantissa
            else:
                return None
        else:
            try:
                mantissa = full_url.split("://")[1].split("/")[0] # gets out the main part, e.g. 'www.digitalbond.com'
                domain = '.'.join(mantissa.split('.')[-2:]) # get the last two chunks and re-append them with '.', e.g. 'digitalbond.com'
                return domain                
            except:
                #print "error on url: ", full_url
                return None
       

    def url_in_domain(self, full_url):
        domain = self.extract_root_domain(full_url)
        if domain in self.rootdomains:
            return True
        else:
            return False
    # check whether the filename extension is in the ignore list (e.g. don't download ".mov" files)   
    def url_suffix_OK(self, full_url):
        suffix = full_url.split(".")[-1]
        if suffix in self.ignoresuffixes:
            return False
        else:
            return True
    # check whether the url is in a list of directories to ignore
    # we may want to add 'repetitious/circular link' detection as well.
    def url_ignore(self, full_url):
        if full_url[0:7] == "mailto:":
            return True
        print "checking %s" % full_url
        directory = "/".join(full_url.split("://")[1].split("/"))
        for ignoredirectory in self.ignoredirectories:
            if ignoredirectory in directory:
                return True # ignore this path
        return False
    # check if we should follow a link
    # checks if link is:
    # 1) in the right domain for us to care about
    # 2) url was checked already
    # 3) url has a suffix that we want to retrieve
    def link_shouldfollow(self, full_url):
        if not self.url_in_domain(full_url):
            return False
        if full_url in self.checkedPages:
            return False
        if not self.url_suffix_OK(full_url):
            return False
        if self.url_ignore(full_url):
            return False # url was in ignore list
        return True
    
    def testforTypo(self, full_url):
        linkdomain = self.extract_root_domain(full_url)
        for domain in self.squatdomains:
            if linkdomain == domain['domain']:
                return True
        # no match found
        return False
    
    def testforTyposR(self, response):
        # check response urls for typos
        for href in response.css('a::attr(href)'):
            full_url = response.urljoin(href.extract())
            if self.testforTypo(full_url):
                # got a bogon! Do not follow the link
                print "=========bogon detected! %s" % full_url
                self.bogons.append(full_url)
                continue # continue to next href in response
            if self.link_shouldfollow(full_url): # check if link is to a page we care about, and hasn't been checked already
                ## see if the page has been checked
                # add to checkedPages
                self.checkedPages.append(full_url)
                # dispatch to subprocess
                yield scrapy.Request(full_url, self.testforTyposR)
            else:
                # url is to some outside website (twitter, etc), so drop it
                continue
                # then add to 
            
        return # yield?
    
    def parse(self, response):
        for href in response.css('a::attr(href)'):
            full_url = response.urljoin(href.extract())
            if self.testforTypo(full_url):
                self.bogons.append(full_url)
                continue
            if self.url_in_domain(full_url):
                # recurse
                yield scrapy.Request(full_url, callback=self.testforTyposR)
            else:
                continue # skip over external links
        print "The following bogons were found:"
        print self.bogons

    def start_requests(self):
        for url in self.start_urls:
            print 'building form request for ', url
            yield scrapy.FormRequest(url, callback=self.parse)
        return
    
    def close(self, spider):
        print "Penultimate final list of bogons: ", self.bogons
        return
        
        
def main():
    print "Making a scraper object"
    myscraper = TypoScraper(name='Squat Typo Scraper')
    argnum = 1
    myscraper.start_urls = []
    print "Building URL list"
    while argnum < len(sys.argv):
        myscraper.start_urls.append(sys.argv[argnum])
        argnum += 1
    print "Building domain list"
    myscraper.rootdomains = []
    for url in myscraper.start_urls:
        myscraper.rootdomains.append(myscraper.extract_root_domain(url))
    print "domain list: ", myscraper.rootdomains
    print "Building squat list"
    # dictionary of domains, each domain gets 
    myscraper.squatdomains = {}
    for domain in myscraper.rootdomains:
        myscraper.squatdomains[domain] = dnstwist.fuzz_domain(domain)
        
    # setup is done, print info?
    print "url list: "
    for url in myscraper.start_urls:
        print url
        for squat in myscraper.squatdomains[myscraper.extract_root_domain(url)]:
            print "\t", squat['domain']
    print "starting requests"
    myscraper.start_requests()
    
    return

#if __name__ == '__main__':
    #print "Calling main"
    #main()
