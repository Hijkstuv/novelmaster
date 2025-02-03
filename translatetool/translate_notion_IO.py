

from novelmaster.translatetool.notion_IO import Notion_IO, BOOK


class Translate_Notion_IO(Notion_IO):
    """class for Notion upload/download, especially for translate project.
    """
    def __init__(
        self,
        notion_token: str,
        notion_main_page_id: str
    ) -> str:
        """initialize with given token and main_page_id.
        """
        Notion_IO.__init__(
            self,
            notion_token,
            notion_main_page_id
        )
    
    
    def searchNovelPage(self) -> str:
        """search page of novel.
        """
        novel_page_id = self.searchPage(
            self.main_page_id,
            self.novel_title
        )
        return novel_page_id
    
    
    def searchLangPage(
        self,
        lang: str
    ) -> str|None:
        """search page of novel//lang.
        """
        
        novel_page_id = self.searchNovelPage()
        if not novel_page_id:
            return None
        lang_page_id = self.searchPage(
            novel_page_id,
            lang
        )
        return lang_page_id
    
    
    def searchEpisodePage(
        self,
        lang: str,
        episode: str|None = None
    ) -> str:
        """search page of novel//lang//episode.
        """
        
        if not episode:
            episode = self.episode
        lang_page_id = self.searchLangPage(lang)
        if not lang_page_id:
            return
        episode_page_id = self.searchPage(
            lang_page_id,
            episode
        )
        return episode_page_id
    
    
    def createNovelPage(self) -> str:
        """create novel page and novel//lang
        """
        
        novel_page_id = self.createNewChildPage(
            self.main_page_id,
            self.novel_title,
            BOOK
        )
        self.createNewChildPage(
            novel_page_id,
            self.info["source_lang"],
            BOOK
        )
        self.createNewChildPage(
            novel_page_id,
            self.target_lang,
            BOOK
        )
        return novel_page_id
    
    
    def createEpisodePage(
        self,
        lang: str,
        episode: str|None = None
    ) -> str:
        """create novel//lang//episode page
        """
        
        lang_page_id = self.searchLangPage(
            self.novel_title,
            lang
        )
        episode_page_id = self.createNewChildPage(
            lang_page_id,
            episode,
            BOOK
        )
        return episode_page_id
    
    
    def uploadEpisode(
        self,
        lang: str,
        episode: str|None = None
    ) -> None:
        """
        upload episode text to episode page.
        caution: it does not rewrite, just write after current blocks.
        """
        
        if not episode:
            episode = self.episode
        episode_page_id = self.createEpisodePage()
        self.writeText(
            episode_page_id,
            self.episode_text)
        print(
            self.novel_title + " - episode " + episode 
            + "(" + lang + ") : Notion_uploaded"
        )
    
    
    def downloadEpisode(
        self,
        lang: str,
        episode: str|None = None
    ) -> None:
        """download episode text from episode page.
        """
        
        if not episode:
            episode = self.episode
        episode_page_id = self.searchEpisodePage(
            lang,
            episode
        )
        if episode_page_id:
            self.episode_text = self.readText(episode_page_id)
    
    
#%%

'''
notion_client.blocks.children.list()
-> results -> paragraph -> rich_text -> {type:mention} 
-> plain_text / mention -> page -> id

response(retrieve) -> id

novel_title -> lang -> episode
'''
