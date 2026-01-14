from bs4 import BeautifulSoup, NavigableString
import requests
import os
from tqdm import tqdm
import chardet
import pandas as pd
import logging
import json
import time
from selenium.webdriver.common.by import By
from . import ips
import random
try:
    import scrapy
except ImportError:
    scrapy = None

dir_save = "/Users/macjianfeng/Dropbox/Downloads/"
# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
# Suppress WDM INFO logs
logging.getLogger("WDM").setLevel(logging.WARNING)
proxies_glob = None

# Define supported content types and corresponding parsers
CONTENT_PARSERS = {
    "text/html": lambda text, parser: BeautifulSoup(text, parser),
    "application/json": lambda text, parser: json.loads(text),
    "text/xml": lambda text, parser: BeautifulSoup(text, parser),
    "text/plain": lambda text, parser: text.text,
}
 
# Fallback pool of common User-Agent strings
fallback_user_agents = [
    # Chrome (Windows)
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
    # Firefox (Mac)
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:106.0) Gecko/20100101 Firefox/106.0",
    # Edge (Windows)
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36 Edg/115.0.1901.203",
    # Safari (Mac)
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.1 Safari/605.1.15",
    # Linux Chrome
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.5993.90 Safari/537.36",
    # Android Tablet (Samsung)
    "Mozilla/5.0 (Linux; Android 9; SAMSUNG SM-T860) AppleWebKit/537.36 (KHTML, like Gecko) SamsungBrowser/10.1 Chrome/71.0.3578.99 Safari/537.36",
    # iPhone Safari
    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.4 Mobile/15E148 Safari/604.1",
    # Android Mobile Chrome
    "Mozilla/5.0 (Linux; Android 11; Pixel 4a) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.5481.154 Mobile Safari/537.36",
    # iPad Safari
    "Mozilla/5.0 (iPad; CPU OS 15_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.2 Mobile/15E148 Safari/604.1",
    # Opera (Windows)
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.60 Safari/537.36 OPR/86.0.4363.32",
    # Brave (Mac)
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_5_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36",
    # Vivaldi (Windows)
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36 Vivaldi/5.1.2567.49",
    # Android Chrome OnePlus
    "Mozilla/5.0 (Linux; Android 10; ONEPLUS A6010) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.74 Mobile Safari/537.36",
    # Samsung Galaxy S22 Chrome
    "Mozilla/5.0 (Linux; Android 12; SAMSUNG SM-S901B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Mobile Safari/537.36",
    # Xiaomi MIUI Browser
    "Mozilla/5.0 (Linux; Android 11; M2012K11AG) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.125 Mobile Safari/537.36",
    # Desktop Safari on macOS Ventura
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_0) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Safari/605.1.15",
]
def user_agent(
    browsers=["chrome", "edge", "firefox", "safari"],
    platforms=["pc", "tablet"],
    verbose=False,
    os_names=["windows", "macos", "linux"],
):
    import warnings
    import traceback

    try:
        from fake_useragent import UserAgent

        ua = UserAgent(browsers=browsers, platforms=platforms, os=os_names)
        output_ua = ua.random
    except Exception as e:
        warnings.warn("fake_useragent failed, using fallback list instead.\n" + str(e))
        if verbose:
            traceback.print_exc()
        output_ua = random.choice(fallback_user_agents)

    if verbose:
        print("Selected User-Agent:", output_ua)

    return output_ua

def get_tags(content, ascending=True):
    tag_names = set()

    # Iterate through all tags in the parsed HTML
    for tag in content.find_all(True):  # `True` finds all tags
        tag_names.add(tag.name)  # Add the tag name to the set

    # Convert set to a sorted list for easier reading (optional)
    if ascending is None:
        return tag_names
    else:
        if ascending:
            return sorted(tag_names)
        else:
            return tag_names


def get_attr(content, where=None, attr=None, **kwargs):
    """
    usage: nt.get_attr(soup, where="a", attr="href", class_="res-1foik6i")

    Extracts the specified attribute from tags in the content.

    Parameters:
    - content: BeautifulSoup object of the HTML content.
    - where: The tag name to search for (e.g., 'time').
    - attr: The attribute to extract (e.g., 'datetime').
    - kwargs: Additional filtering conditions for find_all.

    Returns:
    - A list of attribute values if found; otherwise, prints debug info.
    """
    # Extract all tags from the content
    all_tags = get_tags(content)
    if all([where, attr]):
        if where in all_tags:
            if kwargs:
                element_ = content.find_all(where, **kwargs)
            else:
                element_ = content.find_all(where)
            attr_values = [i.get(attr) for i in element_ if i.has_attr(attr)]
            if attr_values:
                return attr_values
            else:
                print(f"The attribute '{attr}' is not found in the elements.")
        else:
            from pprint import pp

            print(f"Cannot find tag '{where}' in the content.")
            print("Available tags:")
            pp(all_tags)
    else:
        print("Please provide both 'where' (tag name) and 'attr' (attribute).")


def extract_text_from_content(
    content, content_type="text/html", where=None, what=None, extend=True, **kwargs
):
    """
    Extracts text from the given content based on the specified content type and search criteria.

    Parameters:
    - content (str/BeautifulSoup): The content to extract text from.
    - content_type (str): The type of content, e.g., "text/html" or "application/json".
    - where (str/list): The HTML tag or list of tags to search for.
    - what (str): The class name to filter the tags (optional).
    - extend (bool): Whether to recursively extract text from child elements.
    - **kwargs: Additional keyword arguments for the search (e.g., id, attributes).

    Returns:
    - list: A list of extracted text segments.
    """

    def extract_text(element):
        texts = ""
        if isinstance(element, NavigableString) and element.strip():  
            texts += element.strip() + " " 
        elif hasattr(element, "children"):
            for child in element.children:
                texts += extract_text(child)
        return texts

    if content is None:
        logger.error("Content is None, cannot extract text.")
        return []

    if content_type not in CONTENT_PARSERS:
        logger.error(f"Unsupported content type: {content_type}")
        return []
    if "json" in content_type:
        where = None
        return extract_text_from_json(content, where)
    elif "text" in content_type:
        if isinstance(where, list):
            res = []
            for where_ in where:
                res.extend(
                    extract_text_from_content(
                        content,
                        content_type="text/html",
                        where=where_,
                        what=what,
                        extend=extend,
                        **kwargs,
                    )
                )
            return res
        else:
            search_kwargs = {**kwargs}
            # correct 'class_'
            # dict_=dict(class_="gsc_mnd_art_info")
            if "class_" in search_kwargs:
                search_kwargs["class"] = search_kwargs["class_"]
                del search_kwargs["class_"]
            if what:
                search_kwargs["class"] = what
            if "attrs" in kwargs:
                result_set = content.find_all(where, **search_kwargs)
            else:
                result_set = content.find_all(where, attrs=dict(**search_kwargs))
            if "get" in kwargs:
                del search_kwargs["get"]  # rm 'get' key
                return get_attr(
                    content, where=where, attr=kwargs["get"], **search_kwargs
                )
            if not result_set:
                print("Failed: check the 'attrs' setting:  attrs={'id':'xample'}")
            if extend:
                texts = ""
                for tag in result_set:
                    texts = texts + " " + extract_text(tag) + " \n"
                    # texts = texts + " " + tag.get_text(" ", strip=True)+ " \n"
                    
                text_list = [tx.strip() for tx in texts.split(" \n") if tx.strip()]
                return text_list
            else:
                # texts_ = " ".join(tag.get_text() for tag in result_set)
                texts_ = []
                for tag in result_set:
                    for child in tag.children:
                        if child.name is None:
                            texts_.append(child.strip())
                # texts_=" ".join(texts_)
                # texts = [tx.strip() for tx in texts_.split("\n") if tx.strip()]
                texts = [tx.strip() for tx in texts_ if tx.strip()]
                return texts


