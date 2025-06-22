from warnings import warn
from random import uniform
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from pushbullet import PushBullet

class Website:
    def __init__(self, url: str, type: str):
        self.url = url
        self.type = type

websites = []
type_stockelement_pairs = {}
stock_texts = ['' for _ in range(len(websites))]
interval_between_scrapes = 60000 # 60 seconds
scrape_interval_min_noise, scrape_interval_max_noise = 0.5, 2.0 # multiplier for scraping interval
interval_between_gets = 500 # 0.5 seconds
randomize_get_order = True # avoids anti-bot filter
get_interval_min_noise, get_interval_max_noise = 0.5, 2.0 # multiplier for request interval 

options = webdriver.ChromeOptions()
options.add_argument('--no-sandbox')
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_experimental_option("excludeSwitches", ['enable-automation'])
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36")
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--disable-gpu')

service = Service('/usr/bin/chromedriver')

driver = webdriver.Chrome(service=service, options=options)

thread_running = True

def print_syntax_warning(url):
    warn('Warning, %s is not a valid URL. Please check to ensure proper syntax.' % url)

def print_html_warning(url, status_code):
    warn('Warning, %s returned status code %d. Please check to ensure website is operating correctly.' % (url, status_code))

def is_valid_website(website):
    return True

def get_sleep_interval(interval, min_noise, max_noise):
    noise = uniform(min_noise, max_noise) 
    return interval * noise

def get_request_interval():
    return get_sleep_interval(interval_between_gets, get_interval_min_noise, get_interval_max_noise)

def get_scrape_interval():
    return get_sleep_interval(interval_between_scrapes, scrape_interval_min_noise, scrape_interval_max_noise)

def get_stock_text(website: Website):
    driver.get(website.url)
    try: 
        elem = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, type_stockelement_pairs[website.type])))
        return elem.text
    except: 
        print('Could not get stock status from %s. Possible CAPTCHA detected. Please resolve manually using VNC' % website.url)
    return ''
    

def alert_stock_change(website: Website, stock_text: str, pb: PushBullet):
    msg = 'ALERT ALERT ALERT There is a stock change on %s. New status is %s' % (website.url, stock_text)
    print(msg)
    pb.push_note('Labotbu', msg)

def scrape_websites(pushbullet: PushBullet):
    for i in range(len(websites)):
        website = websites[i]
        print('Scraping %s...' % website.url)
        if not(is_valid_website(website)):
            print_syntax_warning(website)
            continue
        if i > 0:
            sleep(get_request_interval() / 1000)
        stock_text = get_stock_text(website)
        if stock_texts[i] != stock_text:
            alert_stock_change(website, stock_text, pushbullet)
            stock_texts[i] = stock_text
        

def scrape_loop():
    global thread_running
    sleep(10)
    pushbullet_token = input('Please enter your Pushbullet Access Token:')
    pb = PushBullet(pushbullet_token)
    while thread_running:
        print('Scraping websites...')
        scrape_websites(pb)
        print('Scraping done. Looping...')
        sleep(get_scrape_interval() / 1000)
        
def wait_for_input():
    user_input = input('Press anything to cancel...')

def main():
    scrape_loop()




if __name__ == "__main__":
    main()
