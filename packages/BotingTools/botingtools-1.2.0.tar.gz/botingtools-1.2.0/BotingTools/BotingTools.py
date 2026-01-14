import time
import os
from os import walk
import re
from selenium import webdriver
from msedge.selenium_tools import EdgeOptions
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support import expected_conditions
import subprocess
from random_username.generate import generate_username
from hcaptcha_solver import hcaptcha_solver
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from gpt4all import GPT4All
import socket
import random
from selenium.common.exceptions import NoSuchElementException, TimeoutException, InvalidSessionIdException, WebDriverException
import requests
import json
#from seleniumbase import Driver
import urllib
import shutil
import urllib.request
from bs4 import BeautifulSoup
from urllib.request import urlopen
from selenium_recaptcha_solver import RecaptchaSolver
from fake_useragent import UserAgent
import undetected_chromedriver as uc
import stackapi
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from selenium.webdriver.chrome.service import Service
from stackapi import StackAPI
from moviepy import VideoFileClip, AudioFileClip, ImageClip, CompositeVideoClip, video, concatenate_videoclips, clips_array, TextClip
from moviepy.video.fx.Loop import Loop

class BotTools:
    #------------#
    #   Others   #
    #------------#

    def __init__(self, BotTools):
        self.BotTools = BotTools

    def ai_chat(prompt):
        model = GPT4All("Meta-Llama-3-8B-Instruct.Q4_0.gguf") # downloads / loads a 4.66GB LLM
        with model.chat_session():
            text = model.generate(prompt, max_tokens=1024)
        
        return text

    def delete_string(file, words):
        f = open(file, "r")
        lst = []
        for line in f:
            for word in words:
                if word in line:
                    line = line.replace(word,'')
            lst.append(line)
        f.close()
        f = open(file, "w")
        for line in lst:
            f.write(line)
        f.close()

    def delete_line(temp_file):
        file = open(temp_file, "r")
        lines = file.readlines()
        new_lines = []
        for line in lines:
            if "DNS" not in line.strip():
                new_lines.append(line)
        file = open(temp_file, "w")
        file.writelines(new_lines)
        file.close()

    def get_email(driver):
        
        email = ""
        
        while email == "":
            try: #Consent Button
                WebDriverWait(driver, 3).until(expected_conditions.presence_of_element_located((By.XPATH, "/html/body/div[7]/div[2]/div[2]/div[2]/div[2]/button[1]"))).click()
            except:
                pass
                
            try: #Change Email Button
                WebDriverWait(driver, 3).until(expected_conditions.presence_of_element_located((By.XPATH, "/html/body/div[2]/div/div[2]/table/tbody/tr[2]/td[1]/a/button"))).click()
            except:
                pass

            time.sleep(0.5)
            
            try: #Get email Text
                email = WebDriverWait(driver, 3).until(expected_conditions.presence_of_element_located((By.ID, "email_ch_text"))).text
            except:
                pass
            
        driver.quit()
       
        print("\nEmail: " + email)
        return email
        
    #-----------#
    #   Proxy   #
    #-----------#
        
    def verify_tor_proxy(blocked_countries):
        #Check Ip
        http_proxy  = "socks5://127.0.0.1:9050"
        https_proxy = "socks5://127.0.0.1:9050"
        proxies = { 
                      "http"  : http_proxy, 
                      "https" : https_proxy, 
                    }
        ip_address = requests.get("http://wtfismyip.com/text", proxies=proxies).text
        ip_address = ip_address.rstrip()
        #print(ip_address)
        
        # create the url for the API, using f-string
        token = "3f4d82419bf119"
        url = f"https://www.ipinfo.io/{ip_address}?token={token}"

        # call the API and save the response
        with urlopen(url) as response:
            response_content = response.read()

        # parsing the response 
        data = json.loads(response_content)
        country = data['country']
        print(country)

        if country in blocked_countries:
            return True
        else:
            return False

    def create_tor_proxy(tor_path, torrc_path):
        #Delete Service
        os.system("sc delete tor")
        
        #Create Service
        arg = "" + tor_path + " --service install -options -f " + torrc_path
        os.system(arg)

    def renew_tor_proxy(tor_path, torrc_path):
        #Make Sure Service is Stopped
        os.system("sc stop tor")

        # Start Tor manually if not already running
        tor_process = subprocess.Popen(
            [tor_path, "-f", torrc_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        # Wait for Tor SOCKS port (9050) to open
        start = time.time()
        while time.time() - start < 30:
            try:
                s = socket.create_connection(("127.0.0.1", 9050), timeout=2)
                s.close()
                break
            except OSError:
                time.sleep(1)
        else:
            raise RuntimeError("Tor did not start in time")
        
        os.system("sc qc tor")
        
        # Send NEWNYM to the control port (9051)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect(("127.0.0.1", 9051))
            s.sendall(b'AUTHENTICATE "yourpassword"\r\n')
            s.sendall(b'SIGNAL NEWNYM\r\n')

    def start_tor_proxy(blocked_countries, tor_path, torrc_path):
        BotTools.renew_tor_proxy(tor_path, torrc_path)
        
        #Start Proxy With IP From Allowed Country
        i = 0
        while i == 0:
            if BotTools.verify_tor_proxy(blocked_countries):
                BotTools.renew_tor_proxy(tor_path, torrc_path)
            else:
                i = 1

    def inplace_change(temp_file, filename, old_string, new_string, temp_file_name):
        # Safely read the input filename using 'with'
        with open(filename) as f:
            s = f.read()

        # Safely write the changed content, if found in the file
        os.remove(temp_file)
        file = open(temp_file, "w")
        s = s.replace(old_string, new_string)
        file.truncate(0)
        file.write(s)

    def connect_vpn(websites, index_file, vpn_folder, temp_file, temp_file_name):    
        try: #Make Sure to quit Wireguard:
            command = '"C:\\Program Files\\WireGuard\\wireguard.exe" /uninstalltunnelservice %s' % (temp_file_name)
            proc = subprocess.Popen(command)
            subprocess.call("TASKKILL /f  /IM  wireguard.exe")
            time.sleep(5)
            #subprocess.run(["ipconfig", "/flushdns"], capture_output=True)
            #time.sleep(5)
        except:
            pass
        
        #Get Website IP
        ip = ""
        o = 0
        for website in websites:
            o += 1
            ip += socket.gethostbyname(website)
            ip += "/24, "
            l = socket.gethostbyname(website).split(".")
            l[2] = int(l[2]) + 1
            temp = ""
            for i in range(len(l)):
                temp += str(l[i])
                if i < len(l) - 1:
                    temp += "."
            ip += temp
            ip += "/24, "
            l = socket.gethostbyname(website).split(".")
            l[2] = int(l[2]) - 1
            temp = ""
            for i in range(len(l)):
                temp += str(l[i])
                if i < len(l) - 1:
                    temp += "."
            ip += temp
            ip += "/24, "
        #remove Last ","
        a = [i for i, letter in enumerate(ip) if letter == ","]
        index = a[len(a)-1]
        ip = ip[:index] + ip[index+1:]
        
        #Get Index
        file = open(index_file, 'r')
        t = file.read() #read leaves file handle at the end of file
        if t == "":
            i = 0
        else:
            i = int(t)
        
        #Create List With OpenVPN Config Files
        f = []
        for (dirpath, dirnames, filenames) in walk(vpn_folder):
            f.extend(filenames)
            break
        if i >= len(f):
            i = 0
        
        #Get Config File Name
        config = f[int(i)]
        
        #Change Config File with Website Ip:
        file = "%s\\%s" % (vpn_folder, config)
        BotTools.inplace_change(temp_file, file, "0.0.0.0/0", ip, temp_file_name)
        BotTools.delete_string(temp_file, [", ::/0"])
        
        #Update Index File
        i += 1
        file = open(index_file, 'w')
        file.write(str(i))
        
        file = open(temp_file, 'r')
        #print(file.read())
        
        #Start Wireguard
        command = '"c:\\Program Files\\WireGuard\\wireguard.exe" /installtunnelservice "%s"' % (temp_file)
        proc = subprocess.Popen(command) 
  
    def get_recapcha_ips(timeout=10):

        url = "https://www.netify.ai/resources/applications/google-recaptcha"

        try:
            response = requests.get(url, timeout=timeout)
            response.raise_for_status()

            return re.findall(
                r'\b(?:\d{1,3}\.){3}\d{1,3}\b',
                response.text
            )

        except requests.exceptions.Timeout:
            print("[WARN] netify.ai timed out — skipping reCAPTCHA IP fetch")
            return []

        except requests.exceptions.RequestException as e:
            print(f"[WARN] netify.ai request failed — {e}")
            return []
  
    def get_recapcha_ips_1():
        #Used to get recapcha ip addresses for ip rotation      
        
        url = "https://www.netify.ai/resources/applications/google-recaptcha"
        
        response = requests.get(url)
        ip_addresses = re.findall(r'\b(?:\d{1,3}\.){3}\d{1,3}\b', response.text)
        
        return ip_addresses
        
    def proxy():
        ips = []
        urls = [
            "https://free-proxy-list.net/",
            "https://proxyscrape.com/free-proxy-list",
            "https://advanced.name/freeproxy",
            "https://www.spys.one/en/free-proxy-list/",
            "https://hide.mn/en/proxy-list/",
            "https://geonode.com/free-proxy-list"
        ]
        
        pattern = re.compile(r'\b(?:25[0-5]|2[0-4]\d|1\d{2}|[1-9]?\d)'
                         r'(?:\.(?:25[0-5]|2[0-4]\d|1\d{2}|[1-9]?\d)){3}'
                         r'(?::\d{1,5})?\b')
        
        for url in urls:
            proxyList = requests.get(url)
            soup = BeautifulSoup(proxyList.text,'lxml')
            
            ips += pattern.findall(soup.get_text()) 
        
        end = 0
        while end == 0:
            proxy = random.choice(ips)
            try:
                proxies = {"http": f"http://{proxy}", "https": f"http://{proxy}"}
                response = requests.get("https://www.google.com/", proxies=proxies, timeout=2)
                end = 1
            except requests.exceptions.ProxyError:
                print(f"❌ Proxy error: {proxy}")
            except requests.exceptions.ConnectTimeout:
                print(f"❌ Timeout: {proxy}")
            except requests.exceptions.ConnectionError:
                print(f"❌ Connection failed: {proxy}")
            except Exception as e:
                print(f"❌ Other error ({proxy}): {e}")
                
        return proxy

    #-------------#
    #   Account   #
    #-------------#
    
    def human_click(driver, target_x, target_y, move_time=0.8):
        """
        Full human-like click:
        - Moves mouse in a natural curved path
        - Overshoots slightly and corrects (real humans do this)
        - Pauses before clicking
        - Clicks with natural timing
        """

        # ---- Step 1: Move near the target (overshoot) ----
        overshoot_x = target_x + random.randint(3, 12)
        overshoot_y = target_y + random.randint(3, 12)

        BotTools.human_move_mouse(driver, overshoot_x, overshoot_y, move_time)

        time.sleep(random.uniform(0.05, 0.12))

        # ---- Step 2: Correct small distance to exact position ----
        human_move_mouse(driver,
                         target_x + random.randint(-1, 1),
                         target_y + random.randint(-1, 1),
                         move_time=random.uniform(0.15, 0.30))

        # ---- Step 3: Hover slightly before click ----
        time.sleep(random.uniform(0.05, 0.20))

        # ---- Step 4: Realistic click timing ----
        actions = ActionChains(driver)
        actions.click().perform()

        # Release time like a human
        time.sleep(random.uniform(0.03, 0.08))
    
    def human_move_mouse(driver, target_x, target_y, move_time=1.0):
        """
        Smooth human-like mouse movement to absolute screen coordinates.
        """

        body = driver.find_element(By.TAG_NAME, "body")
        actions = ActionChains(driver)

        # Always start from (0,0) inside the browser viewport
        actions.move_to_element_with_offset(body, 0, 0).perform()

        steps = int(move_time * 60)  # ~60 FPS smooth motion
        if steps < 1:
            steps = 1

        # Create a random bezier-like path
        cp1 = (target_x * random.uniform(0.2, 0.5),
               target_y * random.uniform(0.2, 0.5))

        cp2 = (target_x * random.uniform(0.5, 0.9),
               target_y * random.uniform(0.5, 0.9))

        def bezier(t, p0, p1, p2, p3):
            return (
                (1 - t)**3 * p0
                + 3 * (1 - t)**2 * t * p1
                + 3 * (1 - t) * t**2 * p2
                + t**3 * p3
            )

        prev_x, prev_y = 0, 0

        for i in range(steps):
            t = i / steps

            x = bezier(t, 0, cp1[0], cp2[0], target_x)
            y = bezier(t, 0, cp1[1], cp2[1], target_y)

            # Add micro human jitter
            x += random.uniform(-1, 1)
            y += random.uniform(-1, 1)

            dx, dy = x - prev_x, y - prev_y

            actions.move_by_offset(dx, dy).perform()

            prev_x, prev_y = x, y

            # slight delay for realism
            time.sleep(random.uniform(0.005, 0.013))
    
    def click_absolute(driver, x, y):
        actions = ActionChains(driver)
        
        # Move to body (0,0) to reset pointer
        body = driver.find_element(By.TAG_NAME, "body")
        actions.move_to_element_with_offset(body, 0, 0)
        
        # Move to your target
        actions.move_by_offset(x, y).click().perform()
    
    def human_move(driver):
        """Fake human mouse movements to avoid HSProtect detection."""
        actions = ActionChains(driver)
        for _ in range(random.randint(3, 8)):
            x = random.randint(10, 800)
            y = random.randint(10, 800)
            try:
                actions.move_by_offset(x, y).perform()
            except:
                pass
            human_wait(0.1, 0.3)
    
    def find_in_iframes(driver, xpath):
        iframes = driver.find_elements(By.TAG_NAME, "iframe")
        print(f"FOUND {len(iframes)} IFRAMES")

        # First check main DOM
        try:
            return driver.find_element(By.XPATH, xpath)
        except:
            pass

        # Try each iframe
        for index, iframe in enumerate(iframes):
            try:
                print(f"Checking iframe {index}")
                driver.switch_to.frame(iframe)
                element = driver.find_element(By.XPATH, xpath)
                print(f"FOUND element in iframe {index}")
                return element
            except:
                driver.switch_to.default_content()
                continue

        raise Exception("Element not found in any iframe")
    
    def xpath_to_css(xpath: str) -> str:
        css = xpath.strip()
        css = css.replace("//", " ").replace("/", " > ")
        css = css.replace("[@id='", "#").replace("']", "")
        css = css.replace("[@class='", ".").replace("']", "")
        css = css.replace("[@name='", "[name='")
        return css.strip()

    def css_from_xpath(xpath):
        
        if is_xpath(path):
            return xpath_to_css(path)
        else:
            return path
        
    def is_xpath(selector: str) -> bool:
        if not isinstance(selector, str):
            return False
        selector = selector.strip()
        # Typical XPath patterns
        return selector.startswith("/") or selector.startswith("(") or re.match(r"^\.*//", selector)

    def human_wait(min_seconds=0.5, max_seconds=2):
        delay = random.uniform(min_seconds, max_seconds)
        time.sleep(delay)

    def start_driver(website_to_login, chrome_version, headless=False, use_proxy=False, websites=None, index_file=None, vpn_folder=None, temp_file=None, temp_file_name=None):
        try:
            os.system("taskkill /im chrome.exe /f >nul 2>&1")
        except:
            pass
        
        #Generate a random User-Agent
        user_agent = UserAgent().random
        
        #Load Extensions
        extension_path1 = os.path.abspath(r'C:\Users\dinis\OneDrive\Documentos\w\M\Extensions\Bye-Bye-Cookie-Banners-—-Cookie-Consent-Automator-Chrome-Web-Store') 
        extension_path2 = os.path.abspath(r'C:\Users\dinis\OneDrive\Documentos\w\M\Extensions\Adblock-Plus-free-ad-blocker-Chrome-Web-Store') 
        extension_path3 = os.path.abspath(r'C:\Users\dinis\OneDrive\Documentos\w\M\Extensions\NopeCHA') 
        #extension_path3 = os.path.abspath(r'C:\Users\dinis\OneDrive\Documentos\w\M\Extensions\hektCaptcha-hCaptchaSolver') 
        
        #Start Browser
        options = uc.ChromeOptions()
        if headless:
            options.add_argument('--headless')
        options.add_experimental_option('prefs', {'intl.accept_languages': 'en,en_US'})
        options.add_argument("--disable-background-timer-throttling")
        options.add_argument("--disable-backgrounding-occluded-windows")
        options.add_argument("--disable-infobars")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--disable-renderer-backgrounding")
        options.add_argument('--disable-features=DisableLoadExtensionCommandLineSwitch')
        load_argument = f'--load-extension={extension_path1},{extension_path2},{extension_path3}'
        options.add_argument(load_argument)
        options.page_load_strategy = 'none' 
        options.add_argument(f"user-agent={user_agent}")
        driver = uc.Chrome(options=options, version_main=chrome_version)
        driver.set_page_load_timeout(20)
        driver.maximize_window()

        #Close Extension Welcome Page
        while len(driver.window_handles) <= 1:
            pass
        while len(driver.window_handles) > 1:
            driver.switch_to.window(driver.window_handles[1])
            time.sleep(1)
            driver.close()
            time.sleep(1)
            driver.switch_to.window(driver.window_handles[0])
            time.sleep(1)
      
        if use_proxy:
            o = 0
            while o == 0:
                BotTools.connect_vpn(websites, index_file, vpn_folder, temp_file, temp_file_name)
                time.sleep(5)
                
                try:
                    driver.get(website_to_login)
                    o = 1
                except TimeoutException as e:
                    print("\n\n")
                    print(f"[Timeout] {e}")
                except WebDriverException as e:
                    print("\n\n")
                    print(f"[Connection Error] {e.msg}")
        else:
            o = 0
            while o == 0:
                try:
                    driver.get(website_to_login)
                    o = 1
                except TimeoutException as e:
                    print("\n\n")
                    print(f"[Timeout] {e}")
                except WebDriverException as e:
                    print("\n\n")
                    print(f"[Connection Error] {e.msg}")
        
        #Disable WebDriver flag
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

        #Execute Cloudflare's challenge script
        driver.execute_script("return navigator.language")
        
        return driver
        
    def start_driver_Edge(website_to_login, chrome_version, driver_path, headless=False, use_proxy=False, websites=None, index_file=None, vpn_folder=None, temp_file=None, temp_file_name=None):
        try:
            os.system("taskkill /IM msedge.exe /F")
            os.system("taskkill /IM msedgedriver.exe /F")
        except:
            pass
        
        #Generate a random User-Agent
        user_agent = UserAgent().random
        
        #Load Extensions
        #extension_path1 = os.path.abspath(r'C:\Users\dinis\OneDrive\Documentos\w\M\Extensions\Bye-Bye-Cookie-Banners-—-Cookie-Consent-Automator-Chrome-Web-Store') 
        #extension_path2 = os.path.abspath(r'C:\Users\dinis\OneDrive\Documentos\w\M\Extensions\Adblock-Plus-free-ad-blocker-Chrome-Web-Store') 
        
        #Driver Path
        #service = EdgeService(executable_path=driver_path)
        
        #Start Browser
        options = webdriver.EdgeOptions()
        if headless:
            options.add_argument('--headless')
        #options.add_experimental_option("excludeSwitches", ["enable-automation"])
        #options.add_experimental_option("useAutomationExtension", False)
        options.add_argument("--disable-background-timer-throttling")
        options.add_argument("--disable-backgrounding-occluded-windows")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-infobars")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--disable-renderer-backgrounding")
        options.add_argument('--disable-features=DisableLoadExtensionCommandLineSwitch')
        #load_argument = f'--load-extension={extension_path1},{extension_path2}'
        #options.add_argument(load_argument)
        options.page_load_strategy = 'none' 
        options.add_argument(f"user-agent={user_agent}")
        driver = webdriver.Edge(options = options)
        driver.set_page_load_timeout(20)
        driver.maximize_window()
      
        # driver.execute_cdp_cmd(
            # "Page.addScriptToEvaluateOnNewDocument",
            # {
                # "source": """
                    # Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
                # """
            # }
        # )
      
        if use_proxy:
            o = 0
            while o == 0:
                BotTools.connect_vpn(websites, index_file, vpn_folder, temp_file, temp_file_name)
                time.sleep(5)
                
                try:
                    driver.get(website_to_login)
                    o = 1
                except TimeoutException as e:
                    print("\n\n")
                    print(f"[Timeout] {e}")
                except WebDriverException as e:
                    print("\n\n")
                    print(f"[Connection Error] {e.msg}")
        else:
            o = 0
            while o == 0:
                try:
                    driver.get(website_to_login)
                    o = 1
                except TimeoutException as e:
                    print("\n\n")
                    print(f"[Timeout] {e}")
                except WebDriverException as e:
                    print("\n\n")
                    print(f"[Connection Error] {e.msg}")
        
        #Disable WebDriver flag
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

        #Execute Cloudflare's challenge script
        driver.execute_script("return navigator.language")
        
        return driver

    def start_driver_proxy(website_to_login, chrome_version, headless=False):
        try:
            os.system("taskkill /im chrome.exe /f >nul 2>&1")
        except:
            pass
        
        #Generate a random User-Agent
        user_agent = UserAgent().random
        
        #Proxy
        proxy = BotTools.proxy()
        
        #Start Browser
        options = uc.ChromeOptions()
        if headless:
            options.add_argument('--headless')
        options.add_argument("--disable-background-timer-throttling")
        options.add_argument("--disable-backgrounding-occluded-windows")
        options.add_argument("--disable-renderer-backgrounding")
        options.add_argument("--disable-logging")
        options.add_argument("--log-level=3")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--disable-popup-blocking")
        options.add_argument("--disable-extensions")
        options.add_argument("--start-maximized")
        options.add_argument(f"user-agent={user_agent}")
        options.add_argument(f"--proxy-server={proxy}")
        driver = uc.Chrome(options=options, version_main=chrome_version)
        driver.maximize_window()
       
        driver.get(website_to_login)
        
        #Disable WebDriver flag
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

        #Execute Cloudflare's challenge script
        driver.execute_script("return navigator.language")
        
        return driver

    def capcha_token(profile):
        options = webdriver.FirefoxOptions()
        #options.add_argument("-headless")
        profile = webdriver.FirefoxProfile(profile)
        options.profile = profile
        options.add_argument('--disable-blink-features=AutomationControlled')
        driver = webdriver.Firefox(options=options)
        driver.get("https://2captcha.com/cabinet")
        
        while True:
            try: #Remind Me Later
                WebDriverWait(driver, 2).until(expected_conditions.element_to_be_clickable((By.XPATH, "/html/body/div[4]/div/div/section/a"))).click()
            except:
                pass
            try: #Start Solve Button
                WebDriverWait(driver, 2).until(expected_conditions.element_to_be_clickable((By.XPATH, "/html/body/div/div[2]/main/div/div[1]/div/button"))).click()
            except:
                pass
            
            try: # rCaptcha
                solver = RecaptchaSolver(driver=driver)
                recaptcha_iframe = driver.find_element(By.XPATH, '//iframe[@title="reCAPTCHA"]')
                solver.click_recaptcha_v2(iframe=recaptcha_iframe)
                print("\nCAPTCHA: Captcha Solved")
            except:
                WebDriverWait(driver, 2).until(expected_conditions.element_to_be_clickable((By.XPATH, "/html/body/div[1]/div[2]/main/div/div[1]/div/form/button"))).click()
                print("\nFAIL: Captcha Failed")
        
    def create_account(driver, email_driver, website_to_login, website_loged_in, name_path=None, email_path=None, Pass_path=None, conf_pass_path=None, sign_button1_path=None, sign_button2_path=None):
        
        while driver.current_url != website_loged_in:
            
            email = BotTools.get_email(email_driver)
            name = generate_username(1)[0]
            
            #--------------------#
            #   Create Account   #
            #--------------------#

            try: #Signup Button
                WebDriverWait(driver, 2).until(expected_conditions.element_to_be_clickable((By.CSS_SELECTOR, sign_button1_path))).click()
                print("\nFILL: Signup Button Clicked")
            except:
                print("\nFAIL: Signup Button Clicked")
                
            try: #Name
                elem = WebDriverWait(driver, 3).until(expected_conditions.presence_of_element_located((By.CSS_SELECTOR, name_path)))
                elem.clear()
                elem.send_keys(name)
                print("\nCREATE ACCOUNT: Name Filled")
            except:
                print("\nFAIL: Name Filled")
                
            try: #Email
                elem = WebDriverWait(driver, 2).until(expected_conditions.presence_of_element_located((By.CSS_SELECTOR, email_path)))
                elem.clear()
                elem.send_keys(email)
                print("\nCREATE ACCOUNT: Email Filled")
            except:
                print("\nFAIL: Email Filled")
                
            try: #Password
                elem = WebDriverWait(driver, 2).until(expected_conditions.presence_of_element_located((By.CSS_SELECTOR, Pass_path)))
                elem.clear()
                elem.send_keys("A1ssssss!")
                print("\nCREATE ACCOUNT: Password Filled")
            except:
                print("\nFAIL: Password Filled")
            try: #Confirm Password
                elem = WebDriverWait(driver, 2).until(expected_conditions.presence_of_element_located((By.CSS_SELECTOR, conf_pass_path)))
                elem.clear()
                elem.send_keys("A1ssssss!")
                print("\nCREATE ACCOUNT: Confirm Password Filled")
            except:
                print("\nFAIL: Confirm Password Filled")

            #------------#
            #   Capcha   #
            #------------#
                
            try: #Select hCapcha
                driver.find_element(By.XPATH, '/html/body/div[2]/div/div[2]/div[1]/div/form/div[6]/div/div[1]/div/div/a[1]').click()
            except:
                pass
                
            #Wait For Nopcha to solve Capcha
            time.sleep(10)
                
            try: #Register Button                                                   
                element = WebDriverWait(driver, 2).until(expected_conditions.element_to_be_clickable((By.CSS_SELECTOR, sign_button2_path)))
                driver.execute_script("arguments[0].scrollIntoView();", element)
                element.click()
                print("\nCAPTCHA: Register Button Clicked")
            except:
                print("\nFAIL: Register Button Clicked")

    def registration_bonus(driver, claim_button, cookie_id=None, skip_intro=None, reward_menu=None, reward_btn=None, claim_button_2=None):
        print("\n\nREGISTRATION BONUS\n\n")
        
        i = 0
        end = 0
        while end == 0:
            i += 1
            print("\n\nREGISTRATION BONUS: " + str(i) + "\n\n")
            
            try: #Cookies
                element = WebDriverWait(driver, 2).until(expected_conditions.element_to_be_clickable((By.ID, cookie_id)))
                driver.execute_script("arguments[0].style.display='none';", element)
                print("\nINTRODOCTION: Cookies Window Hidden")
            except:
                print("\nFAIL: Cookies Window Hidden")
            
            try: #Skip Introduction
                WebDriverWait(driver, 2).until(expected_conditions.element_to_be_clickable((By.CSS_SELECTOR, skip_intro))).click()
                print("\nINTRODUCTION: Introduction Skiped")
            except:
                print("\nFAIL: Introduction Skiped")
                
            try: #Reward Menu Button
                WebDriverWait(driver, 2).until(expected_conditions.element_to_be_clickable((By.CSS_SELECTOR, reward_menu))).click()
                print("\nVERIFY: Reward Menu Button Clicked")
            except:
                print("\nFAIL: Reward Menu Button Clicked")
            
            try: #Claim Reward Button
                element = WebDriverWait(driver, 2).until(expected_conditions.presence_of_element_located((By.CSS_SELECTOR, claim_button_2)))
                time.sleep(0.1)
                driver.execute_script("arguments[0].scrollIntoView();", element)
                time.sleep(0.1)
                element.click()
                print("\nVERIFY: Continue Button Clicked")
            except:
                print("\nFAIL: Continue Button Clicked")
                driver.refresh()
                
            try: #Cookies
                element = WebDriverWait(driver, 2).until(expected_conditions.element_to_be_clickable((By.ID, cookie_id)))
                driver.execute_script("arguments[0].style.display='none';", element)
                print("\nINTRODOCTION: Cookies Window Hidden")
            except:
                print("\nFAIL: Cookies Window Hidden")
            
            try: #Captcha
                solver = RecaptchaSolver(driver=driver)
                recaptcha_iframe = driver.find_element(By.XPATH, '//iframe[@title="reCAPTCHA"]')
                solver.click_recaptcha_v2(iframe=recaptcha_iframe)
                print("\nVERIFY: Capcha Clicked")
            except:
                print("\nFAIL: Capcha Clicked")
              
            try: #Claim Reward Button
                element = WebDriverWait(driver, 2).until(expected_conditions.element_to_be_clickable((By.CSS_SELECTOR, claim_button)))
                driver.execute_script("arguments[0].click();", element)
                time.sleep(10)
                end = 1
                print("\nVERIFY: Claim Button Clicked")
            except:
                print("\nFAIL: Claim Button Clicked")
            
    #-------------#
    #   Youtube   #
    #-------------#

    def stackapi():
        #Retrieve The Text From Stack Overflow:
        SITE = StackAPI('stackoverflow')
        SITE.max_pages=1
        SITE.page_size=100
        
        #Create Anwsers
        time1 = random.randrange(1262304000, 1696118400)
        time2 = random.randrange(time1, 1696118400)
        question = SITE.fetch('questions', Key='4qArFpyh*TIw4)Man)R)7Q((', client_id=29098, fromdate=time1, todate=time2, max=1, pagesize=1, max_pages=1, sort='votes', filter='!9YdnSIN*P') #filter='quota_max'
        
        return question

    def text_to_video(text, t, clip_path, font_path, duration, font_size):
        
        clip = VideoFileClip(clip_path, audio=False).with_duration(duration)
        txt_clip = TextClip(font_path, text, size=(1920, 1080), text_align='center', font_size=font_size, method="caption")
        txt_clip = txt_clip.with_position('center').with_duration(duration)
        video = CompositeVideoClip([clip, txt_clip])
        
        #Calculate Timestamp
        t += duration

        a = [video, t]
        return a

    def txt_to_img(t, i, img_folder, font_path):
    
        im = Image.new("RGB", (1920, 1080), "#fff")
        box = ((0, 0, 1920, 1080))
        draw = ImageDraw.Draw(im)
        #draw.rectangle(box, outline="#000")

        text = t
        font_size = 100
        size = None
        while (size is None or size[0] > box[2] - box[0] or size[1] > box[3] - box[1]) and font_size > 0:
            font = ImageFont.truetype(font_path, font_size)
            #size = font.getsize_multiline(text)
            dummy_img = Image.new("RGB", (1, 1))
            draw = ImageDraw.Draw(dummy_img)
            bbox = draw.multiline_textbbox((0, 0), text, font=font)
            size = (bbox[2] - bbox[0], bbox[3] - bbox[1])
            font_size -= 1
        draw.multiline_text((box[0], box[1]), text, "#000", font)
        path = img_folder + str(i) + ".png"
        im.save(path)

    def trend_script():
        # GET TREND #
        pytrend = TrendReq(hl='en-US', tz=360)
        print(pytrend)
        trends = pytrend.trending_searches()

        rand1=random.Random()
        num = rand1.randint(0, len(trends[0]))

        print("\nTrend: " + trends[0][num])
        
        return trends[0][num]

    def decide_topic():
        #Decide Topic Randomly:
        topics = ["programming", "python", "web Development", "html", "Computers", "Viruses", "Hacking", "Gamming"]
        rand1=random.Random()
        num = rand1.randint(0, len(topics))
        topic = topics[num - 1]
        print("\nQuiz Topic: " + topic)
        
        return topic

    def upload_quiz(driver, question, a1, a2, a3, a4, n):
        #   UPLOAD   #
        driver.get("https://www.youtube.com/@TheKnowledgeBase69/community")
        sleep(5)
            
        #quiz:    
        driver.find_element(By.CSS_SELECTOR, "span.style-scope:nth-child(4) > ytd-button-renderer:nth-child(1) > yt-button-shape:nth-child(1) > button:nth-child(1)").click()
        print("\nQuiz Button Clicked")

        #Question:
        driver.find_element(By.ID, "contenteditable-root").send_keys(question)
        print("\nQuiz Question Written")

        #Add Anwsers:
        driver.find_element(By.CSS_SELECTOR, "#quiz-attachment > div.button-container.style-scope.ytd-backstage-quiz-editor-renderer > yt-button-renderer > yt-button-shape > button").click()
        driver.find_element(By.CSS_SELECTOR, "#quiz-attachment > div.button-container.style-scope.ytd-backstage-quiz-editor-renderer > yt-button-renderer > yt-button-shape > button").click()
        print("\nQuiz Add Answer Button CLicked Twice")

        #anwser 1:
        driver.find_element(By.XPATH, "/html/body/ytd-app/div[1]/ytd-page-manager/ytd-browse/ytd-two-column-browse-results-renderer/div[1]/ytd-section-list-renderer/div[2]/ytd-backstage-items/ytd-item-section-renderer/div[1]/ytd-comments-header-renderer/div[7]/ytd-backstage-post-dialog-renderer/div[2]/ytd-commentbox/div[2]/div/ytd-backstage-quiz-editor-renderer/div[1]/div[1]/div[1]/tp-yt-paper-input-container/div[2]/div/tp-yt-iron-autogrow-textarea/div[2]/textarea").send_keys(a1)
        print("\nQuiz Anwser 1 Written")

        #anwser 2:
        driver.find_element(By.XPATH, "/html/body/ytd-app/div[1]/ytd-page-manager/ytd-browse/ytd-two-column-browse-results-renderer/div[1]/ytd-section-list-renderer/div[2]/ytd-backstage-items/ytd-item-section-renderer/div[1]/ytd-comments-header-renderer/div[7]/ytd-backstage-post-dialog-renderer/div[2]/ytd-commentbox/div[2]/div/ytd-backstage-quiz-editor-renderer/div[1]/div[2]/div[1]/tp-yt-paper-input-container/div[2]/div/tp-yt-iron-autogrow-textarea/div[2]/textarea").send_keys(a2)
        print("\nQuiz Anwser 2 Written")

        #anwser 3:
        driver.find_element(By.XPATH, "/html/body/ytd-app/div[1]/ytd-page-manager/ytd-browse/ytd-two-column-browse-results-renderer/div[1]/ytd-section-list-renderer/div[2]/ytd-backstage-items/ytd-item-section-renderer/div[1]/ytd-comments-header-renderer/div[7]/ytd-backstage-post-dialog-renderer/div[2]/ytd-commentbox/div[2]/div/ytd-backstage-quiz-editor-renderer/div[1]/div[3]/div[1]/tp-yt-paper-input-container/div[2]/div/tp-yt-iron-autogrow-textarea/div[2]/textarea").send_keys(a3)
        print("\nQuiz Anwser 3 Written")

        #anwser 4:
        driver.find_element(By.XPATH, "/html/body/ytd-app/div[1]/ytd-page-manager/ytd-browse/ytd-two-column-browse-results-renderer/div[1]/ytd-section-list-renderer/div[2]/ytd-backstage-items/ytd-item-section-renderer/div[1]/ytd-comments-header-renderer/div[7]/ytd-backstage-post-dialog-renderer/div[2]/ytd-commentbox/div[2]/div/ytd-backstage-quiz-editor-renderer/div[1]/div[4]/div[1]/tp-yt-paper-input-container/div[2]/div/tp-yt-iron-autogrow-textarea/div[2]/textarea").send_keys(a4)
        print("\nQuiz Anwser 4 Written")

        #Select Correct Anwser:
        if n == 1:
            driver.find_element(By.CSS_SELECTOR, "div.quiz-option:nth-child(1) > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > yt-icon-button:nth-child(1) > button:nth-child(1)").click()
            print("\nQuiz Anwser 1 Selected as Real")
        elif n == 2:
            driver.find_element(By.CSS_SELECTOR, "div.quiz-option:nth-child(2) > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > yt-icon-button:nth-child(1) > button:nth-child(1)").click()
            print("\nQuiz Anwser 2 Selected as Real")
        elif n == 3:
            driver.find_element(By.CSS_SELECTOR, "div.quiz-option:nth-child(3) > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > yt-icon-button:nth-child(1) > button:nth-child(1)").click()
            print("\nQuiz Anwser 3 Selected as Real")
        elif n == 4:
            driver.find_element(By.CSS_SELECTOR, "div.quiz-option:nth-child(4) > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > yt-icon-button:nth-child(1) > button:nth-child(1)").click()
            print("\nQuiz Anwser 4 Selected as Real")
        
        print(9)
        
        #Publish:
        WebDriverWait(driver, 100).until(EC.element_to_be_clickable((By.XPATH, "//*[@id='submit-button']/yt-button-shape/button"))).click()
        print("\nQuiz Publish Button Clicked")
            
        sleep(5)
        print("\nQuiz Sucessfully Uploaded")
        
    def upload_img(driver, path):
        driver.get("https://www.youtube.com/@TheKnowledgeBase69/community")
        print("\nMeme Youtube Opened")
        try:
            #Image:
            WebDriverWait(driver, 100).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "span.ytd-backstage-post-dialog-renderer:nth-child(1) > ytd-button-renderer:nth-child(1) > yt-button-shape:nth-child(1) > button:nth-child(1)"))).click()
            print("\nMeme Image Button Clicked")
            
            sleep(1)
            
            #DRag'n'drop:
            elem = driver.find_element(By.XPATH, "/html/body/ytd-app/div[1]/ytd-page-manager/ytd-browse/ytd-two-column-browse-results-renderer/div[1]/ytd-section-list-renderer/div[2]/ytd-backstage-items/ytd-item-section-renderer/div[1]/ytd-comments-header-renderer/div[7]/ytd-backstage-post-dialog-renderer/div[2]/ytd-commentbox/div[2]/div/div[2]/tp-yt-paper-input-container/div[2]/div/div[3]/ytd-backstage-multi-image-select-renderer/div[1]/input")
            driver.execute_script("arguments[0].scrollIntoView();", elem)
            elem.send_keys(path)
            print("\nMeme Image Drag and Drop Successfull")
            
            sleep(1)

            #Publish:                                                                          
            WebDriverWait(driver, 100).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#submit-button > yt-button-shape:nth-child(1) > button:nth-child(1)"))).click()
            print("\nMeme Publish Button Clicked")
            
            sleep(5)
            print("\nMeme Uploaded Sucessfully")
        except:
            pass

    def create_video_trend(script, audio_path, video_clip_path, trend_video_path):
        #Text to Speech:
        language = 'en' 
        myobjAnwser = gTTS(text=script, lang=language, slow=False)
        myobjAnwser.save(audio_path)
        print("\nAudio Created")    
            
        clip = VideoFileClip(video_clip_path)
        audioclip = AudioFileClip(audio_path)
        duration = audioclip.duration
        videoclip = clip.subclipped(0, duration)

        new_audioclip = CompositeAudioClip([audioclip])
        videoclip.audio = new_audioclip
        videoclip.write_videofile(trend_video_path, threads=4, logger=None, ffmpeg_params=['-crf','18', '-aspect', '9:16'])

    def create_youtube_quiz(driver):
            topic = BotTools.decide_topic()

            text = BotTools.ai_chat("short quiz about " + topic + " with 3 fake anwsers and one real one. Include 1 question and 4 answers (for a total of FIVE senteces) seperated by the symbol |, have the question be first and the real anwser be second, include only the question and anwers and nothing else")
            
            print("\nText: " + text)
            words = text.split()
            t2 = text.split("|")
            print("\nQuiz: " + str(t2))
            
            # if text == "" or len(t2) > 5:
                # continue
            
            #Seperate Question and Anwsers:
            question = t2[0]
            real = t2[1]
            fake1 = t2[2]
            fake2 = t2[3]
            fake3 = t2[4]
            
            #Decide order of anwsers randomly
            a1 = ""
            a2 = ""
            a3 = ""
            a4 = ""
            rand=random.Random()
            n = rand.randint(1, 4)
            
            if n == 1:
                a1 = real
                a2 = fake1
                a3 = fake2
                a4 = fake3
                print("\nQuiz Order 1")
            if n == 2:
                a1 = fake1
                a2 = real
                a3 = fake2
                a4 = fake3
                print("\nQuiz Order 2")
            if n == 3:
                a1 = fake1
                a2 = fake2
                a3 = real
                a4 = fake3
                print("\nQuiz Order 2")
            if n == 4:
                a1 = fake1
                a2 = fake2
                a3 = fake3
                a4 = real
                print("\nQuiz Order 2")
            
            BotTools.upload_quiz(driver, question, a1, a2, a3, a4, n)

    def create_youtube_meme(driver, img_path):
            text = BotTools.ai_chat("Random short caption for a meme about Programming that you never told before, include only the caption and nothing else")
                
            # if text == "":
                # continue
                
            #Divide Caption to Fit Image
            i = 0
            t = ""
            words = text.split()
            for word in words:
                t += word + " "
                i += 1
                if i == 4:
                    i = 0
                    t += "\n"

            print("\nMeme Captcion: " + str(t))

            #Decide Wich Image to Use Randomy
            n = random.randrange(1,10)
            print("\nMeme Image " + str(n))
             
            #Delete Previous meme:
            try:
                os.remove(img_path) 
                print("\nMeme Deleted")
            except:
                print("\nMeme Delete Failed")
                pass
            
            # Open an Image
            path = img_path + ".jpg"
            print("\nMeme Image Opened")
             
            # Call draw Method to add 2D graphics in an image
            I1 = ImageDraw.Draw(img)

            # Add Text to an image
            font = ImageFont.truetype("impact.ttf", 125)
            I1.text((1500, 1500), t, (255, 255, 255), font, None, 5, "left")
            print("\nMeme Text Added")
             
            # Save the edited image
            img.save(img_path)
            print("\nMeme Saved")
            
            BotTools.upload_img(driver, img_path)

    def create_youtube_trend(driver):
            trend1 = BotTools.trend_script()

            script = BotTools.ai_chat(trend1)
            # if script == "":
                # print("\nScript Empty")
                # continue

            BotTools.create_video_trend(script)
            
            BotTools.upload_video(driver, trend1, script)
    
    def create_info_video(driver, video_path, img_folder, clip1_path, img, clip2_path, font_path, out_folder, out_video_path):    
        
        t = 0
        
        #Delete Previous Folder:
        if os.path.exists(video_path):
            shutil.rmtree(video_path) 
            print("\nVideo Deleted")
            
        #Retrieve The Text From Stack Overflow:
        s = 0
        while s == 0: 
            try:
                SITE = StackAPI('stackoverflow')
                s = 1
            except:
                pass
        SITE.max_pages=1
        SITE.page_size=100
        
        #Create Anwsers
        time1 = random.randrange(1262304000, 1696118400)
        time2 = random.randrange(time1, 1696118400)
        question = SITE.fetch('questions', Key='4qArFpyh*TIw4)Man)R)7Q((', client_id=29098, fromdate=time1, todate=time2, max=1, pagesize=1, max_pages=1, sort='votes', filter='!9YdnSIN*P')
        
        #Only proceed if the question has at least one anwser
        quest = []
        cont = 0
        for n in question['items']:
            quest = n
            if quest["is_answered"] == False:
                cont = 1
            
        if cont == 1:
            exit
            
        #Make Sure Title Isn't to long for youtube
        titleQuest = quest['title']
        titleQuest = titleQuest[0:100]
            
        #Get Question Text and anwsers
        question = quest['body']
        question_id = quest['question_id']
        top_answer = SITE.fetch('questions/' + str(question_id) + '/answers', order = 'desc', sort='votes', filter='withbody')
        
        #Format the Question Title:
        titleQuest2 = re.sub(r'\<a.+>', '', titleQuest)
        titleQuest2 = titleQuest2.replace('`', '"')
        question2 = re.sub(r'\<a.+>', '', question)
        question2 = question2.replace('`', '"')
        
        txt_clips = []
        
        # ADD QUESTION TITLE TO VIDEO #
        a = BotTools.text_to_video(titleQuest2, t, clip2_path, font_path, 2, 100)
        txt_clips.append(a[0])
        t = a[1]
        
        # ADD QUESTION TEXT TO VIDEO #
        a = BotTools.text_to_video(question, t, clip1_path, font_path, 30, 35)
        txt_clips.append(a[0])
        t = a[1]
         
        # ADD ANWSERS TO VIDEO #
            
        for r, an in zip(range(10), top_answer['items']):
            
            #Get Anwser Text
            AnwserText = an['body']
            
            #Format Answer Text
            AnwserText = re.sub(r'\<a.+>', '', AnwserText)
            AnwserText = AnwserText.replace('`', '"')
            anwserText1 = AnwserText
            
            #Create Anwser Title
            titleAnwser = "Anwser " + str(r + 1) + ": "

            # ADD ANSWER TITLE TO VIDEO #
            a = BotTools.text_to_video(titleAnwser, t, clip2_path, font_path, 2, 100)
            txt_clips.append(a[0])
            t = a[1]
            
            # ADD ANSWER TEXT TO VIDEO #
            a = BotTools.text_to_video(AnwserText, t, clip1_path, font_path, 30, 35)
            txt_clips.append(a[0])
            t = a[1]
         
        #Put all clips together
        final_video = concatenate_videoclips(txt_clips)
        final_video.write_videofile(out_video_path, fps=24)
            
        #Format Video Title
        titleQuest2 = titleQuest2.replace('&quot;', '"')
        titleQuest2 = titleQuest2.replace('&#vide39;', '"')

        #   UPLOAD   #
        BotTools.upload_video(driver, titleQuest2, out_video_path)

    def create_rot_short(driver, rot_video_path):
            
            k = 0
            script = BotTools.ai_chat("Random Interesting Reddid Post With around 120 words, include only the reddit post text nothing else inclunding quotation marks", k)
            title = BotTools.ai_chat("title for this script: " + script + ", include only the title nothing else", k)
            # if script == "":
                # continue
            
            print("\nTitle: " + title)
            print("\nScript: " + script)
            
            dur_final = 0
            clips, dur_final = BotTools.create_video_Text(script)
            print("\nFinal Duration: " + str(dur_final))
            
            vid = concatenate_videoclips(clips)
            
            vid.duration = dur_final
            vid.write_videofile(rot_video_path, threads=4, ffmpeg_params=['-crf','18', '-aspect', '9:16'])
            print("\nVideo Created")
            
            title = script[0:90]
            
            BotTools.upload_video(driver, title, script)

    def upload_video(driver, title, path):
        
        try:
            print("\nUPLOAD: Start")
            
            #Open Youtube Page
            driver.get("https://www.youtube.com/upload")
            print("\nUPLOAD: Entered Youtbe Page")
            
            #Upload Video
            time.sleep(5)
            driver.find_element(By.XPATH, "//input[@type='file']").send_keys(r"" + path + "")
            print("\nUPLOAD: Video Uploaded")
            
            time.sleep(2)

            #Add Title
            WebDriverWait(driver, 2).until(EC.element_to_be_clickable((By.ID, "textbox"))).clear()
            WebDriverWait(driver, 2).until(EC.element_to_be_clickable((By.ID, "textbox"))).send_keys(title)
            print("\nUPLOAD: Title Added")
        
            try: #Not Made For Kids Button
                driver.find_element(By.CSS_SELECTOR , "tp-yt-paper-radio-button.ytkc-made-for-kids-select:nth-child(2) > div:nth-child(1)").click()
                print("\nUPLOAD: Not Made for Kids Button Clicked")
                #driver.implicitly_wait(5)
            except:
                pass    
            
            #Next Button
            WebDriverWait(driver, 2).until(expected_conditions.element_to_be_clickable((By.XPATH, "//*[@id='next-button']/ytcp-button-shape/button"))).click()
            print("\nUPLOAD: Next Button Clicked 1")
            WebDriverWait(driver, 2).until(expected_conditions.element_to_be_clickable((By.XPATH, "//*[@id='next-button']/ytcp-button-shape/button"))).click()
            print("\nUPLOAD: Next Button Clicked 2")
            WebDriverWait(driver, 2).until(expected_conditions.element_to_be_clickable((By.XPATH, "//*[@id='next-button']/ytcp-button-shape/button"))).click()
            print("\nUPLOAD: Next Button Clicked 3")   
            time.sleep(5)
            
            try:
                WebDriverWait(driver, 2).until(expected_conditions.element_to_be_clickable((By.XPATH, "/html/body/ytcp-uploads-dialog/tp-yt-paper-dialog/div/ytcp-animatable[2]/div/div[2]/ytcp-button[3]/ytcp-button-shape/button"))).click()
            except:
                pass
            
            #Publish Button
            try:
                WebDriverWait(driver, 2).until(expected_conditions.element_to_be_clickable((By.XPATH, "//*[@id='next-button']/ytcp-button-shape/button"))).click()
                print("\nUPLOAD: Publish Button Clicked")
            except:
                pass
                
            #Wait for Video to load
            time.sleep(100)

            #Click Close Window Button
            WebDriverWait(driver, 2).until(expected_conditions.element_to_be_clickable((By.XPATH, "/html/body/ytcp-uploads-still-processing-dialog/ytcp-dialog/tp-yt-paper-dialog/div[3]/ytcp-button/ytcp-button-shape/button"))).click()
            print("\nUPLOAD: Close Window Button Clicked")
            time.sleep(3)
        except:
            pass