def extract_text_from_json(content, key=None):
    if key:
        if isinstance(content, list):
            return [str(item.get(key, "")) for item in content if key in item]
        if isinstance(content, dict):
            return [str(content.get(key, ""))]
    else:
        return [str(value) for key, value in flatten_json(content).items()]


def flatten_json(y):
    out = {}

    def flatten(x, name=""):
        if isinstance(x, dict):
            for a in x:
                flatten(x[a], name + a + "_")
        elif isinstance(x, list):
            i = 0
            for a in x:
                flatten(a, name + str(i) + "_")
                i += 1
        else:
            out[name[:-1]] = x

    flatten(y)
    return out


def get_proxy():
    import random

    list_ = []
    headers = {"User-Agent": user_agent()}
    response = requests.get(
        "https://free-proxy-list.net", headers=headers, timeout=30, stream=True
    )
    content = BeautifulSoup(response.content, "html.parser")
    info = extract_text_from_content(content, where="td", extend=0)[0].split()
    count, pair_proxy = 0, 2
    for i, j in enumerate(info):
        if "." in j:
            list_.append(j + ":" + info[i + 1])
            # list_.append()  # Assuming the next item is the value
            count += 1
            # if count == pair_proxy:  # Stop after extracting the desired number of pairs
            #     break
    prox = random.sample(list_, 2)
    proxies = {
        "http": f"http://" + prox[0],
        "https": f"http://" + prox[1],
    }
    return proxies


# proxies_glob=get_proxy()
def get_soup(url, **kwargs):
    _, soup_ = fetch_all(url, **kwargs)
    return soup_


def get_cookies(url, login={"username": "your_username", "password": "your_password"}):
    session = requests.Session()
    response = session.post(url, login)
    cookies_dict = session.cookies.get_dict()
    return cookies_dict


### 更加平滑地移动鼠标, 这样更容易反爬
def scroll_smth_steps(driver, scroll_pause=0.5, min_step=200, max_step=600):
    import random

    """Smoothly scrolls down the page to trigger lazy loading."""
    current_scroll_position = 0
    end_of_page = driver.execute_script("return document.body.scrollHeight")

    while current_scroll_position < end_of_page:
        step = random.randint(min_step, max_step)
        driver.execute_script(f"window.scrollBy(0, {step});")
        time.sleep(scroll_pause)

        # Update the current scroll position
        current_scroll_position += step
        end_of_page = driver.execute_script("return document.body.scrollHeight")


def scroll_inf2end(driver, scroll_pause=1):
    """Continuously scrolls until the end of the page is reached."""
    last_height = driver.execute_script("return document.body.scrollHeight")

    while True:
        # Scroll to the bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(scroll_pause)

        # Get the new height after scrolling
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break  # Exit if no new content is loaded
        last_height = new_height


def corr_by_kind(wait_until_kind):
    """
    Map the 'wait_until_kind' string to the appropriate Selenium By strategy.
    """
    if "tag" in wait_until_kind:
        return By.TAG_NAME
    elif "css" in wait_until_kind:
        return By.CSS_SELECTOR
    elif "id" in wait_until_kind:
        return By.ID
    elif "name" in wait_until_kind:
        return By.NAME
    elif "class" in wait_until_kind:
        return By.CLASS_NAME
    elif "path" in wait_until_kind:
        return By.XPATH
    elif "link" in wait_until_kind or "text" in wait_until_kind:
        return By.LINK_TEXT
    else:
        raise ValueError(f"Unsupported wait_until_kind: {wait_until_kind}")




def parse_cookies(cookies_str):
    """
    直接复制于browser,它可以负责转换成最终的dict
    """
    import re
    cookies_dict = {}

    # Split the string by newlines to get each cookie row
    cookies_list = cookies_str.strip().split("\n")

    for cookie in cookies_list:
        # Use regular expression to capture name and value pairs
        match = re.match(r"([a-zA-Z0-9_\-\.]+)\s+([^\s]+)", cookie)
        if match:
            cookie_name = match.group(1)
            cookie_value = match.group(2)
            cookies_dict[cookie_name] = cookie_value

    return cookies_dict
def fetch_scrapy(
    url,
    parser="html.parser",
    cookies=None,
    headers=None,
    settings=None,
):
    """
    Fetches content using Scrapy with proper reactor handling.

    Args:
        url (str): The URL to scrape.
        parser (str): Parser for BeautifulSoup (e.g., "lxml", "html.parser").
        cookies (dict): Cookies to pass in the request.
        headers (dict): HTTP headers for the request.
        settings (dict): Scrapy settings, if any.

    Returns:
        dict: Parsed content as a dictionary.
    """
    from scrapy.utils.project import get_project_settings
    from scrapy.crawler import CrawlerRunner
    from scrapy.signalmanager import dispatcher
    from scrapy import signals
    from twisted.internet import reactor, defer
    from twisted.internet.error import ReactorNotRestartable
    import scrapy
    import logging

    # Disable Scrapy's excessive logging
    logging.getLogger('scrapy').setLevel(logging.WARNING)
    logging.getLogger('twisted').setLevel(logging.WARNING)

    # Container for scraped content
    content = []

    # Define the spider class inside the function
    class FetchSpider(scrapy.Spider):
        name = "fetch_spider"
        
        def __init__(self, url=None, parser=None, cookies=None, headers=None, *args, **kwargs):
            super(FetchSpider, self).__init__(*args, **kwargs)
            self.start_urls = [url]
            self.parser = parser
            self.cookies = cookies
            self.headers = headers

        def start_requests(self):
            for url in self.start_urls:
                yield scrapy.Request(
                    url,
                    cookies=self.cookies,
                    headers=self.headers,
                    callback=self.parse
                )

        def parse(self, response):
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(response.text, self.parser)
            yield {
                "content": soup,
                "url": response.url,
                "status": response.status
            }

    # Callback function for item scraped signal
    def handle_item(item, response, spider):
        content.append(item)

    # Scrapy settings
    process_settings = settings or get_project_settings()
    process_settings.update(
        {
            "USER_AGENT": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "DOWNLOAD_DELAY": 1,
            "COOKIES_ENABLED": bool(cookies),
            "LOG_LEVEL": "ERROR",
            "RETRY_ENABLED": False,
            "HTTPERROR_ALLOW_ALL": True,
        }
    )

    # Connect item scraped signal
    dispatcher.connect(handle_item, signal=signals.item_scraped)

    # Asynchronous Twisted function
    @defer.inlineCallbacks
    def crawl():
        runner = CrawlerRunner(settings=process_settings)
        yield runner.crawl(
            FetchSpider,
            url=url,
            parser=parser,
            cookies=cookies,
            headers=headers,
        )
        reactor.stop()

    # Handle reactor execution
    try:
        if not reactor.running:
            crawl()
            reactor.run(installSignalHandlers=0)
        else:
            # This case is problematic - reactor can't be restarted
            raise RuntimeError("Reactor already running. Cannot run multiple crawls in same process.")
    except ReactorNotRestartable:
        raise RuntimeError("Scrapy reactor cannot be restarted. Create a new process for additional crawls.")

    # Return the first scraped content or None if empty
    return content[0] if content else None

