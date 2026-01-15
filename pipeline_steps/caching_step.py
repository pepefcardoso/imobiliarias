import os
import hashlib
from typing import Any
from interfaces.i_pipeline_step import IPipelineStep
from interfaces.i_http_client import IHttpClient

class CachingFetchStep(IPipelineStep):
    """
    Substituto do FetchStep que verifica o disco antes de ir à internet.
    """
    def __init__(self, client: IHttpClient, cache_dir: str, wait_selector: str = None):
        self.client = client
        self.cache_dir = cache_dir
        self.wait_selector = wait_selector
        
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)

    def process(self, url: str) -> str:
        file_hash = hashlib.md5(url.encode('utf-8')).hexdigest()
        file_path = os.path.join(self.cache_dir, f"{file_hash}.html")

        if os.path.exists(file_path):
            print(f"📦 [Cache Hit] Lendo arquivo local: {file_hash}.html")
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()

        print(f"🌐 [Web Fetch] Baixando URL...")
        html_content = self.client.fetch(url, wait_selector=self.wait_selector)

        if html_content:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(html_content)
        
        return html_content