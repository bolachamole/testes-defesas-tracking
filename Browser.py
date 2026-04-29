from bd import BancoDeDados
from selenium.webdriver.chrome.webdriver import WebDriver as ChromeDriver
from selenium.webdriver.firefox.webdriver import WebDriver as FirefoxDriver
from selenium.webdriver.edge.webdriver import WebDriver as EdgeDriver
from selenium.webdriver.safari.webdriver import WebDriver as SafariDriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.safari.options import Options as SafariOptions

class Browser:
    def __init__(self, nav, nivel, profile=None, path=None):
        self.storage = BancoDeDados(nav, nivel)
        if (nav == "firefox"):
            options = FirefoxOptions()
            if (profile):
                options.add_argument("-profile")
                options.add_argument(profile)
            options.set_preference("network.proxy.http", "127.0.0.1")
            options.set_preference("network.proxy.http_port", 8080)
            options.set_preference("network.proxy.share_proxy_settings", True)
            options.set_preference("network.proxy.ssl", "127.0.0.1")
            options.set_preference("network.proxy.ssl_port", 8080)
            options.set_preference("network.proxy.type", 1)
            self.driver = FirefoxDriver(options=options)
        elif (nav == "edge"):
            options = EdgeOptions()
            if (profile):
                options.add_argument(f"--user-data-dir={profile}")
                options.add_argument("--profile-directory=Profile 1")
            options.add_argument("--start-maximized")
            options.add_argument("--proxy-server=http://localhost:8080")
            self.driver = EdgeDriver(options=options)
        elif (nav == "safari"):
            options = SafariOptions()
            self.driver = SafariDriver(options=options)
        else:
            options = ChromeOptions()
            if (path):
                options.binary_location = path
            if (profile):
                options.add_argument(f"--user-data-dir={profile}")
                options.add_argument("--profile-directory=Profile 1")
            options.add_argument("--start-maximized")
            options.add_argument("--proxy-server=http://localhost:8080")
            self.driver = ChromeDriver(options=options)

    def get(self, site):
        try:
            self.driver.get(site)
        except:
            self.driver.get(site)

    def quit(self):
        try:
            self.driver.quit()
        except:
            self.driver.quit()