def _clean_temp():
    import os
    import shutil
    import tempfile
    from pathlib import Path

    # Get the parent folder of the tempdir
    temp_dir = Path(tempfile.gettempdir()).parent  # moves from /T to parent dir

    for subdir in temp_dir.iterdir():
        if subdir.is_dir():
            for d in subdir.iterdir():
                if "com.google.Chrome.code_sign_clone" in d.name:
                    try:
                        print(f"Removing: {d}")
                        shutil.rmtree(d)
                    except Exception as e:
                        print(f"Error removing {d}: {e}")
def fetch_all(
    url,
    parser="lxml",
    driver="request",  # request or selenium
    by=By.TAG_NAME,
    timeout=10,
    retry=3,  # Increased default retries
    wait=0,
    wait_until=None,
    wait_until_kind=None,
    scroll_try=3,
    login_url=None,
    username=None,
    password=None,
    username_field="username",
    password_field="password",
    submit_field="submit",
    username_by=By.NAME,
    password_by=By.NAME,
    submit_by=By.NAME,
    proxy=None,
    javascript=True,
    disable_images=False,
    iframe_name=None,
    login_dict=None,
    cookies=None,
    verify_ssl=True,  # Added SSL verification option
    follow_redirects=True,  # Added redirect control
):
    """
    Enhanced fetch function with better error handling and reliability.
    
    Returns:
        tuple: (content_type, parsed_content) or (None, None) on failure
    """
    def _parse_content(content, content_type, parser):
        """Helper function to parse content with fallback"""
        try:
            if content_type in CONTENT_PARSERS:
                return CONTENT_PARSERS[content_type](content, parser)
            
            # Fallback parsing attempts
            if content_type.startswith('text/'):
                try:
                    return BeautifulSoup(content, parser)
                except:
                    return content
            return content
        except Exception as e:
            logger.warning(f"Content parsing failed: {e}")
            return content

    def _make_request(url, headers, cookies, timeout, verify_ssl, follow_redirects):
        """Helper function for HTTP requests with retries"""
        for attempt in range(retry):
            try:
                response = requests.get(
                    url,
                    headers=headers,
                    cookies=cookies,
                    timeout=timeout,
                    stream=True,
                    verify=verify_ssl,
                    allow_redirects=follow_redirects
                )
                
                # Handle redirects manually if needed
                if not follow_redirects and response.is_redirect:
                    logger.info(f"Redirect detected to: {response.headers['Location']}")
                    return None, None
                
                response.raise_for_status()
                return response, None
                
            except requests.RequestException as e:
                logger.warning(f"Attempt {attempt + 1} failed: {e}")
                if attempt == retry - 1:
                    return None, e
                time.sleep(random.uniform(1, 3))
    
    # Convert driver integer to string if needed
    if isinstance(driver, int):
        drivers = ["request", "selenium", "scrapy"]
        try:
            driver = drivers[driver]
        except IndexError:
            driver = "request"
    
    headers = {"User-Agent": user_agent()}
    
    # Prepare cookies
    cookie_jar = None
    if cookies:
        from requests.cookies import RequestsCookieJar
        cookie_jar = RequestsCookieJar()
        if isinstance(cookies, str):
            cookies = parse_cookies(cookies)
        for name, value in cookies.items():
            cookie_jar.set(name, value)
    
    try:
        if "req" in driver.lower():
            response, error = _make_request(
                url, headers, cookie_jar, timeout, verify_ssl, follow_redirects
            )
            if error:
                return None, None
            content_type = response.headers.get("content-type", "").split(";")[0].lower()
            try:
                detected = chardet.detect(response.content)
                encoding = detected.get("encoding") or "utf-8"
                content = response.content.decode(encoding, errors='replace')
            except:
                content = response.content.decode(response.encoding or 'utf-8', errors='replace')
            
            return content_type, _parse_content(content, content_type, parser)
            
        elif "se" in driver.lower():
            from selenium import webdriver
            from selenium.webdriver.chrome.service import Service
            from selenium.webdriver.chrome.options import Options
            from webdriver_manager.chrome import ChromeDriverManager
            from selenium.common.exceptions import WebDriverException
            
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument(f'--user-data-dir={os.path.expanduser("~/selenium_profile")}')
            chrome_options.add_argument(f"user-agent={user_agent()}")
            
            if proxy:
                chrome_options.add_argument(f"--proxy-server={proxy}")
            if disable_images:
                chrome_options.add_experimental_option(
                    "prefs", {"profile.managed_default_content_settings.images": 2}
                )
            
            driver_instance = None
            try:
                # Try with latest ChromeDriver first
                service = Service(ChromeDriverManager().install())
                driver_instance = webdriver.Chrome(service=service, options=chrome_options)
                
                # Configure wait times
                if 3 < wait < 5:
                    wait_time = random.uniform(3, 5)
                elif 5 <= wait < 8:
                    wait_time = random.uniform(5, 8)
                elif 8 <= wait < 12:
                    wait_time = random.uniform(8, 10)
                else:
                    wait_time = 0
                
                driver_instance.implicitly_wait(wait_time)
                
                # Handle login if needed
                if login_url and login_dict:
                    cookies = get_cookies(url=login_url, login=login_dict)
                    driver_instance.get(url)
                    for name, value in cookies.items():
                        driver_instance.add_cookie({"name": name, "value": value})
                elif cookies:
                    driver_instance.get(url)
                    if isinstance(cookies, str):
                        cookies = parse_cookies(cookies)
                    for name, value in cookies.items():
                        driver_instance.add_cookie({"name": name, "value": value})
                
                if not javascript:
                    driver_instance.execute_cdp_cmd(
                        "Emulation.setScriptExecutionDisabled", {"value": True}
                    )
                
                # Navigate to target URL
                driver_instance.get(url)
                
                # Handle iframes if needed
                if iframe_name:
                    iframe = WebDriverWait(driver_instance, timeout).until(
                        EC.presence_of_element_located((By.NAME, iframe_name))
                    )
                    driver_instance.switch_to.frame(iframe)
                
                # Scroll to trigger dynamic content
                scroll_smth_steps(driver_instance)
                
                # Get page source with retries
                content = None
                for attempt in range(scroll_try):
                    try:
                        page_source = driver_instance.page_source
                        content = BeautifulSoup(page_source, parser)
                        if content and content.find_all(by):
                            break
                    except Exception as e:
                        logger.warning(f"Attempt {attempt + 1} failed: {e}")
                    time.sleep(random.uniform(1, 3))
                try:
                    _clean_temp()
                except Exception as e:
                    print(e)
                return "text/html", content if content else None
                
            except WebDriverException as e:
                logger.error(f"Selenium error: {e}")
                return None, None
            finally:
                if driver_instance:
                    driver_instance.quit()
                    
        elif 'scr' in driver.lower():
            settings = {
                "USER_AGENT": user_agent(),
                "DOWNLOAD_DELAY": 1,
                "COOKIES_ENABLED": bool(cookies),
                "LOG_LEVEL": "WARNING",
                "RETRY_TIMES": retry,
                "DOWNLOAD_TIMEOUT": timeout,
            }
            content = fetch_scrapy(
                url, 
                parser=parser, 
                cookies=cookies, 
                headers=headers, 
                settings=settings
            )
            return parser, content
            
    except Exception as e:
        logger.error(f"Unexpected error in fetch_all: {e}")
        return None, None
    
    return None, None

