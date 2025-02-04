

import dotenv
from novelmaster.translatetool import TTP, TCrawl, TGpt, TLocal, TNotion


UNLOADED = 1
CRAWLED = 2
TRANSLATED = 3


class NovelMaster(TTP, TCrawl, TGpt, TLocal, TNotion):
    def __init__(
        self,
        novel_title: str,
        target_lang: str,
        is_Notion: bool = False
    ) -> None:
        """
        initialize NovelMaster.
        novel_title: title of the novel.
        target_lang: target language for translate.
        is_Notion: activate notion upload/download.
        **notion auth_key & main page id required**
        """
        
        self.init_TLocal(novel_title)
        if not self.isExist():
            self.newNovel()
        
        if is_Notion:
            self.init_TNotion()
        self.init_TGpt()
        self.loadInfo()
        self.target_lang = target_lang
    
    
    def init_TLocal(self, novel_title: str) -> None:
        """initialize TLocal.
        """
        
        TLocal.__init__(
            self,
            novel_title
        )
    
    
    def init_TGpt(self) -> None:
        """initialize TGpt.
        """
        
        TGpt.__init__(
            self,
            api_key = dotenv.dotenv_values(
                "novelmaster//.env"
            ).get("translate_gpt_api_key")
        )
    
    def init_TNotion(self) -> None:
        """initialize TNotion.
        """
        
        TNotion.__init__(
            self,
            dotenv.dotenv_values(
                "novelmaster//.env"
            ).get("translate_notion_auth"), 
            dotenv.dotenv_values(
                "novelmaster//.env"
            ).get("translate_notion_main_page_id")
        )
    
    def newNovel(self) -> None:
        """make new novel directory.
        """
        
        novel_id = input("novel_id : ")
        source_lang = input("source_lang(default = 'Japanese' : ")
        if source_lang == "":
            source_lang = "Japanese"
        
        self.info = {
            "novel_title": self.novel_title,
            "novel_id": novel_id, # <- ex) n7637dj
            "source_lang": source_lang, # <- ex) "Japanese"
            "episode_dict": {} # will be added with crawl process
        }
        self.clearGlossary()
        self.saveInfo()
    
    
    def clearGlossary(self) -> None:
        """make empty glossary.
        """
        
        self.info["glossary"] = {}
    
    
    def setGlossary(self) -> None:
        """append or correct source/target words in the glossary.
        """
        
        source_word = input("source_word : ")
        target_word = input("target_word : ")
        self.info["glossary"][source_word] = target_word
    
    
    def setEpisode(
        self,
        episode: str
    ) -> None:
        """set self.episode.
        """
        
        self.episode = episode
    
    
    def episodeList(self) -> list[str]:
        """return list of episodes.
        """
        
        return self.info["episode_dict"].keys()
    
    
    def getEpisodeStatus(self) -> str:
        """return episode status.
        """
        
        return self.info["episode_dict"][self.episode]["status"]
    
    
    def setEpisodeStatus(self, status: str) -> None:
        """set episode status.
        """
        
        self.info["episode_dict"][self.episode]["status"] = status
    
    
    def syosetuCrawlAll(
        self,
        first_episode: str|None = "1"
    ) -> None:
        """
        crawl all novel text from [syosetukani narou].
        you should use valid novel_id, or it won't work.
        """
        
        self.openBrowser()
        self.episode = first_episode
        while True:
            self.info["episode_dict"][self.episode] = {
                "status": UNLOADED,
            }
            next_episode = self.syosetuCrawl()
            if next_episode == "TimeoutException":
                print(f"{self.episode} : TimeoutException")
                break
            self.writeEpisode(
                self.info["source_lang"],
                self.episode
            )
            self.setEpisodeStatus(CRAWLED)
            print(f"{self.info['novel_id']} - {self.episode} : Crawled")
            self.saveInfo()
            
            if not next_episode:
                print(f"{self.info['novel_id']} - {self.episode} : End")
                break
            self.setEpisode(next_episode)
        
        self.closeBrowser()
    
    
    def translateEpisode(
        self,
        method: str|None = "chat"
    ) -> None:
        """translate episode with the method : "chat" / "batch".
        """
        
        METHOD_MAP = {
            "chat": self.translate_byChat,
            "batch": self.translate_byBatch
        }
        self.readEpisode(self.info["source_lang"])
        if self.info["source_lang"] == "Japanese":
            self.preprocess_japanese()
        func = METHOD_MAP[method]
        translate_response = func(
            self.info["source_lang"],
            self.target_lang,
            self.episode_text
        )
        self.setText(translate_response.translation)
        self.writeEpisode(self.target_lang)
        for wordset in translate_response.proper_noun_dict:
            if not wordset.proper_noun in self.info["glossary"].keys():
                self.info["glossary"][wordset.proper_noun] = wordset.translated_proper_noun
        self.init_TGpt()
    
    
    def translateNovel(
        self,
        method: str|None = "chat",
        work_limit: int|None = None
   ) -> None:
        """translate with work limit, or translate all.
        """
        
        work_count = 0
        for episode in self.episodeList():
            if work_count == work_limit:
                break
            self.setEpisode(episode)
            
            if self.getEpisodeStatus() == CRAWLED:
                self.translateEpisode(method = method)
                self.setEpisodeStatus(TRANSLATED)
                print(f"{self.novel_title} - {self.episode} : Translated")
                work_count += 1
        
        self.saveInfo()
    
    
    def isCompleted(self) -> bool:
        """check whether whole translation is completed.
        """
        
        for episode in self.episodeList():
            if self.getEpisodeStatus() < TRANSLATED:
                return False
        return True
    
    
    def notion_novelUpload(self) -> None:
        """upload novel to notion page.
        """
        
        if not self.isCompleted():
            return
        for episode in self.episodeList():
            self.episodeUpload(
                self.novel_title,
                self.info["source_lang"],
                episode
            )
            self.episodeUpload(
                self.novel_title,
                self.target_lang,
                episode
            )
    
    
