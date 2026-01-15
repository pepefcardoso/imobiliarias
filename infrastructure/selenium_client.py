from typing import Optional
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from interfaces.i_http_client import IHttpClient

class SeleniumClient(IHttpClient):
    def __init__(self, headless: bool = True):
        self.headless = headless
        self._driver = None

    def _configurar_opcoes(self) -> Options:
        options = Options()
        if self.headless:
            options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36")
        return options

    def _get_driver(self):
        """Retorna a instância ativa do driver ou cria uma nova."""
        if self._driver is None:
            service = Service(ChromeDriverManager().install())
            self._driver = webdriver.Chrome(service=service, options=self._configurar_opcoes())
        return self._driver

    def close(self):
        """Fecha o driver manualmente se necessário."""
        if self._driver:
            try:
                self._driver.quit()
            except Exception:
                pass
            finally:
                self._driver = None

    def fetch(self, url: str, wait_selector: Optional[str] = None) -> str:
        try:
            driver = self._get_driver()
            driver.get(url)
            
            wait = WebDriverWait(driver, 20)
            
            if wait_selector:
                wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, wait_selector)))
            else:
                wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            
            return driver.page_source
            
        except Exception as e:
            print(f"Erro no SeleniumClient: {e}")
            self.close()
            return ""

    def __del__(self):
        """Garante que o navegador é fechado ao destruir o objeto."""
        self.close()