def find_links(url, driver="request", booster=False):
    from urllib.parse import urlparse, urljoin

    links_href, cond_ex = [], ["javascript:", "mailto:", "tel:", "fax:"]
    content_type, soup = fetch_all(url, driver=driver)

    if soup and content_type == "text/html":
        base_url = urlparse(url)

        # Extract links from all tags with 'href' and 'src' attributes
        elements = soup.find_all(True, href=True) + soup.find_all(True, src=True)

        for element in elements:
            link_href = element.get("href") or element.get("src")
            if link_href:
                if link_href.startswith("//"):
                    link_href = "http:" + link_href
                elif not link_href.startswith(("http", "https")):
                    link_href = urljoin(base_url.geturl(), link_href)

                if all(exclusion not in link_href for exclusion in cond_ex):
                    links_href.append(link_href)

        unique_links = ips.unique(links_href)  # Remove duplicates

        if booster:
            for link in unique_links:
                if link != url:  # Avoid infinite recursion
                    sub_links = find_links(link, driver=driver, booster=False)
                    if sub_links:
                        links_href.extend(sub_links)
            links_href = ips.unique(links_href)  # Remove duplicates again

        return links_href

    elif url.split(".")[-1] in ["pdf"]:
        return [url]
    else:
        return None


# To determine which links are related to target domains(e.g., pages) you are interested in
def filter_links(links, contains="html", driver="requ", booster=False):
    from urllib.parse import urlparse, urljoin

    filtered_links = []
    if isinstance(contains, str):
        contains = [contains]
    if isinstance(links, str):
        links = find_links(links, driver=driver, booster=booster)
    for link in links:
        parsed_link = urlparse(link)
        condition = (
            all([i in link for i in contains]) and "javascript:" not in parsed_link
        )
        if condition:
            filtered_links.append(link)
    return ips.unique(filtered_links)


def find_domain(links):
    from urllib.parse import urlparse, urljoin
    from collections import Counter

    if not links:
        return None
    domains = [urlparse(link).netloc for link in links]
    domain_counts = Counter(domains)
    if domain_counts.most_common(1):
        most_common_domain_tuple = domain_counts.most_common(1)[0]
        if most_common_domain_tuple:
            most_common_domain = most_common_domain_tuple[0]
            return most_common_domain
        else:
            return None
    else:
        return None


def pdf_detector(url, contains=None, dir_save=None, booster=False):
    print("usage: pdf_detector(url, dir_save, booster=True")

    def fname_pdf_corr(fname):
        if fname[-4:] != ".pdf":
            fname = fname[:-4] + ".pdf"
        return fname

    if isinstance(contains, str):
        contains = [contains]
    if isinstance(url, str):
        if ".pdf" in url:
            pdf_links = url
        else:
            if booster:
                links_all = []
                if "http" in url and url:
                    [links_all.append(i) for i in find_links(url) if "http" in i]
                print(links_all)
            else:
                links_all = url
            if contains is not None:
                pdf_links = filter_links(links=links_all, contains=[".pdf"] + contains)
            else:
                pdf_links = filter_links(links=links_all, contains=[".pdf"])
    elif isinstance(url, list):
        links_all = url
        if contains is not None:
            pdf_links = filter_links(links=links_all, contains=["pdf"] + contains)
        else:
            pdf_links = filter_links(links=links_all, contains=["pdf"])
    else:
        links_all = find_links(url)
        if contains is not None:
            pdf_links = filter_links(links=links_all, contains=["pdf"] + contains)
        else:
            pdf_links = filter_links(links=links_all, contains=["pdf"])

    if pdf_links:
        from pprint import pp

        pp(f"pdf detected{pdf_links}")
    else:
        print("no pdf file")
    if dir_save:
        print("... is trying to download to local")
        fnames = [pdf_link_.split("/")[-1] for pdf_link_ in pdf_links]
        idx = 0
        for pdf_link in pdf_links:
            headers = {"User-Agent": user_agent()}
            response = requests.get(pdf_link, headers=headers)
            # Check if the request was successful (status code 200)
            if response.status_code == 200:
                # Save the PDF content to a file
                with open(dir_save + fname_pdf_corr(fnames[idx]), "wb") as pdf:
                    pdf.write(response.content)
                print("PDF downloaded successfully!")
            else:
                print("Failed to download PDF:", response.status_code)
            idx += 1
        print(f"{len(fnames)} files are downloaded:\n{fnames}\n to local: \n{dir_save}")

