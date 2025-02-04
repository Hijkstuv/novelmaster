

import re


class Translate_TextProcesser():
    """class for pre/postprocessing text.
    """
    def getText(self) -> str:
        return self.episode_text
    
    def setText(self, text: str) -> None:
        self.episode_text = text
    
    
    def addEndmark(self) -> None:
        """add japanese end mark, if there's no mark at the end of speech lines.
        """
        
        self.episode_text = re.sub(
            r'([^。？！])?(」+)', r'\1。\2',
            self.episode_text
        )
    
    def replaceChar(self) -> None:
        """replace japanese characters.
        """
        
        self.episode_text = re.sub(r'[「」]', '\"', self.episode_text)
        self.episode_text = self.episode_text.replace('『', '[')
        self.episode_text = self.episode_text.replace('』', ']')
        self.episode_text = self.episode_text.replace('　', ' ')
    
    def preprocess_japanese(self) -> None:
        """preprocess of japanese characters.
        """
        
        self.addEndmark()
        self.replaceChar()
    
    
    