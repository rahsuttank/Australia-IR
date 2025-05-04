import scrapy
import signal
import sys
import os
import json
from urllib.parse import urlparse
from pathlib import Path
from collections import defaultdict
from twisted.internet import error as twisted_error
import re

class AustraliaWebgraphSpider(scrapy.Spider):
    name = "australia_webgraph"
    
    custom_settings = {
        'DEPTH_LIMIT': 3,
        'CLOSESPIDER_PAGECOUNT': 100000,
        'CONCURRENT_REQUESTS': 200,
        'CONCURRENT_REQUESTS_PER_DOMAIN': 8,
        'DOWNLOAD_DELAY': 0.0,
        'AUTOTHROTTLE_ENABLED': False,
        'REACTOR_THREADPOOL_MAXSIZE': 100,
        'USER_AGENT': 'AusWebGraphBot/1.0 (+https://example.com/bot-info)',
        'LOG_LEVEL': 'INFO',
        'RETRY_ENABLED': True,
        'RETRY_TIMES': 1,
        'RETRY_HTTP_CODES': [500, 502, 503, 504],
        'HTTPCACHE_IGNORE_HTTP_CODES': [403, 404, 408, 429, 500, 502, 503, 504],
        'DOWNLOAD_TIMEOUT': 60,
        'REDIRECT_ENABLED': True,
        'DUPEFILTER_DEBUG': False,
        'DOWNLOAD_MAXSIZE': 4048576,
        'DOWNLOAD_WARNSIZE': 1048576,
        'MEDIA_ALLOW_REDIRECTS': False,
        'HTTPCACHE_ENABLED': False,
        'HTTPCACHE_DIR': '.scrapy_cache',
        'DNSCACHE_ENABLED': True,
        'DNS_TIMEOUT': 10,
        'DOWNLOADER_CLIENT_TLS_METHOD': 'TLSv1.2',
    }

    # File types to skip (common large/binary types)
    BLACKLIST_EXT = {
        '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
        '.jpg', '.jpeg', '.png', '.gif', '.zip', '.tar', '.gz', '.mp3', '.mp4',
        '.csv', '.exe', '.dmg', '.iso', '.rar', '.rtf'
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.webgraph = defaultdict(dict)
        self.seen_urls = set()
        self.failed_urls = set()
        self.domain_failures = defaultdict(int)
        self.MAX_DOMAIN_FAILURES = 10
        self.blacklisted_domains = set()
        self.success_count = 0
        self.MAX_SUCCESS_PAGES = 100000
        self.output_dir = Path("crawl_output")
        self.output_dir.mkdir(exist_ok=True)
        signal.signal(signal.SIGINT, self.emergency_save)
        self.whitespace_re = re.compile(r'\s+')
        self.clean_text_re = re.compile(r'<[^>]+>|{[^}]+}|\[[^\]]+\]')

    def start_requests(self):
        seeds = [
                    # Your Original Seeds
                    "https://www.australia.gov.au/",
                    "https://www.gov.au/",
                    "https://www.my.gov.au/",
                    "https://www.ato.gov.au/",
                    "https://www.servicesaustralia.gov.au/",
                    "https://www.nsw.gov.au/",
                    "https://www.vic.gov.au/",
                    "https://www.qld.gov.au/",
                    "https://www.abc.net.au/",
                    "https://www.smh.com.au/",
                    "https://www.theage.com.au/",
                    "https://www.sbs.com.au/news/",
                    "https://www.unsw.edu.au/",
                    "https://www.unimelb.edu.au/",
                    "https://www.uq.edu.au/",

                    # New Additions
                    "https://en.wikipedia.org/wiki/Australia",
                    "https://en.wikipedia.org/wiki/States_and_territories_of_Australia",
                    "https://www.wa.gov.au/",
                    "https://www.sa.gov.au/",
                    "https://www.tas.gov.au/",
                    "https://nt.gov.au/",
                    "https://www.act.gov.au/",
                    "https://www.cityofsydney.nsw.gov.au/",
                    "https://www.melbourne.vic.gov.au/",
                    "https://www.news.com.au/",
                    "https://www.theaustralian.com.au/",
                    "https://www.afr.com/",
                    "https://www.perthnow.com.au/",
                    "https://www.adelaidenow.com.au/",
                    "https://www.crikey.com.au/",
                    "https://www.anu.edu.au/",
                    "https://www.uwa.edu.au/",
                    "https://www.tafe.nsw.edu.au/",
                    "https://www.accc.gov.au/",
                    "https://www.business.gov.au/",
                    "https://www.australianmining.com.au/",
                    "https://www.nff.org.au/",
                    "https://www.austrade.gov.au/",
                    "https://www.asx.com.au/",
                    "https://www.healthdirect.gov.au/",
                    "https://www.cancer.org.au/",
                    "https://www.beyondblue.org.au/",
                    "https://www.health.wa.gov.au/",
                    "https://www.australia.com/",
                    "https://www.sydneyoperahouse.com/",
                    "https://www.nma.gov.au/",
                    "https://www.visitcanberra.com.au/",
                    "https://www.greatbarrierreef.org/",
                    "https://www.ebay.com.au/",
                    "https://www.gumtree.com.au/",
                    "https://www.coles.com.au/",
                    "https://www.bunnings.com.au/",
                    "https://forums.whirlpool.net.au/",
                    "https://www.reddit.com/r/australia/",
                    "https://www.productreview.com.au/",
                ]

        for url in seeds:
            yield scrapy.Request(
                url, 
                callback=self.parse, 
                meta={'source': url},
                errback=self.handle_error,
                dont_filter=True
            )

    def parse(self, response):
        if response.url in self.seen_urls or response.url in self.failed_urls:
            return
        self.seen_urls.add(response.url)

        content_type = response.headers.get('Content-Type', b'').decode('utf-8').lower()
        if 'html' not in content_type:
            self.logger.debug(f"Skipping non-HTML: {response.url}")
            return

        # Extract page metadata
        title = response.css('title::text').get(default='').strip()
        description = response.css('meta[name="description"]::attr(content)').get(default='').strip()
        main_content = self.extract_main_content(response)
        clean_text = self.clean_text(main_content)

        self.webgraph[response.url] = {
            'title': title,
            'description': description,
            'content': clean_text,
            'links': [],
            'source': response.meta.get('source', '')
        }

        current_url = response.url
        australian_links = set()
        for href in response.css('a::attr(href)').getall():
            try:
                if not href or href.startswith(('javascript:', 'mailto:', 'tel:')):
                    continue
                abs_url = response.urljoin(href.strip())
                parsed = urlparse(abs_url)
                # Skip blacklisted file extensions
                if any(parsed.path.lower().endswith(ext) for ext in self.BLACKLIST_EXT):
                    continue
                # Only follow .au domains
                if '.au' in parsed.netloc or parsed.netloc.endswith('.au'):
                    if abs_url not in self.failed_urls:
                        australian_links.add(abs_url)
            except Exception as e:
                self.logger.debug(f"Link error {href}: {str(e)}")
                continue

        self.webgraph[current_url]['links'] = list(australian_links)

        # Save checkpoint every 1000 pages
        if len(self.webgraph) % 1000 == 0:
            self.save_output(f"checkpoint_{len(self.webgraph)}_")
            self.logger.info(f"Checkpoint saved: {len(self.webgraph)} pages")

        # Prioritize government domains
        gov_domains = ['.gov.au', '.edu.au']
        for link in australian_links:
            meta = {'source': current_url}
            if any(d in link for d in gov_domains):
                meta['download_timeout'] = 90
                meta['download_slot'] = 'gov'
            elif 'news.com.au' in link:
                meta['download_delay'] = 2.0
            yield scrapy.Request(
                link, 
                callback=self.parse, 
                meta=meta, 
                errback=self.handle_error,
                priority=1 if any(d in link for d in gov_domains) else 0
            )

    def extract_main_content(self, response):
        selectors = [
            'article', 'main', '.content', '#content', '.main-content',
            '.article-body', '.post-content', 'div[role="main"]', 'body'
        ]
        for selector in selectors:
            content = response.css(selector).get()
            if content and len(content) > 200:
                return content
        return response.css('body').get() or ''

    def clean_text(self, text):
        if not text:
            return ''
        clean = self.clean_text_re.sub(' ', text)
        clean = self.whitespace_re.sub(' ', clean).strip()
        return clean[:50000]

    def handle_error(self, failure):
        url = failure.request.url
        domain = urlparse(url).netloc
        self.failed_urls.add(url)
        self.domain_failures[domain] += 1
        if self.domain_failures[domain] >= self.MAX_DOMAIN_FAILURES:
            self.blacklisted_domains.add(domain)
            self.logger.warning(f"Domain blacklisted due to repeated failures: {domain}")
        msg = ""
        if failure.check(TimeoutError, twisted_error.TimeoutError, twisted_error.TCPTimedOutError):
            msg = "Timeout"
        elif failure.check(twisted_error.DNSLookupError):
            msg = "DNS lookup failed"
        elif failure.check(twisted_error.ConnectionLost, twisted_error.ConnectionDone):
            msg = "Connection lost"
        else:
            msg = failure.getErrorMessage()
        self.logger.warning(f"Error on {url}: {msg}")
        with open(self.output_dir / "failed_urls.txt", "a") as f:
            f.write(f"{url}\t{msg}\n")

    def save_output(self, prefix=""):
        temp_json = self.output_dir / f"{prefix}webgraph.tmp"
        final_json = self.output_dir / f"{prefix}webgraph.json"
        with temp_json.open('w', encoding='utf-8') as f:
            json.dump(self.webgraph, f, ensure_ascii=False, indent=2)
        os.replace(temp_json, final_json)

        temp_csv = self.output_dir / f"{prefix}webgraph_edges.tmp"
        final_csv = self.output_dir / f"{prefix}webgraph_edges.csv"
        with temp_csv.open('w', encoding='utf-8') as f:
            f.write("source,target\n")
            for source, data in self.webgraph.items():
                for target in data['links']:
                    f.write(f'"{source}","{target}"\n')
        os.replace(temp_csv, final_csv)

        temp_nodes = self.output_dir / f"{prefix}webgraph_nodes.tmp"
        final_nodes = self.output_dir / f"{prefix}webgraph_nodes.csv"
        with temp_nodes.open('w', encoding='utf-8') as f:
            f.write("url,title,description,source\n")
            for url, data in self.webgraph.items():
                title = data['title'].replace('"', '""')
                desc = data['description'].replace('"', '""')
                source = data['source'].replace('"', '""')
                f.write(f'"{url}","{title}","{desc}","{source}"\n')
        os.replace(temp_nodes, final_nodes)

    def emergency_save(self, signum, frame):
        print("\n=== EMERGENCY SAVE INITIATED ===")
        self.save_output("emergency_")
        print(f"Saved {len(self.webgraph)} pages to emergency files")
        sys.exit(0)

    def closed(self, reason):
        self.save_output()
        self.logger.info(f"Final output saved. Total pages: {len(self.webgraph)}")
        self.logger.info(f"Total failed URLs: {len(self.failed_urls)}")

if __name__ == "__main__":
    from scrapy.crawler import CrawlerProcess
    process = CrawlerProcess()
    process.crawl(AustraliaWebgraphSpider)
    process.start()