def downloader(
    url,
    dir_save=None,
    kind=[".pdf"],
    contains=None,
    rm_folder=False,
    booster=False,
    verbose=True,
    timeout=30,
    n_try=3,
    timestamp=False,
    chunk_size=8192,
    retry_delay=2,
):
    """
    Enhanced file downloader with robust error handling and resume capability
    
    Args:
        url: URL or list of URLs to download
        dir_save: Directory to save files (None for current directory)
        kind: List of file extensions to filter for (e.g., ['.pdf', '.xls'])
        contains: String that must be present in the filename
        rm_folder: Whether to remove the target folder before downloading
        booster: Whether to search for links on the page
        verbose: Whether to print progress information
        timeout: Connection timeout in seconds
        n_try: Number of retry attempts
        timestamp: Whether to add timestamp to filenames
        chunk_size: Download chunk size in bytes
        retry_delay: Delay between retries in seconds
    """
    import os
    import time
    import shutil
    import requests
    from requests.exceptions import (ChunkedEncodingError, ConnectionError, 
                                  RequestException, Timeout)
    from urllib.parse import urlparse
    from datetime import datetime

    if verbose and ips.run_once_within():
        print("usage: downloader(url, dir_save=None, kind=['.pdf','xls'], contains=None, booster=False)")
        
    # -------------------- wget integration helper --------------------
    def _wget_available():
        """Check if wget exists on system"""
        return shutil.which("wget") is not None

    def _wget_download(url, out_path):
        import subprocess
        """Download a file using system wget with progress bar"""
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        try:
            subprocess.run(
                ["wget", "-c", "--show-progress", "--progress=bar:force", "-O", out_path, url],
                check=True,
            )
            return True
        except Exception as e:
            if verbose:
                print(f"wget download failed: {e}")
            return False
    # -----------------------------------------------------------------

    def fname_corrector(fname, ext):
        """Ensure filename has correct extension"""
        if not ext.startswith("."):
            ext = "." + ext
        if not fname.endswith(ext):
            fname = os.path.splitext(fname)[0] + ext
        if not any(fname[:-len(ext)]):
            fname = datetime.now().strftime("%H%M%S") + ext
        return fname

    def check_and_modify_filename(directory, filename):
        """Handle duplicate filenames by adding counter"""
        base, ext = os.path.splitext(filename)
        counter = 1
        new_filename = filename
        while os.path.exists(os.path.join(directory, new_filename)):
            new_filename = f"{base}_{counter:02d}{ext}"
            counter += 1
        return new_filename

    def get_partial_file_size(filepath):
        """Get size of partially downloaded file"""
        try:
            return os.path.getsize(filepath)
        except OSError:
            return 0

    def download_with_resume(url, filepath, headers=None):
        """Download with resume capability"""
        headers = headers or {}
        initial_size = get_partial_file_size(filepath)
        
        if initial_size > 0:
            headers['Range'] = f'bytes={initial_size}-'
            mode = 'ab'
        else:
            mode = 'wb'

        try:
            with requests.get(url, headers=headers, stream=True, timeout=timeout) as r:
                r.raise_for_status()
                total_size = int(r.headers.get('content-length', 0)) + initial_size
                
                with open(filepath, mode) as f, tqdm(
                    total=total_size,
                    unit='B',
                    unit_scale=True,
                    unit_divisor=1024,
                    initial=initial_size,
                    desc=os.path.basename(filepath),
                    disable=not verbose,
                ) as progress:
                    for chunk in r.iter_content(chunk_size=chunk_size):
                        if chunk:  # filter out keep-alive chunks
                            f.write(chunk)
                            progress.update(len(chunk))
            return True
        except Exception as e:
            if verbose:
                print(f"Download error: {e}")
            return False

    dir_save = dir_save or "./"
    filename = os.path.basename(urlparse(url).path)
    save_path = os.path.join(dir_save, filename)
    os.makedirs(dir_save, exist_ok=True)
    # Handle FTP URLs
    if isinstance(url, str) and url.startswith("ftp"):
        import urllib.request
        
        try:
            urllib.request.urlretrieve(url, save_path)
            if verbose:
                print(f"Downloaded FTP file to: {save_path}")
            return save_path
        except Exception as e:
            print(f"FTP download failed: {e}")
            return None
    if kind is None and _wget_available():
        if verbose:
            print(f"Using wget for download: {url}")
        success = _wget_download(url, save_path)
        if success:
            if verbose:
                print(f"Successfully downloaded via wget: {save_path}")
            return save_path
        else:
            if verbose:
                print("⚠️ wget failed, falling back to requests...")
            kind = [".*"]  # dummy
    # Process directory and file links
    if not isinstance(kind, list):
        kind = [kind]
        
    if isinstance(url, list):
        results = []
        for url_ in url:
            results.append(downloader(
                url_,
                dir_save=dir_save,
                kind=kind,
                contains=contains,
                booster=booster,
                verbose=verbose,
                timeout=timeout,
                n_try=n_try,
                timestamp=timestamp,
            ))
        return results

    # Normalize file extensions
    kind = [k if k.startswith(".") else f".{k}" for k in kind]

    # Find and filter links
    file_links_all = []
    for kind_ in kind:
        if isinstance(url, str) and any(ext in url for ext in kind):
            file_links = [url]
        else:
            links_all = find_links(url) if booster else ([url] if isinstance(url, str) else url)
            file_links = filter_links(
                links_all, 
                contains=(contains + kind_) if contains else kind_
            )
        
        file_links = ips.unique(file_links)
        if verbose:
            if file_links:
                print("Files detected:")
                from pprint import pp
                pp(file_links)
            else:
                print("No files detected")
        
        if file_links:
            file_links_all.extend(file_links if isinstance(file_links, list) else [file_links])

    file_links_all = ips.unique(file_links_all)
    if not file_links_all:
        return None

    # Prepare download directory
    dir_save = dir_save or "./"
    if rm_folder:
        ips.rm_folder(dir_save)
    os.makedirs(dir_save, exist_ok=True)

    # Download files
    results = []
    for file_link in file_links_all:
        headers = {
            "User-Agent": user_agent(),
            "Accept-Encoding": "identity"  # Disable compression for resume support
        }
        
        # Determine filename
        filename = os.path.basename(urlparse(file_link).path)
        ext = next((ftype for ftype in kind if ftype in filename), kind[0])
        corrected_fname = fname_corrector(filename, ext)
        corrected_fname = check_and_modify_filename(dir_save, corrected_fname)
        
        if timestamp:
            corrected_fname = datetime.now().strftime("%y%m%d_%H%M%S_") + corrected_fname
        
        save_path = os.path.join(dir_save, corrected_fname)
        
        # Download with retry logic
        success = False
        for attempt in range(n_try):
            try:
                if verbose:
                    print(f"Downloading {file_link} (attempt {attempt + 1}/{n_try})")
                if _wget_available():
                    success = _wget_download(file_link, save_path)
                    if success:
                        if verbose:
                            print(f"Successfully downloaded via wget: {save_path}")
                        break
                if download_with_resume(file_link, save_path, headers):
                    success = True
                    if verbose:
                        print(f"Successfully downloaded: {save_path}")
                    break
                
            except (ChunkedEncodingError, ConnectionError, Timeout, RequestException) as e:
                if verbose:
                    print(f"Attempt {attempt + 1} failed: {e}")
                if attempt < n_try - 1:
                    time.sleep(retry_delay)
        
        if success:
            results.append(save_path)
        else:
            if verbose:
                print(f"Failed to download {file_link} after {n_try} attempts")
            # Clean up potentially corrupted file
            if os.path.exists(save_path):
                os.remove(save_path)
            results.append(None)

    return results if len(results) != 1 else results[0]

def find_img(url, driver="request", dir_save="images", rm_folder=False, verbose=True):
    """
    Save images referenced in HTML content locally.
    Args:
        content (str or BeautifulSoup): HTML content or BeautifulSoup object.
        url (str): URL of the webpage.
        content_type (str): Type of content. Default is "html".
        dir_save (str): Directory to save images. Default is "images".
    Returns:
        str: HTML content with updated image URLs pointing to local files.
    """
    from urllib.parse import urlparse, urljoin
    import base64

    if rm_folder:
        ips.rm_folder(dir_save)
    content_type, content = fetch_all(url, driver=driver)
    if content_type is None:
        content_type=""
    if "html" in content_type.lower():
        # Create the directory if it doesn't exist
        os.makedirs(dir_save, exist_ok=True)
        # Parse HTML content if it's not already a BeautifulSoup object
        if isinstance(content, str):
            content = BeautifulSoup(content, "html.parser")
        image_links = []
        # Extracting images
        images = content.find_all("img", src=True)
        if not images:
            content_type, content = fetch_all(url, driver="selenium")
            images = content.find_all("img", src=True)
        for i, image in enumerate(images):
            try:
                image_url = image["src"]
                if image_url.startswith("data:image"):
                    mime_type, base64_data = image_url.split(",", 1)
                    if ":" in mime_type:
                        # image_extension = mime_type.split(":")[1].split(";")[0]
                        image_extension = (
                            mime_type.split(":")[1].split(";")[0].split("/")[-1]
                        )
                    else:
                        image_extension = (
                            "png"  # Default to PNG if extension is not specified
                        )
                    image_data = base64.b64decode(base64_data)
                    image_filename = os.path.join(
                        dir_save, f"image_{i}.{image_extension}"
                    )
                    with open(image_filename, "wb") as image_file:
                        image_file.write(image_data)
                    image["src"] = image_filename
                    # if verbose:
                    #     plt.imshow(image_data)
                else:
                    # Construct the absolute image URL
                    absolute_image_url = urljoin(url, image_url)
                    # Parse the image URL to extract the file extension
                    parsed_url = urlparse(absolute_image_url)
                    image_extension = os.path.splitext(parsed_url.path)[1]
                    # Download the image
                    image_response = requests.get(
                        absolute_image_url, proxies=proxies_glob
                    )
                    # Save the image to a file
                    image_filename = os.path.join(
                        dir_save, f"image_{i}{image_extension}"
                    )
                    with open(image_filename, "wb") as image_file:
                        image_file.write(image_response.content)
                    # Update the src attribute of the image tag to point to the local file
                    image["src"] = image_filename
            except (requests.RequestException, KeyError) as e:
                print(f"Failed to process image {image_url}: {e}")
        print(f"images were saved at\n{dir_save}")
        if verbose:
            display_thumbnail_figure(flist(dir_save, kind="img"), dpi=100)
    return content


def svg_to_png(svg_file):
    import io
    from PIL import Image

    with WandImage(filename=svg_file, resolution=300) as img:
        img.format = "png"
        png_image = img.make_blob()
    return Image.open(io.BytesIO(png_image))


def display_thumbnail_figure(dir_img_list, figsize=(10, 10), dpi=100):
    import matplotlib.pyplot as plt
    from PIL import Image

    """
    Display a thumbnail figure of all images in the specified directory.
    Args:
        dir_img_list (list): List of the Directory containing the images.
    """
    num_images = len(dir_img_list)
    if num_images == 0:
        print("No images found to display.")
        return
    grid_size = int(num_images**0.5) + 1
    fig, axs = plt.subplots(grid_size, grid_size, figsize=figsize, dpi=dpi)
    for ax, image_file in zip(axs.flatten(), dir_img_list):
        try:
            img = Image.open(image_file)
            ax.imshow(img)
            ax.axis("off")  # Hide axes
        except:
            continue
    try:
        [ax.axis("off") for ax in axs.flatten()]
        plt.tight_layout()
        plt.show()
    except:
        pass


