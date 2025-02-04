

import os
from novelmaster.translatetool.local_IO import Local_IO

class Translate_Local_IO(Local_IO):
    def __init__(
            self,
            novel_title: str,
            base_dir: str|None = "C:\\task\\translate"
        ) -> None:
        self.novel_title = novel_title
        self.base_dir = base_dir
    
    def isExist(self) -> bool:
        """return novel existance.
        """
        return os.path.exists(
            os.path.join(
                self.base_dir,
                self.novel_title
            )
        )
    
    
    def readEpisode(
        self,
        lang: str,
        episode: str|None = None
    ) -> None:
        """read episode txt from local.
        """
        
        if not episode:
            episode = self.episode
        
        file_path = os.path.join(
            self.base_dir,
            self.novel_title,
            lang,
            episode + ".txt"
        )
        self.episode_text = self.readTXT(file_path)
    
    
    def writeEpisode(
        self,
        lang: str,
        episode: str|None = None,
    ) -> None:
        """write episode txt to local.
        """
        
        if not episode:
            episode = self.episode
            
        file_path = os.path.join(
            self.base_dir,
            self.novel_title,
            lang,
            episode + ".txt"
        )
        self.writeTXT(file_path, self.episode_text)
    
    
    def loadInfo(self) -> None:
        """load info json from local.
        """
        
        file_path = os.path.join(
            self.base_dir,
            self.novel_title,
            "info.json"
        )
        self.info = self.readJSON(file_path)
    
    
    def saveInfo(self) -> None:
        """save info json to local.
        """
        
        file_path = os.path.join(
            self.base_dir,
            self.novel_title,
            "info.json"
        )
        self.writeJSON(file_path, self.info)
    
    