

import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

SYOSETU_URL = "https://ncode.syosetu.com/"


def get_episode_str(url: str) -> str | None:
    parts = url.rstrip("/").split("/")
    return parts[-1] if parts[-1].isdigit() else None


def postprocess_html(html: str) -> str|None:
    """postprocess about ruby tags and etc."""
    
    pattern = re.compile(
        r'<div\s+class="js-novel-text\s+p-novel__text".*?</div>',
        re.DOTALL
    )
    match = pattern.search(html)
    if match:
        text_cleaned_html = match.group(0)
    else:
        return None
    ruby_cleaned_html = re.sub(
        r'<ruby>(.*?)<rp>.*?</rp><rt>(.*?)</rt>(.*?)</ruby>',
        r'\1(\2)\3',
        text_cleaned_html
    )
    tag_cleaned_html = re.sub(r'<.*?>', '', ruby_cleaned_html)

    return tag_cleaned_html


class Translate_Crawl_IO():
    def __init__(self):
        return
    
    def openBrowser(self):
        self.browser = webdriver.Chrome()
    
    def closeBrowser(self):
        self.browser.close()
    
    
    def syosetuCrawl(
        self,
        novel_id: str|None = None,
        episode: str|None = None
    ) -> str|None:
        """
        crawl novel text from [syosetukani narou], with novel_id and episode str.
        return next_episode; or None when there is no next episode.
        """
        
        if not novel_id:
            novel_id = self.info["novel_id"]
        if not episode:
            episode = self.episode
        
        self.browser.get(SYOSETU_URL + novel_id + "/" + episode)
        try:
            WebDriverWait(self.browser, 180).until(
                EC.presence_of_element_located((By.CLASS_NAME, "p-novel__body"))
            )
        except Exception:
            print(f"{novel_id} - {episode} : timeout")
            return "TimeoutException"
        print(f"{novel_id} - {episode} : loaded")
        
        novel_subTitle_1 = self.browser.find_elements(
            By.TAG_NAME,
            "span"
        )[5].text.strip()
        novel_subTitle_2 = self.browser.find_element(
            By.TAG_NAME,
            "h1"
        ).text.strip()
    
        novel_body_element = self.browser.find_element(
            By.CLASS_NAME,
            "p-novel__body"
        )
        
        novel_body = novel_body_element.get_attribute("innerHTML")
        novel_body = postprocess_html(novel_body)
        
        episode_text = f"{novel_subTitle_1}\n{novel_subTitle_2}{novel_body}"
        
        self.episode_text = episode_text
        
        try:
            next_link = self.browser.find_element(
                By.XPATH,
                '//a[contains(text(), "次へ")]'
            ).get_attribute("href")
            next_episode = get_episode_str(next_link)
            return next_episode
        except Exception:
            return None
    
    