def content_div_class(content, div="div", div_class="highlight"):
    texts = [div.text for div in content.find_all(div, class_=div_class)]
    return texts


def fetch_selenium(
    url,
    where="div",
    what=None,
    extend=False,
    by=By.TAG_NAME,
    timeout=10,
    retry=2,
    login_url=None,
    username=None,
    password=None,
    username_field="username",
    password_field="password",
    submit_field="submit",
    username_by=By.NAME,
    password_by=By.NAME,
    submit_by=By.NAME,
    # capability='eager', # eager or none
    proxy=None,  # Add proxy parameter
    javascript=True,  # Add JavaScript option
    disable_images=False,  # Add option to disable images
    iframe_name=None,  # Add option to handle iframe
    **kwargs,
):
    import random
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.common.by import By
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from webdriver_manager.chrome import ChromeDriverManager
    from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument(f'--user-data-dir={os.path.expanduser("~/selenium_profile")}')
    chrome_options.add_argument(f"user-agent={user_agent()}")
    if proxy:
        chrome_options.add_argument(f"--proxy-server={proxy}")
    if disable_images:
        prefs = {"profile.managed_default_content_settings.images": 2}
        chrome_options.add_experimental_option("prefs", prefs)
    # chrome_options.page_load_strategy = capability
    service = Service(ChromeDriverManager().install())
    for attempt in range(retry):
        try:
            driver = webdriver.Chrome(service=service, options=chrome_options)

            if not javascript:
                driver.execute_cdp_cmd(
                    "Emulation.setScriptExecutionDisabled", {"value": True}
                )

            if login_url:
                driver.get(login_url)
                WebDriverWait(driver, timeout).until(
                    EC.presence_of_element_located((username_by, username_field))
                ).send_keys(username)
                WebDriverWait(driver, timeout).until(
                    EC.presence_of_element_located((password_by, password_field))
                ).send_keys(password)
                WebDriverWait(driver, timeout).until(
                    EC.element_to_be_clickable((submit_by, submit_field))
                ).click()

            driver.get(url)

            if iframe_name:
                iframe = WebDriverWait(driver, timeout).until(
                    EC.presence_of_element_located((By.NAME, iframe_name))
                )
                driver.switch_to.frame(iframe)

            WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located((by, where))
            )
            page_source = driver.page_source
            driver.quit()

            content = BeautifulSoup(page_source, "html.parser")
            texts = extract_text_from_content(
                content, where=where, what=what, extend=extend, **kwargs
            )
            return texts
        except Exception as e:
            # logger.error(f"Attempt {attempt + 1} failed with error ")
            if driver:
                driver.quit()
            if attempt == retry - 1:
                logger.error("Failed to fetch the content after all retries")
                return []
        time.sleep(random.uniform(1, 3))
    # Return empty list if nothing found after all retries
    return []


def fetch(
    url,
    where="div",
    driver="request",
    what=None,
    extend=True,
    booster=False,
    retry=2,
    verbose=False,
    output="text",
    **kws,
):
    import random
    from urllib.parse import urlparse, urljoin

    if "xt" in output.lower():
        for attempt in range(retry):
            if verbose and attempt == 0:
                xample = 'fetch(url,where="div",what=None,extend=True,by=By.TAG_NAME,timeout=10,retry=3,login_url=None,username=None,password=None,username_field="username",password_field="password",submit_field="submit",username_by=By.NAME,password_by=By.NAME,submit_by=By.NAME)'
                print(xample)
            if isinstance(url, str):
                content_type, content = fetch_all(
                    url, parser="html.parser", driver=driver
                )
            else:
                content_type, content = "text/html", url
            texts = extract_text_from_content(
                content,
                content_type=content_type,
                where=where,
                what=what,
                extend=extend,
                **kws,
            )
            if isinstance(texts, pd.core.frame.DataFrame):
                if not texts.empty:
                    break
            else:
                if texts:
                    break
                time.sleep(random.uniform(0.5, 1.5))
        if isinstance(texts, pd.core.frame.DataFrame):
            condition_ = [texts.empty, booster]
        else:
            condition_ = [not texts, booster]
        if any(condition_): 
            print("trying to use 'fetcher2'...")
            texts = fetch_selenium(
                url=url, where=where, what=what, extend=extend, **kws
            )
        if texts:
            return texts
        else:
            print("got nothing")
            return fetch(
                url,
                where=where,
                driver=driver,
                what=what,
                extend=extend,
                booster=booster,
                retry=retry,
                verbose=verbose,
                output="soup",
                **kws,
            )
    elif "url" in output.lower():
        base_url = urlparse(url)
        if verbose:
            print("urljoin(urlparse(url), link_part)")
        return base_url.geturl()
    else:
        try:
            content_type, content = fetch_all(url, parser="html.parser", driver=driver)
            search_kwargs = {**kws}
            if "class_" in search_kwargs:
                search_kwargs["class"] = search_kwargs["class_"]
                del search_kwargs["class_"]
            if what:
                search_kwargs["class"] = what
            if "attrs" in kws:
                result_set = content.find_all(where, **search_kwargs)
            else:
                result_set = content.find_all(where, attrs=dict(**search_kwargs))
            return result_set
        except:
            print("got nothing")
            return None


def extract_from_content(content, where="div", what=None):
    if what is None:
        result_set = content.find_all(where, recursive=True)
        texts_ = " ".join(tag.get_text() + "\n" for tag in result_set)
        texts = [tx for tx in texts_.split("\n") if tx]
    else:
        texts_ = " ".join(
            div.get_text() + "\n"
            for div in content.find_all(where, class_=what, recursive=True)
        )
        texts = [tx for tx in texts_.split("\n") if tx]
    return texts


def find_forms(url, driver="requ"):
    content_type, content = fetch_all(url, driver=driver)
    df = pd.DataFrame()
    # Extracting forms and inputs
    forms = content.find_all("form", recursive=True)
    form_data = []
    for form in forms:
        if form:
            form_inputs = form.find_all("input", recursive=True)
            input_data = {}
            for input_tag in form_inputs:
                input_type = input_tag.get("type")
                input_name = input_tag.get("name")
                input_value = input_tag.get("value")
                input_data[input_name] = {"type": input_type, "value": input_value}
            form_data.append(input_data)
    return form_data


#  to clean strings
def clean_string(value):
    if isinstance(value, str):
        return value.replace("\n", "").replace("\r", "").replace("\t", "")
    else:
        return value


def find_all(url, dir_save=None, driver="req"):
    content_type, content = fetch_all(url, driver=driver)
    paragraphs_text = extract_from_content(content, where="p")
    # Extracting specific elements by class
    specific_elements_text = [
        element.text
        for element in content.find_all(class_="specific-class", recursive=True)
        if element
    ]
    # Extracting links (anchor tags)
    links_href = find_links(url)
    links_href = filter_links(links_href)

    # Extracting images
    images_src = [
        image["src"]
        for image in content.find_all("img", src=True, recursive=True)
        if image
    ]

    # Extracting headings (h1, h2, h3, etc.)
    headings = [f"h{i}" for i in range(1, 7)]
    headings_text = {
        heading: [tag.text for tag in content.find_all(heading, recursive=True)]
        for heading in headings
        if heading
    }

    # Extracting lists (ul, ol, li)
    list_items_text = [
        item.text
        for list_ in content.find_all(["ul", "ol"], recursive=True)
        for item in list_.find_all("li", recursive=True)
        if item
    ]

    # Extracting tables (table, tr, td)
    table_cells_text = [
        cell.text
        for table in content.find_all("table", recursive=True)
        for row in table.find_all("tr")
        for cell in row.find_all("td")
        if cell
    ]

    # Extracting other elements
    divs_content = extract_from_content(content, where="div")
    headers_footer_content = [
        tag.text
        for tag in content.find_all(["header", "footer"], recursive=True)
        if tag
    ]
    meta_tags_content = [
        (tag.name, tag.attrs) for tag in content.find_all("meta", recursive=True) if tag
    ]
    spans_content = extract_from_content(content, where="span")
    bold_text_content = extract_from_content(content, where="b")
    italic_text_content = extract_from_content(content, where="i")
    code_snippets_content = extract_from_content(content, where="code")
    blockquotes_content = extract_from_content(content, where="blockquote")
    preformatted_text_content = extract_from_content(content, where="pre")
    buttons_content = extract_from_content(content, where="button")
    navs_content = extract_from_content(content, where="nav")
    sections_content = extract_from_content(content, where="section")
    articles_content = extract_from_content(content, where="article")
    figures_content = extract_from_content(content, where="figure")
    captions_content = extract_from_content(content, where="figcap")
    abbreviations_content = extract_from_content(content, where="abbr")
    definitions_content = extract_from_content(content, where="dfn")
    addresses_content = extract_from_content(content, where="address")
    time_elements_content = extract_from_content(content, where="time")
    progress_content = extract_from_content(content, where="process")
    forms = find_forms(url)

    lists_to_fill = [
        paragraphs_text,
        specific_elements_text,
        links_href,
        images_src,
        headings_text["h1"],
        headings_text["h2"],
        headings_text["h3"],
        headings_text["h4"],
        headings_text["h5"],
        headings_text["h6"],
        list_items_text,
        table_cells_text,
        divs_content,
        headers_footer_content,
        meta_tags_content,
        spans_content,
        bold_text_content,
        italic_text_content,
        code_snippets_content,
        blockquotes_content,
        preformatted_text_content,
        buttons_content,
        navs_content,
        sections_content,
        articles_content,
        figures_content,
        captions_content,
        abbreviations_content,
        definitions_content,
        addresses_content,
        time_elements_content,
        progress_content,
        forms,
    ]
    # add new features
    script_texts = content_div_class(content, div="div", div_class="highlight")
    lists_to_fill.append(script_texts)

    audio_src = [
        audio["src"] for audio in content.find_all("audio", src=True, recursive=True)
    ]
    video_src = [
        video["src"] for video in content.find_all("video", src=True, recursive=True)
    ]
    iframe_src = [
        iframe["src"] for iframe in content.find_all("iframe", src=True, recursive=True)
    ]
    lists_to_fill.extend([audio_src, video_src, iframe_src])

    rss_links = [
        link["href"]
        for link in content.find_all(
            "link", type=["application/rss+xml", "application/atom+xml"], recursive=True
        )
    ]
    lists_to_fill.append(rss_links)

    # Find the maximum length among all lists
    max_length = max(len(lst) for lst in lists_to_fill)

    # Fill missing data with empty strings for each list
    for lst in lists_to_fill:
        lst += [""] * (max_length - len(lst))

    # Create DataFrame
    df = pd.DataFrame(
        {
            "h1": headings_text["h1"],
            "h2": headings_text["h2"],
            "h3": headings_text["h3"],
            "h4": headings_text["h4"],
            "h5": headings_text["h5"],
            "h6": headings_text["h6"],
            "paragraphs": paragraphs_text,
            "divs": divs_content,
            "items": list_items_text,
            "tables": table_cells_text,
            "headers": headers_footer_content,
            "tags": meta_tags_content,
            "spans": spans_content,
            "bold_text": bold_text_content,
            "italic_text": italic_text_content,
            "codes": code_snippets_content,
            "blocks": blockquotes_content,
            "preformatted_text": preformatted_text_content,
            "buttons": buttons_content,
            "navs": navs_content,
            "sections": sections_content,
            "articles": articles_content,
            "figures": figures_content,
            "captions": captions_content,
            "abbreviations": abbreviations_content,
            "definitions": definitions_content,
            "addresses": addresses_content,
            "time_elements": time_elements_content,
            "progress": progress_content,
            "specific_elements": specific_elements_text,
            "forms": forms,
            "scripts": script_texts,
            "audio": audio_src,
            "video": video_src,
            "iframe": iframe_src,
            "rss": rss_links,
            "images": images_src,
            "links": links_href,
        }
    )
    # to remove the '\n\t\r'
    df = df.apply(
        lambda x: x.map(clean_string) if x.dtype == "object" else x
    )  # df=df.applymap(clean_string)
    if dir_save:
        if not dir_save.endswith(".csv"):
            dir_save = dir_save + "_df.csv"
            df.to_csv(dir_save)
        else:
            df.to_csv(dir_save)
        print(f"file has been saved at\n{dir_save}")
    return df


def flist(fpath, kind="all"):
    all_files = [
        os.path.join(fpath, f)
        for f in os.listdir(fpath)
        if os.path.isfile(os.path.join(fpath, f))
    ]
    if kind == "all" or "all" in kind:
        return all_files
    if isinstance(kind, str):
        kind = [kind]
    filt_files = []
    for f in all_files:
        for kind_ in kind:
            if isa(f, kind_):
                filt_files.append(f)
                break
    return filt_files


def isa(fpath, kind="img"):
    """
    kinds file paths based on the specified kind.
    Args:
        fpath (str): Path to the file.
        kind (str): kind of file to kind. Default is 'img' for images. Other options include 'doc' for documents,
                    'zip' for ZIP archives, and 'other' for other types of files.
    Returns:
        bool: True if the file matches the kind, False otherwise.
    """
    if "img" in kind.lower():
        return is_image(fpath)
    elif "doc" in kind.lower():
        return is_document(fpath)
    elif "zip" in kind.lower():
        return is_zip(fpath)
    else:
        return False


def is_image(fpath):
    import mimetypes

    mime_type, _ = mimetypes.guess_type(fpath)
    if mime_type and mime_type.startswith("image"):
        return True
    else:
        return False


def is_document(fpath):
    import mimetypes

    mime_type, _ = mimetypes.guess_type(fpath)
    if mime_type and (
        mime_type.startswith("text/")
        or mime_type == "application/pdf"
        or mime_type == "application/msword"
        or mime_type
        == "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        or mime_type == "application/vnd.ms-excel"
        or mime_type
        == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        or mime_type == "application/vnd.ms-powerpoint"
        or mime_type
        == "application/vnd.openxmlformats-officedocument.presentationml.presentation"
    ):
        return True
    else:
        return False


def is_zip(fpath):
    import mimetypes

    mime_type, _ = mimetypes.guess_type(fpath)
    if mime_type == "application/zip":
        return True
    else:
        return False


def search(
    query,
    limit=5,
    kind="text",
    output="df",
    verbose=False,
    download=False,
    dir_save=dir_save,
    **kwargs,
):

    if "te" in kind.lower():
        from duckduckgo_search import DDGS

        results = DDGS().text(query, max_results=limit)
        res = pd.DataFrame(results)
        res.rename(columns={"href": "links"}, inplace=True)
    if verbose:
        print(f'searching "{query}": got the results below\n{res}')
    if download:
        try:
            downloader(
                url=res.links.tolist(), dir_save=dir_save, verbose=verbose, **kwargs
            )
        except:
            if verbose:
                print(f"failed link")
    return res


def echo(query, model="gpt", verbose=True, log=True, dir_save=dir_save):
    from duckduckgo_search import DDGS

    def is_in_any(str_candi_short, str_full, ignore_case=True):
        if isinstance(str_candi_short, str):
            str_candi_short = [str_candi_short]
        res_bool = []
        if ignore_case:
            [res_bool.append(i in str_full.lower()) for i in str_candi_short]
        else:
            [res_bool.append(i in str_full) for i in str_candi_short]
        return any(res_bool)

    def valid_mod_name(str_fly):
        if is_in_any(str_fly, "claude-3-haiku"):
            return "claude-3-haiku"
        elif is_in_any(str_fly, "gpt-3.5"):
            return "gpt-3.5"
        elif is_in_any(str_fly, "llama-3-70b"):
            return "llama-3-70b"
        elif is_in_any(str_fly, "mixtral-8x7b"):
            return "mixtral-8x7b"
        else:
            print(
                f"not support your model{model}, supported models: 'claude','gpt(default)', 'llama','mixtral'"
            )
            return "gpt-3.5"  # default model

    model_valid = valid_mod_name(model)
    res = DDGS().chat(query, model=model_valid)
    if verbose:
        from pprint import pp

        pp(res)
    if log:
        from datetime import datetime

        dt_str = datetime.fromtimestamp(time.time()).strftime("%Y-%m-%d_%H:%M:%S")
        res_ = f"###{dt_str}\n\n>{res}\n"
        os.makedirs(dir_save, exist_ok=True)
        fpath = os.path.join(dir_save, f"log_ai.md")
        ips.fupdate(fpath=fpath, content=res_)
        print(f"log file:{fpath}")
    return res


def chat(*args, **kwargs):
    if len(args) == 1 and isinstance(args[0], str):
        kwargs["query"] = args[0]
    return echo(**kwargs)


def ai(*args, **kwargs):
    if len(args) == 1 and isinstance(args[0], str):
        kwargs["query"] = args[0]
    return echo(**kwargs)


#! get_ip()
def get_ip(ip=None):
    """
    Usage:
        from py2ls import netfinder as nt
        ip = nt.get_ip()
    """

    import requests
    import time
    import logging
    from datetime import datetime, timedelta

    # Set up logging configuration
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler("public_ip_log.log"),  # Log to a file
        ],
    )

    cache = {}

    # Function to fetch IP addresses synchronously
    def fetch_ip(url, retries, timeout, headers):
        """
        Synchronous function to fetch the IP address with retries.
        """
        for attempt in range(retries):
            try:
                response = requests.get(url, timeout=timeout, headers=headers)
                response.raise_for_status()
                return response.json()
            except requests.RequestException as e:
                logging.error(f"Attempt {attempt + 1} failed: {e}")
                if attempt < retries - 1:
                    time.sleep(2**attempt)  # Exponential backoff
                else:
                    logging.error("Max retries reached.")
                    return {"error": f"Error fetching IP: {e}"}
            except requests.Timeout:
                logging.error("Request timed out")
                time.sleep(2**attempt)
        return {"error": "Failed to fetch IP after retries"}

    # Function to fetch geolocation synchronously
    def fetch_geolocation(url, retries, timeout, headers):
        """
        Synchronous function to fetch geolocation data by IP address.
        """
        for attempt in range(retries):
            try:
                response = requests.get(url, timeout=timeout, headers=headers)
                response.raise_for_status()
                return response.json()
            except requests.RequestException as e:
                logging.error(f"Geolocation request attempt {attempt + 1} failed: {e}")
                if attempt < retries - 1:
                    time.sleep(2**attempt)  # Exponential backoff
                else:
                    logging.error("Max retries reached.")
                    return {"error": f"Error fetching geolocation: {e}"}
            except requests.Timeout:
                logging.error("Geolocation request timed out")
                time.sleep(2**attempt)
        return {"error": "Failed to fetch geolocation after retries"}

    # Main function to get public IP and geolocation
    def get_public_ip(
        ip4=True,
        ip6=True,
        verbose=True,
        retries=3,
        timeout=5,
        geolocation=True,
        headers=None,
        cache_duration=5,
    ):
        """
        Synchronously fetches public IPv4 and IPv6 addresses, along with optional geolocation info.
        """
        # Use the cache if it's still valid
        cache_key_ip4 = "public_ip4"
        cache_key_ip6 = "public_ip6"
        cache_key_geolocation = "geolocation"

        if (
            cache
            and cache_key_ip4 in cache
            and datetime.now() < cache[cache_key_ip4]["expires"]
        ):
            logging.info("Cache hit for IPv4, using cached data.")
            ip4_data = cache[cache_key_ip4]["data"]
        else:
            ip4_data = None

        if (
            cache
            and cache_key_ip6 in cache
            and datetime.now() < cache[cache_key_ip6]["expires"]
        ):
            logging.info("Cache hit for IPv6, using cached data.")
            ip6_data = cache[cache_key_ip6]["data"]
        else:
            ip6_data = None

        if (
            cache
            and cache_key_geolocation in cache
            and datetime.now() < cache[cache_key_geolocation]["expires"]
        ):
            logging.info("Cache hit for Geolocation, using cached data.")
            geolocation_data = cache[cache_key_geolocation]["data"]
        else:
            geolocation_data = None

        # Fetch IPv4 if requested
        if ip4 and not ip4_data:
            logging.info("Fetching IPv4...")
            ip4_data = fetch_ip(
                "https://api.ipify.org?format=json", retries, timeout, headers
            )
            cache[cache_key_ip4] = {
                "data": ip4_data,
                "expires": datetime.now() + timedelta(minutes=cache_duration),
            }

        # Fetch IPv6 if requested
        if ip6 and not ip6_data:
            logging.info("Fetching IPv6...")
            ip6_data = fetch_ip(
                "https://api6.ipify.org?format=json", retries, timeout, headers
            )
            cache[cache_key_ip6] = {
                "data": ip6_data,
                "expires": datetime.now() + timedelta(minutes=cache_duration),
            }

        # Fetch geolocation if requested
        if geolocation and not geolocation_data:
            logging.info("Fetching Geolocation...")
            geolocation_data = fetch_geolocation(
                "https://ipinfo.io/json", retries, timeout, headers
            )
            cache[cache_key_geolocation] = {
                "data": geolocation_data,
                "expires": datetime.now() + timedelta(minutes=cache_duration),
            }

        # Prepare the results
        ip_info = {
            "ip4": ip4_data.get("ip") if ip4_data else "N/A",
            "ip6": ip6_data.get("ip") if ip6_data else "N/A",
            "geolocation": geolocation_data if geolocation_data else "N/A",
        }

        # Verbose output if requested
        if verbose:
            print(f"Public IPv4: {ip_info['ip4']}")
            print(f"Public IPv6: {ip_info['ip6']}")
            print(f"Geolocation: {ip_info['geolocation']}")

        return ip_info

    # Function to get geolocation data by IP
    def get_geolocation_by_ip(ip, retries=3, timeout=5, headers=None):
        """
        Fetches geolocation data for a given IP address.
        """
        url = f"https://ipinfo.io/{ip}/json"
        geolocation_data = fetch_geolocation(url, retries, timeout, headers)
        return geolocation_data
    #! here starting get_ip()
    headers = {"User-Agent": user_agent()}
    if ip is None:
        try:
            ip_data = get_public_ip(headers=headers, verbose=True)
        except Exception as e:
            print(e)
            ip_data = None
        return ip_data
    else:
        geolocation_data = get_geolocation_by_ip(ip, headers=headers)
        return geolocation_data
